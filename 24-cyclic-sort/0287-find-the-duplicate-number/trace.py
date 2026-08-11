"""Rich full-arc trace for Find the Duplicate Number, mirroring the two functions
in solution.py. The array is read as jumps (index i -> nums[i]); two indices
sharing a value create a cycle whose entrance is the duplicate. Shows the O(n^2)
brute pair-scan, the constraint that rules out sign-flipping, then Floyd's slow/
fast pointers hopping across indices. Writes trace.json.
"""
import json
import os

nums = [1, 3, 4, 2, 2]  # duplicate is 2
frames = []

BRUTE = [
    "for i in range(n):",
    "    for j in range(i+1, n):",
    "        if nums[i] == nums[j]:",
    "            return nums[i]",
]
FAST = [
    "slow = fast = nums[0]",
    "while True:                 # phase 1: find a meeting point",
    "    slow = nums[slow]",
    "    fast = nums[nums[fast]]",
    "    if slow == fast: break",
    "slow = nums[0]              # phase 2: find the entrance",
    "while slow != fast:",
    "    slow = nums[slow]",
    "    fast = nums[fast]",
    "return slow",
]


def add(**f):
    frames.append(f)


# ---- Act 0: brute force, compare every pair ----
n = len(nums)
work = 0
add(act=0, cells=nums, code="brute", line=0,
    intro="every i re-compares against the whole tail — the same pairs, over and over.",
    invariant="every pair before (i, j) has been compared and differed.",
    note="Brute force: compare every pair; the first equal pair is the duplicate. "
         "O(n^2) time.",
    pointers={"i": 0, "j": 1}, marks={"0": "active", "1": "dim"},
    state=[["i", 0], ["j", 1], ["comparisons", 0]])
found = None
for i in range(n):
    for j in range(i + 1, n):
        work += 1
        hit = nums[i] == nums[j]
        add(act=0, code="brute", line=2,
            note=f"nums[{i}]={nums[i]} vs nums[{j}]={nums[j]}. "
                 + ("Equal — duplicate found." if hit else "Different."),
            pointers={"i": i, "j": j}, arc=[i, j],
            marks={str(i): "active", str(j): "good" if hit else "dim"},
            state=[["i", i], ["j", j], ["comparisons", work]])
        if hit:
            found = nums[i]
            break
    if found is not None:
        break
add(act=0, code="brute", line=3,
    note=f"Duplicate is {found}, but it took {work} comparisons — about n^2/2, and it "
         "gives us no O(1)-space, no-mutation guarantee.",
    marks={"3": "good", "4": "good"},
    state=[["answer", found], ["comparisons", work]])

# ---- Act 1: the two constraints rule out the easy tricks ----
add(act=1,
    intro="no extra memory AND no mutation — that pair is what forces Floyd.",
    note="A set would find it in O(n) but uses O(n) memory. Sign-flipping (like #442) "
         "is O(1) memory but MUTATES the array. #287 forbids both.",
    marks={str(k): "dim" for k in range(n)},
    state=[["set", "O(n) memory ✗"], ["sign-flip", "mutates array ✗"],
           ["need", "O(1) space, read-only"]])
add(act=1,
    intro="read index i as an arrow to nums[i]; a repeated value = two arrows into one node.",
    note="Read the array as jumps: from index i, go to index nums[i]. Two indices hold "
         "the duplicate, so two arrows land on the same node — the path must loop, and "
         "the loop's entrance IS the duplicate.",
    cells=nums,
    marks={"0": "dim", "1": "dim", "2": "dim", "3": "good", "4": "good"},
    state=[["index 3 → nums[3]", "2"], ["index 4 → nums[4]", "2"],
           ["shared target", "index 2 = a cycle"]])

# ---- Act 2: Floyd's tortoise and hare ----
def jump_marks(slow, fast):
    m = {str(k): "dim" for k in range(n)}
    m[str(slow)] = "active"
    m[str(fast)] = "bad" if fast != slow else "good"
    return m


add(act=2, cells=nums, code="fast", line=0,
    intro="slow hops one arrow, fast hops two; inside the loop they must collide.",
    invariant="both pointers are following the same jump function from index 0.",
    note="Phase 1: slow = nums[slow] (one jump), fast = nums[nums[fast]] (two jumps). "
         "They start together, then chase around the loop.",
    pointers={"slow": nums[0], "fast": nums[0]},
    marks=jump_marks(nums[0], nums[0]),
    state=[["slow at", nums[0]], ["fast at", nums[0]], ["phase", 1]])

