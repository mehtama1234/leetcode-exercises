"""Rich full-arc trace for Find Minimum in Rotated Sorted Array, mirroring the
two functions in solution.py. Shows the O(n) min-scan, then lo/mid/hi
collapsing onto the cliff by comparing mid to hi. Writes trace.json.
"""
import json
import os

nums = [4, 5, 6, 7, 0, 1, 2]  # min is 0 at index 4
frames = []

LINEAR = [
    "return min(nums)",
]
FAST = [
    "lo, hi = 0, len(nums) - 1",
    "while lo < hi:",
    "    mid = lo + (hi - lo) // 2",
    "    if nums[mid] > nums[hi]:",
    "        lo = mid + 1",
    "    else:",
    "        hi = mid",
    "return nums[lo]",
]


def add(**f):
    frames.append(f)


# ---- Act 0: scan everything and keep the smallest ----
work = 0
best = None
best_i = None
add(act=0, cells=nums, code="linear", line=0,
    intro="the scan reads all n values even though only one 'cliff' matters.",
    invariant="best holds the smallest value seen in nums[0..i].",
    note="Linear: read every element, keep the smallest. Correct, but O(n) and "
         "it ignores that the array is almost sorted.",
    pointers={"i": 0}, marks={"0": "active"},
    state=[["i", 0], ["min so far", "—"], ["reads", 0]])
for i, x in enumerate(nums):
    work += 1
    if best is None or x < best:
        best, best_i = x, i
    add(act=0, code="linear", line=0,
        note=f"nums[{i}] = {x}. Smallest so far is {best} (index {best_i}).",
        pointers={"i": i},
        marks={str(i): "active", str(best_i): "good", **{str(k): "dim" for k in range(i) if k != best_i}},
        state=[["i", i], ["nums[i]", x], ["min so far", best], ["reads", work]])
add(act=0, code="linear", line=0,
    note=f"Minimum is {best} at index {best_i} — after reading all {work} elements.",
    marks={str(best_i): "good", **{str(k): "dim" for k in range(len(nums)) if k != best_i}},
    state=[["answer", best], ["reads", work]])

# ---- Act 1: the waste + the structure ----
add(act=1,
    intro="the array is two rising runs; the minimum sits right after the drop.",
    note=f"The scan touched all {work} cells. But rotating a sorted array leaves "
         "exactly ONE cliff: a big value followed by a small one. The min is that "
         "small one.",
    marks={"3": "active", "4": "good", **{str(k): "dim" for k in [0, 1, 2, 5, 6]}},
    state=[["reads (scan)", work], ["cliff", "7 → 0"], ["min", "just after the cliff"]])
add(act=1,
    note="Comparing the middle to the RIGHT end says which side the cliff is on. "
         "So we can bisect to it in ~log n steps and skip most of the array.",
    marks={str(k): "dim" for k in range(len(nums))},
    state=[["scan at n=1000", "~1000"], ["binary at n=1000", "~10"]])

# ---- Act 2: binary search toward the cliff ----
def win_marks(lo, hi, mid=None, extra=None):
    m = {}
    for k in range(len(nums)):
        if lo <= k <= hi:
            m[str(k)] = "active" if k == mid else "dim"
        else:
            m[str(k)] = "bad"
    if extra:
        m.update(extra)
    return m


steps = 0
add(act=2, cells=nums, code="fast", line=0,
    intro="hi is the anchor: mid > nums[hi] means the min is right of mid.",
    invariant="the minimum is always inside [lo, hi].",
    note="Binary search. Compare nums[mid] to nums[hi] to decide which half keeps "
         "the cliff, and shrink toward it.",
    pointers={"lo": 0, "hi": len(nums) - 1},
    marks=win_marks(0, len(nums) - 1),
    state=[["lo", 0], ["hi", len(nums) - 1], ["nums[hi]", nums[-1]], ["steps", 0]])

