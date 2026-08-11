"""Rich full-arc trace for First Missing Positive, mirroring the two functions in
solution.py. Shows the O(n)-extra-space set baseline, then cyclic sort: each
value swaps toward its home index v-1 until the first empty seat shows the gap.
Writes trace.json.
"""
import json
import os

nums = [3, 4, -1, 1]  # answer: 2 is missing
frames = []

SET = [
    "present = set(nums)",
    "candidate = 1",
    "while candidate in present:",
    "    candidate += 1",
    "return candidate",
]
FAST = [
    "for i in range(n):",
    "    while 1 <= nums[i] <= n and nums[nums[i]-1] != nums[i]:",
    "        correct = nums[i] - 1",
    "        nums[i], nums[correct] = nums[correct], nums[i]",
    "for i in range(n):",
    "    if nums[i] != i + 1:",
    "        return i + 1",
    "return n + 1",
]


def add(**f):
    frames.append(f)


def sidebar(present):
    return {"title": "present (set)", "rows": [[str(v), "✓"] for v in sorted(present)]}


# ---- Act 0: the set baseline (costs O(n) extra memory) ----
n = len(nums)
present = set(nums)
add(act=0, cells=nums, code="set", line=0,
    intro="the set is the whole cost: O(n) extra memory the problem forbids.",
    invariant="present holds exactly the values already read from nums.",
    note="Baseline: dump every value into a set, then count up 1, 2, 3... until one "
         "is missing. Correct, but the set is extra memory.",
    marks={str(k): "dim" for k in range(n)}, sidebar=sidebar(present),
    state=[["set size", len(present)], ["extra memory", "O(n)"]])
cand = 1
while cand in present:
    add(act=0, code="set", line=3,
        note=f"Is {cand} in the set? Yes — keep counting up.",
        marks={str(k): "dim" for k in range(n)}, sidebar=sidebar(present),
        state=[["candidate", cand], ["in set?", "yes"]])
    cand += 1
add(act=0, code="set", line=4,
    note=f"Is {cand} in the set? No — {cand} is the first missing positive. But we "
         "paid O(n) extra memory to learn it.",
    marks={str(k): "dim" for k in range(n)}, sidebar=sidebar(present),
    state=[["candidate", cand], ["in set?", "no"], ["answer", cand], ["extra memory", "O(n)"]])

# ---- Act 1: the idea — the array is its own hash table ----
add(act=1,
    intro="value v has a home: index v-1. Put each home in place, then find the gap.",
    note="With n slots the answer is in 1..n+1. So value v belongs at index v-1 — "
         "the array's own indices ARE the hash table. No extra memory needed.",
    cells=[1, 2, 3, 4], labels=[0, 1, 2, 3],
    marks={"0": "good", "1": "good", "2": "good", "3": "good"},
    state=[["value 1", "home index 0"], ["value 2", "home index 1"],
           ["value v", "home index v-1"]])
add(act=1,
    note="Out-of-range values (<=0 or >n) have no home here — ignore them. Everything "
         "in 1..n we swap into its seat, then scan for the first wrong seat.",
    cells=nums, labels=[0, 1, 2, 3],
    marks={"0": "dim", "1": "dim", "2": "bad", "3": "dim"},
    state=[["-1", "out of range → ignore"], ["swap the rest", "toward home"]])

# ---- Act 2: cyclic sort, real swaps toward home ----
arr = list(nums)
swaps = 0


def home_marks(i, active_home=None):
    m = {}
    for k in range(n):
        v = arr[k]
        if 1 <= v <= n and v - 1 == k:
            m[str(k)] = "good"          # value sitting in its home seat
        elif not (1 <= v <= n):
            m[str(k)] = "bad"           # out of range, no home
        else:
            m[str(k)] = "dim"
    m[str(i)] = "active"
    if active_home is not None:
        m[str(active_home)] = "active"
    return m


add(act=2, cells=arr, labels=list(range(n)), code="fast", line=0,
    intro="a swap only lands when it puts a value in its home — so it can't loop forever.",
    invariant="everything left of i that had a home is already sitting in it.",
    note="Pass 1: for each i, keep swapping nums[i] to its home index nums[i]-1 until "
         "index i holds something with no home or already home.",
    pointers={"i": 0}, marks=home_marks(0),
    state=[["i", 0], ["n", n], ["swaps", 0]])