slow = nums[0]
fast = nums[0]
hops = 0
while True:
    hops += 1
    slow = nums[slow]
    fast = nums[nums[fast]]
    met = slow == fast
    add(act=2, code="fast", line=3,
        note=f"slow jumps once → index {slow}. fast jumps twice → index {fast}. "
             + ("They meet! A point inside the cycle." if met else "Not yet."),
        pointers={"slow": slow, "fast": fast},
        marks=jump_marks(slow, fast),
        state=[["slow at", slow], ["fast at", fast], ["hops", hops], ["met?", "yes" if met else "no"]])
    if met:
        break

add(act=2, code="fast", line=5,
    intro="reset slow to the start; now both step ONE at a time — they meet at the entrance.",
    invariant="the distance math guarantees they collide exactly at the cycle entrance.",
    note=f"Phase 2: leave fast at the meeting point (index {fast}); reset slow to "
         f"nums[0] = {nums[0]}. Now both step one jump at a time.",
    pointers={"slow": nums[0], "fast": fast},
    marks=jump_marks(nums[0], fast),
    state=[["slow reset to", nums[0]], ["fast at", fast], ["phase", 2]])

slow = nums[0]
while slow != fast:
    slow = nums[slow]
    fast = nums[fast]
    met = slow == fast
    add(act=2, code="fast", line=7,
        note=f"slow → index {slow}, fast → index {fast}. "
             + ("They meet — this index is the cycle entrance." if met else "Keep stepping."),
        pointers={"slow": slow, "fast": fast},
        marks=jump_marks(slow, fast),
        state=[["slow at", slow], ["fast at", fast], ["met?", "yes" if met else "no"]])
add(act=2, code="fast", line=9,
    note=f"Entrance index = {slow}, and that value is the duplicate: {slow}. O(1) space, "
         "array never touched.",
    pointers={"slow": slow, "fast": fast},
    marks={str(slow): "good", **{str(k): "dim" for k in range(n) if k != slow}},
    state=[["answer", slow], ["extra memory", "O(1)"], ["array modified?", "no"]],
    banner=f"Duplicate = {slow}   — O(1) space, read-only (brute took {work} compares)")

# ---- Act 3: edge case — smallest array [1, 1] ----
edge = [1, 1]
add(act=3, cells=edge, code="fast", line=0,
    intro="the tiniest cycle: index 1 points to itself, and that's the duplicate.",
    invariant="two positions holding 1 both jump to index 1 — an immediate loop.",
    note="Edge case: [1, 1], n = 1. Both index 0 and index 1 jump to index 1, so the "
         "loop entrance is index 1 → duplicate 1.",
    pointers={"slow": edge[0], "fast": edge[0]},
    marks={"0": "dim", "1": "active"},
    state=[["slow at", edge[0]], ["fast at", edge[0]], ["phase", 1]])
es = edge[0]
ef = edge[0]
# phase 1
es = edge[es]
ef = edge[edge[ef]]
add(act=3, code="fast", line=3,
    note=f"slow → index {es}, fast → index {ef}. Already equal — meeting point is index {es}.",
    pointers={"slow": es, "fast": ef},
    marks={str(es): "good", str(1 - es): "dim"},
    state=[["slow at", es], ["fast at", ef], ["met?", "yes"]])
es = edge[0]
add(act=3, code="fast", line=5,
    note=f"Phase 2: reset slow to nums[0] = {edge[0]}. slow == fast already at index {ef}.",
    pointers={"slow": es, "fast": ef},
    marks={str(ef): "good", str(1 - ef): "dim"},
    state=[["slow at", es], ["fast at", ef]])
add(act=3, code="fast", line=9,
    note=f"Entrance index = {ef}, duplicate value = {ef}. The smallest case works too.",
    pointers={"slow": ef, "fast": ef},
    marks={str(ef): "good", str(1 - ef): "dim"},
    state=[["answer", ef], ["extra memory", "O(1)"]],
    banner="Smallest case [1, 1] → duplicate = 1")

trace = {
    "player": "linear",
    "title": "Find the Duplicate — a cycle in the jumps, found read-only",
    "acts": ["Brute: every pair", "The constraints", "Floyd's tortoise & hare",
             "Edge case: [1, 1]"],
    "code": {"brute": BRUTE, "fast": FAST},
    "legend": [["active", "slow pointer"], ["bad", "fast pointer"],
               ["good", "meeting point / the duplicate"], ["dim", "other indices"]],
    "cells": nums, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
