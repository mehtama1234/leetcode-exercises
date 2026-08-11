"""Rich full-arc trace for Binary Search, mirroring the two functions in
solution.py. Shows the linear scan's wasted comparisons, then lo/mid/hi
collapsing a sorted window by half each step. Writes trace.json.
"""
import json
import os

nums = [-1, 0, 3, 5, 9, 12]
T = 9  # answer index 4
frames = []

LINEAR = [
    "for i, x in enumerate(nums):",
    "    if x == target:",
    "        return i",
    "return -1",
]
FAST = [
    "lo, hi = 0, len(nums) - 1",
    "while lo <= hi:",
    "    mid = lo + (hi - lo) // 2",
    "    if nums[mid] == target:",
    "        return mid",
    "    if nums[mid] < target:",
    "        lo = mid + 1",
    "    else:",
    "        hi = mid - 1",
]


def add(**f):
    frames.append(f)


# ---- Act 0: linear scan (the honest, wasteful first thought) ----
work = 0
add(act=0, cells=nums, code="linear", line=0,
    intro="the scan walks past sorted values it could have skipped whole halves of.",
    invariant="every index left of i has been checked and ruled out.",
    note=f"Linear scan: check each value against target {T}, left to right. "
         "It never uses that the array is sorted.",
    pointers={"i": 0}, marks={"0": "active"},
    state=[["i", 0], ["target", T], ["comparisons", 0]])
found = None
for i, x in enumerate(nums):
    work += 1
    hit = x == T
    add(act=0, code="linear", line=1 if not hit else 2,
        note=f"nums[{i}] = {x}. " + ("Match." if hit else f"Not {T}, step right."),
        pointers={"i": i},
        marks={str(i): "good" if hit else "active", **{str(k): "dim" for k in range(i)}},
        state=[["i", i], ["nums[i]", x], ["comparisons", work]])
    if hit:
        found = i
        break
add(act=0, code="linear", line=2,
    note=f"Found at index {found} — but it took {work} comparisons, and it would "
         f"take {len(nums)} on a miss. Sorted or shuffled, this scan can't tell.",
    pointers={"i": found}, marks={str(found): "good", **{str(k): "dim" for k in range(found)}},
    state=[["answer", found], ["comparisons", work]])

# ---- Act 1: the waste ----
add(act=1,
    intro="one look at the middle rules out half the array — the scan threw that away.",
    note=f"The scan checked {work} cells one by one. But the array is SORTED: if "
         "the middle is too small, everything left of it is too small too.",
    marks={str(k): "dim" for k in range(len(nums))},
    state=[["comparisons (scan)", work], ["ignored", "the array is sorted"]])
add(act=1,
    note="Each comparison against the middle can delete HALF of what's left. "
         "n=1000 → ~10 steps instead of 1000. That halving is the whole idea.",
    marks={str(k): "dim" for k in range(len(nums))},
    state=[["scan at n=1000", "~1000"], ["binary at n=1000", "~10"]])

# ---- Act 2: binary search ----
def win_marks(lo, hi, mid=None, extra=None):
    m = {}
    for k in range(len(nums)):
        if lo <= k <= hi:
            m[str(k)] = "active" if k == mid else "dim"
        else:
            m[str(k)] = "bad"  # discarded half
    if extra:
        m.update(extra)
    return m


steps = 0
add(act=2, cells=nums, code="fast", line=0,
    intro="lo and hi are the fence; mid is the probe. Discarded cells go dark.",
    invariant="if target is in the array, it is inside [lo, hi].",
    note=f"Binary search for {T}. Keep a window [lo, hi] that could still hold it; "
         "look only at the middle.",
    pointers={"lo": 0, "hi": len(nums) - 1},
    marks=win_marks(0, len(nums) - 1),
    state=[["lo", 0], ["hi", len(nums) - 1], ["target", T], ["steps", 0]])