for i in range(n):
    add(act=2, code="fast", line=1,
        note=f"i = {i}. nums[i] = {arr[i]}. "
             + (f"In range and not home yet — swap it toward index {arr[i]-1}."
                if (1 <= arr[i] <= n and arr[arr[i]-1] != arr[i])
                else "No swap: out of range or already home."),
        pointers={"i": i}, marks=home_marks(i),
        state=[["i", i], ["nums[i]", arr[i]], ["swaps", swaps]])
    while 1 <= arr[i] <= n and arr[arr[i] - 1] != arr[i]:
        correct = arr[i] - 1
        moved = arr[i]
        add(act=2, code="fast", line=3,
            note=f"Send {moved} home to index {correct}: swap nums[{i}] and nums[{correct}].",
            pointers={"i": i}, arc=[i, correct],
            marks=home_marks(i, active_home=correct),
            state=[["i", i], ["value", moved], ["→ home index", correct], ["swaps", swaps + 1]])
        arr[i], arr[correct] = arr[correct], arr[i]
        swaps += 1
        add(act=2, code="fast", line=3,
            note=f"{moved} is now home at index {correct}. Index {i} now holds {arr[i]} — "
                 "check it again.",
            pointers={"i": i},
            marks=home_marks(i),
            state=[["i", i], ["nums[i]", arr[i]], ["swaps", swaps]])

add(act=2, code="fast", line=4,
    note="Pass 1 done. Every value 1..n that exists sits in its home seat. Now scan "
         "for the first seat i whose value isn't i+1.",
    marks=home_marks(0),
    state=[["array", " ".join(map(str, arr))], ["swaps total", swaps]])

miss = None
for i in range(n):
    ok = arr[i] == i + 1
    add(act=2, code="fast", line=5,
        note=f"Seat {i}: nums[{i}] = {arr[i]}, expected {i+1}. "
             + ("Correct, move on." if ok else f"Wrong — {i+1} never arrived."),
        pointers={"i": i},
        marks={**home_marks(i), str(i): "good" if ok else "bad"},
        state=[["i", i], ["nums[i]", arr[i]], ["expected", i + 1]])
    if not ok:
        miss = i + 1
        break
if miss is None:
    miss = n + 1
add(act=2, code="fast", line=6 if miss <= n else 7,
    note=f"First empty seat is index {miss-1}: {miss} is missing. Same answer as the "
         "set, with zero extra memory.",
    marks={**{str(k): "good" for k in range(n) if arr[k] == k + 1},
           str(miss - 1): "bad"} if miss <= n else {str(k): "good" for k in range(n)},
    state=[["answer", miss], ["extra memory", "O(1)"], ["swaps", swaps]],
    banner=f"First missing positive = {miss}   (set said {cand}) — O(1) space")

# ---- Act 3: edge case — fully packed 1..n ----
edge = [1, 2, 3]
add(act=3, cells=edge, labels=[0, 1, 2], code="fast", line=0,
    intro="when 1..n are all home already, no seat is wrong — the answer is n+1.",
    invariant="every value is already in its home seat, so no swaps happen.",
    note="Edge case: [1, 2, 3] is already packed. Every value is home, so the gap is "
         "past the end.",
    pointers={"i": 0}, marks={"0": "good", "1": "good", "2": "good"},
    state=[["n", len(edge)], ["swaps", 0]])
en = len(edge)
for i in range(en):
    add(act=3, code="fast", line=5,
        note=f"Seat {i}: nums[{i}] = {edge[i]} = {i+1}. Correct.",
        pointers={"i": i},
        marks={str(k): "good" for k in range(en)},
        state=[["i", i], ["nums[i]", edge[i]], ["expected", i + 1]])
add(act=3, code="fast", line=7,
    note=f"No wrong seat anywhere: 1..{en} are all present, so the first missing "
         f"positive is {en + 1}.",
    marks={str(k): "good" for k in range(en)},
    state=[["answer", en + 1], ["extra memory", "O(1)"]],
    banner=f"All of 1..{en} present → first missing positive = {en + 1}")

trace = {
    "player": "linear",
    "title": "First Missing Positive — the array as its own hash table",
    "acts": ["Set baseline (O(n) space)", "The idea: value v → index v-1",
             "Cyclic sort in place", "Edge case: fully packed"],
    "code": {"set": SET, "fast": FAST},
    "legend": [["active", "index being placed"], ["good", "value in its home seat"],
               ["bad", "out of range / the gap"], ["dim", "not yet placed"]],
    "cells": nums, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