lo, hi = 0, len(nums) - 1
while lo < hi:
    steps += 1
    mid = lo + (hi - lo) // 2
    add(act=2, code="fast", line=2,
        note=f"Window [{lo}, {hi}]. mid={mid}, nums[mid]={nums[mid]}, nums[hi]={nums[hi]}.",
        pointers={"lo": lo, "mid": mid, "hi": hi},
        marks=win_marks(lo, hi, mid),
        state=[["lo", lo], ["mid", mid], ["hi", hi],
               ["nums[mid]", nums[mid]], ["nums[hi]", nums[hi]], ["steps", steps]])
    if nums[mid] > nums[hi]:
        add(act=2, code="fast", line=4,
            note=f"{nums[mid]} > {nums[hi]}: [mid, hi] wraps, so the cliff is right of "
                 f"mid. Drop [{lo}, {mid}]. lo → {mid + 1}.",
            pointers={"lo": lo, "mid": mid, "hi": hi},
            marks=win_marks(lo, hi, mid),
            state=[["rule", "nums[mid] > nums[hi]"], ["lo →", mid + 1], ["steps", steps]])
        lo = mid + 1
    else:
        add(act=2, code="fast", line=6,
            note=f"{nums[mid]} <= {nums[hi]}: [mid, hi] is sorted, so the min is mid or "
                 f"left of it. Keep mid: hi → {mid}.",
            pointers={"lo": lo, "mid": mid, "hi": hi},
            marks=win_marks(lo, hi, mid),
            state=[["rule", "nums[mid] <= nums[hi]"], ["hi →", mid], ["steps", steps]])
        hi = mid
add(act=2, code="fast", line=7,
    note=f"lo == hi == {lo}: the window is one cell. nums[{lo}] = {nums[lo]} is the "
         f"minimum, found in {steps} steps.",
    pointers={"lo": lo, "hi": hi},
    marks=win_marks(lo, hi, extra={str(lo): "good"}),
    state=[["answer", nums[lo]], ["steps", steps], ["vs scan", work]],
    banner=f"Minimum {nums[lo]} at index {lo}   — {steps} steps vs {work} scanned")

# ---- Act 3: edge case — not rotated at all ----
edge = [11, 13, 15, 17]
add(act=3, cells=edge, code="fast", line=0,
    intro="with no cliff, every step says 'go left' and hi slides to index 0.",
    invariant="nums[mid] <= nums[hi] holds the whole way, so hi keeps shrinking.",
    note="Edge case: the array was never rotated. There is no cliff, so the "
         "minimum is simply the first element.",
    pointers={"lo": 0, "hi": len(edge) - 1},
    marks={str(k): "dim" for k in range(len(edge))},
    state=[["lo", 0], ["hi", len(edge) - 1], ["nums[hi]", edge[-1]]])
lo, hi = 0, len(edge) - 1
es = 0
while lo < hi:
    es += 1
    mid = lo + (hi - lo) // 2
    m = {}
    for k in range(len(edge)):
        m[str(k)] = ("active" if k == mid else "dim") if lo <= k <= hi else "bad"
    add(act=3, code="fast", line=6,
        note=f"mid={mid}, nums[mid]={edge[mid]} <= nums[hi]={edge[hi]}: sorted, hi → {mid}.",
        pointers={"lo": lo, "mid": mid, "hi": hi}, marks=m,
        state=[["lo", lo], ["mid", mid], ["hi", hi], ["hi →", mid]])
    hi = mid
add(act=3, code="fast", line=7,
    note=f"lo == hi == {lo}. nums[{lo}] = {edge[lo]} — the front element, exactly as "
         "expected for an unrotated array.",
    pointers={"lo": lo, "hi": hi},
    marks={"0": "good", **{str(k): "bad" for k in range(1, len(edge))}},
    state=[["answer", edge[lo]], ["steps", es]],
    banner=f"Not rotated → minimum {edge[0]} at index 0")

trace = {
    "player": "linear",
    "title": "Find Minimum in Rotated Array — bisecting toward the cliff",
    "acts": ["Scan for the min", "The waste", "Binary search to the cliff",
             "Edge case: not rotated"],
    "code": {"linear": LINEAR, "fast": FAST},
    "legend": [["active", "current mid"], ["good", "the minimum"],
               ["bad", "discarded half"], ["dim", "still in the window"]],
    "cells": nums, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