lo, hi = 0, len(nums) - 1
ans = -1
while lo <= hi:
    steps += 1
    mid = lo + (hi - lo) // 2
    add(act=2, code="fast", line=2,
        note=f"Window [{lo}, {hi}]. mid = {mid}, nums[mid] = {nums[mid]}.",
        pointers={"lo": lo, "mid": mid, "hi": hi},
        marks=win_marks(lo, hi, mid),
        state=[["lo", lo], ["mid", mid], ["hi", hi], ["nums[mid]", nums[mid]], ["steps", steps]])
    if nums[mid] == T:
        ans = mid
        add(act=2, code="fast", line=4,
            note=f"nums[{mid}] = {T} = target. Done in {steps} steps, not {work}.",
            pointers={"lo": lo, "mid": mid, "hi": hi},
            marks=win_marks(lo, hi, extra={str(mid): "good"}),
            state=[["answer", mid], ["steps", steps], ["vs scan", work]],
            banner=f"Found {T} at index {mid}   — {steps} steps vs {work} scanned")
        break
    if nums[mid] < T:
        add(act=2, code="fast", line=6,
            note=f"{nums[mid]} < {T}: the target is right of mid. Drop [{lo}, {mid}] — "
                 "half the window gone.",
            pointers={"lo": lo, "mid": mid, "hi": hi},
            marks=win_marks(lo, hi, mid),
            state=[["rule", "nums[mid] < target"], ["lo →", mid + 1], ["steps", steps]])
        lo = mid + 1
    else:
        add(act=2, code="fast", line=8,
            note=f"{nums[mid]} > {T}: the target is left of mid. Drop [{mid}, {hi}] — "
                 "half the window gone.",
            pointers={"lo": lo, "mid": mid, "hi": hi},
            marks=win_marks(lo, hi, mid),
            state=[["rule", "nums[mid] > target"], ["hi →", mid - 1], ["steps", steps]])
        hi = mid - 1

# ---- Act 3: edge case — target absent, window empties ----
edge = [1, 2, 3, 4, 5]
ET = 6
add(act=3, cells=edge, code="fast", line=1,
    intro="when the answer is missing, lo passes hi and the window closes empty.",
    invariant="lo > hi means no index is left that could hold the target.",
    note=f"Edge case: search for {ET}, which isn't present. Watch the window "
         "shrink to nothing.",
    pointers={"lo": 0, "hi": len(edge) - 1},
    marks={str(k): "dim" for k in range(len(edge))},
    state=[["target", ET], ["lo", 0], ["hi", len(edge) - 1]])
lo, hi = 0, len(edge) - 1
es = 0
while lo <= hi:
    es += 1
    mid = lo + (hi - lo) // 2
    m = {}
    for k in range(len(edge)):
        m[str(k)] = ("active" if k == mid else "dim") if lo <= k <= hi else "bad"
    add(act=3, code="fast", line=2,
        note=f"Window [{lo}, {hi}]. mid={mid}, nums[mid]={edge[mid]} < {ET}, go right.",
        pointers={"lo": lo, "mid": mid, "hi": hi}, marks=m,
        state=[["lo", lo], ["mid", mid], ["hi", hi], ["nums[mid]", edge[mid]]])
    if edge[mid] < ET:
        lo = mid + 1
    else:
        hi = mid - 1
add(act=3, code="fast", line=1,
    note=f"lo={lo} > hi={hi}: the window is empty, so {ET} is not here. Return -1.",
    marks={str(k): "bad" for k in range(len(edge))},
    state=[["lo", lo], ["hi", hi], ["answer", -1]],
    banner=f"{ET} absent — window emptied, return -1")

trace = {
    "player": "linear",
    "title": "Binary Search — from a full scan to a window halving each step",
    "acts": ["Linear scan", "The waste", "Binary search", "Edge case: target absent"],
    "code": {"linear": LINEAR, "fast": FAST},
    "legend": [["active", "current mid"], ["good", "the answer"],
               ["bad", "discarded half"], ["dim", "still in the window"]],
    "cells": nums, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
