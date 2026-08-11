"""Rich full-arc trace for Jump Game, mirroring can_jump in solution.py. Shows the
branching brute force exploring every jump choice, names the blow-up, then runs
the greedy one-pass `reach` frontier, and finishes on the classic zero-trap edge
case. Writes trace.json.
"""
import json
import os

nums = [2, 3, 1, 1, 4]  # reachable -> True
frames = []

BRUTE = [
    "def dfs(i):",
    "    if i >= last: return True",
    "    for step in range(1, nums[i] + 1):",
    "        if dfs(i + step):",
    "            return True",
    "    return False",
]
FAST = [
    "reach = 0",
    "for i, step in enumerate(nums):",
    "    if i > reach:",
    "        return False",
    "    reach = max(reach, i + step)",
    "    if reach >= last:",
    "        return True",
]


def add(**f):
    frames.append(f)


last = len(nums) - 1

# ---- Act 0: brute force — try every jump choice ----
work = 0
order = []  # record (i, depth) visits for narration


def dfs(i, depth):
    global work
    work += 1
    order.append((i, depth))
    if i >= last:
        return True
    for step in range(1, nums[i] + 1):
        if dfs(i + step, depth + 1):
            return True
    return False


add(act=0, cells=nums, code="brute", line=0,
    intro="the brute force branches on every possible jump length from every index — the same indices get re-explored.",
    invariant="dfs(i) is True if some choice of jumps from i reaches the last index.",
    note="Brute force: from index i, TRY every jump length 1..nums[i] and recurse. "
         "One index fans out into many.",
    pointers={"i": 0}, marks={"0": "active"},
    state=[["i", 0], ["choices from 0", nums[0]], ["dfs calls", 0]])
# replay dfs with frames
work = 0
order = []


def dfs_traced(i, depth):
    global work
    work += 1
    at_end = i >= last
    add(act=0, code="brute", line=1 if at_end else 2,
        note=(f"dfs({i}) reaches the last index." if at_end
              else f"dfs({i}): can jump 1..{nums[i]} -> try {list(range(i+1, min(i+nums[i], last)+1))}."),
        pointers={"i": i}, marks={str(i): "good" if at_end else "active"},
        state=[["i", i], ["depth", depth], ["dfs calls", work]])
    if at_end:
        return True
    for step in range(1, nums[i] + 1):
        if i + step <= last and dfs_traced(i + step, depth + 1):
            return True
    return False


ok = dfs_traced(0, 0)
add(act=0, code="brute", line=4,
    note=f"Reachable -> True. But that was {work} dfs calls, and indices like 3 and 4 "
         "get visited from several paths.",
    marks={str(last): "good"},
    state=[["answer", ok], ["dfs calls", work]])

# ---- Act 1: the waste ----
add(act=1,
    intro="the recursion re-asks 'can I finish from index k?' many times — the answer never changes.",
    note=f"{work} calls for 5 indices. Whether you can finish from index k depends only "
         "on k, yet the branching re-computes it per path.",
    marks={str(k): "dim" for k in range(len(nums))},
    state=[["dfs calls (brute)", work], ["pattern", "exponential branching"]])
add(act=1,
    note="We never need WHICH jumps to take — only how far we could possibly get. One "
         "number, the farthest reachable index, captures the whole reachable set.",
    marks={str(k): "dim" for k in range(len(nums))},
    state=[["what we track", "farthest reach"], ["cost", "one pass"]])

# ---- Act 2: greedy frontier ----
reach = 0
add(act=2, cells=nums, code="fast", line=0,
    intro="reach is the farthest index reachable so far. If i ever passes reach we are stranded.",
    invariant="every index <= reach is reachable from the start (reachability is downward-closed).",
    note="Greedy: sweep left to right. reach = farthest index reachable using everything "
         f"seen. Start reach = 0.",
    pointers={"i": 0, "reach": 0}, marks={"0": "active"},
    state=[["i", 0], ["reach", 0], ["steps", 0]])
stepwork = 0
for i, step in enumerate(nums):
    stepwork += 1
    if i > reach:
        add(act=2, code="fast", line=3,
            note=f"i = {i} > reach {reach}: nothing before it jumps far enough. Stuck.",
            pointers={"i": i, "reach": reach},
            marks={str(i): "bad", str(reach): "dim"},
            state=[["i", i], ["reach", reach], ["result", "False"]])
        break
    prev = reach
    reach = max(reach, i + step)
    done = reach >= last
    add(act=2, code="fast", line=6 if done else 4,
        note=f"at i={i} we can jump {step} -> reach = max({prev}, {i}+{step}) = {reach}."
             + (" Last index is within reach." if done else ""),
        pointers={"i": i, "reach": reach},
        marks={**{str(k): "good" for k in range(0, reach + 1) if k <= last},
               str(i): "active"},
        state=[["i", i], ["step", step], ["reach", reach], ["steps", stepwork]])
    if done:
        break
add(act=2, code="fast", line=6,
    note=f"reach {reach} covers the last index {last}. Reachable in {stepwork} steps, "
         "no branching.",
    marks={str(k): "good" for k in range(len(nums))},
    state=[["answer", "True"], ["steps", stepwork], ["vs brute", work]],
    banner=f"Can reach the end -> True   — {stepwork} steps vs {work} brute calls")

# ---- Act 3: edge case — the zero trap ----
edge = [3, 2, 1, 0, 4]
reach = 0
add(act=3, cells=edge, labels=[0, 1, 2, 3, 4], code="fast", line=0,
    intro="a 0 you can't jump OVER is a wall — watch reach stall while i marches past it.",
    invariant="if i ever exceeds reach, no jump sequence lands on i.",
    note="Edge case: [3,2,1,0,4]. The 0 at index 3 is a trap unless reach already passed it.",
    pointers={"i": 0, "reach": 0}, marks={"0": "active"},
    state=[["i", 0], ["reach", 0]])
for i, step in enumerate(edge):
    if i > reach:
        add(act=3, code="fast", line=3,
            note=f"i = {i} > reach {reach}. Index {len(edge)-1} is unreachable — the 0 "
                 "at index 3 capped reach at 3.",
            pointers={"i": i, "reach": reach},
            marks={str(i): "bad", "3": "bad", str(reach): "dim"},
            state=[["i", i], ["reach", reach], ["result", "False"]],
            banner="Stuck behind the 0 at index 3 -> False")
        break
    prev = reach
    reach = max(reach, i + step)
    add(act=3, code="fast", line=4,
        note=f"at i={i}, step {step}: reach = max({prev}, {i+step}) = {reach}."
             + (" reach stalls — 0 adds nothing." if step == 0 else ""),
        pointers={"i": i, "reach": reach},
        marks={**{str(k): "good" for k in range(0, reach + 1)}, str(i): "active"},
        state=[["i", i], ["step", step], ["reach", reach]])

trace = {
    "player": "linear",
    "title": "Jump Game — from branching every jump to one greedy frontier",
    "acts": ["Brute force: try every jump", "The waste", "Fast: greedy reach",
             "Edge case: the zero trap"],
    "code": {"brute": BRUTE, "fast": FAST},
    "legend": [["active", "index we stand on"], ["good", "reachable so far"],
               ["bad", "unreachable / stuck"], ["dim", "filed away"]],
    "cells": nums, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
