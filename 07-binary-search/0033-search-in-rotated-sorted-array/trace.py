"""Rich full-arc trace for Search in Rotated Sorted Array, mirroring the two
functions in solution.py. Shows the O(n) scan, then lo/mid/hi collapsing: at
each mid one half is provably sorted, so we can still throw away half.
Writes trace.json.
"""
import json
import os

nums = [4, 5, 6, 7, 0, 1, 2]  # target 0 is at index 4
T = 0
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
    "    if nums[lo] <= nums[mid]:      # left half sorted",
    "        if nums[lo] <= target < nums[mid]:",
    "            hi = mid - 1",
    "        else:",
    "            lo = mid + 1",
    "    else:                          # right half sorted",
    "        if nums[mid] < target <= nums[hi]:",
    "            lo = mid + 1",
    "        else:",
    "            hi = mid - 1",
    "return -1",
]


def add(**f):
    frames.append(f)


# ---- Act 0: linear scan ----
work = 0
found = None
add(act=0, cells=nums, code="linear", line=0,
    intro="the scan ignores that the array is two sorted runs joined at a seam.",
    invariant="every index left of i has been checked and ruled out.",
    note=f"Linear scan: check each value against target {T}. It works on a rotated "
         "array, but treats it like a shuffled one.",
    pointers={"i": 0}, marks={"0": "active"},
    state=[["i", 0], ["target", T], ["comparisons", 0]])
for i, x in enumerate(nums):
    work += 1
    hit = x == T
    add(act=0, code="linear", line=1 if not hit else 2,
        note=f"nums[{i}] = {x}. " + ("Match." if hit else f"Not {T}."),
        pointers={"i": i},
        marks={str(i): "good" if hit else "active", **{str(k): "dim" for k in range(i)}},
        state=[["i", i], ["nums[i]", x], ["comparisons", work]])
    if hit:
        found = i
        break
add(act=0, code="linear", line=2,
    note=f"Found at index {found} after {work} comparisons — and a miss would cost "
         f"all {len(nums)}. The rotation didn't have to slow us down this much.",
    pointers={"i": found}, marks={str(found): "good", **{str(k): "dim" for k in range(found)}},
    state=[["answer", found], ["comparisons", work]])

# ---- Act 1: the structure a rotation leaves behind ----
add(act=1,
    intro="split anywhere and ONE side is a clean sorted run — that side we can trust.",
    note="A rotated sorted array is two ascending runs: [4,5,6,7] then [0,1,2]. The "
         "seam sits in only one half, so the OTHER half is fully sorted.",
    marks={"0": "dim", "1": "dim", "2": "dim", "3": "good", "4": "good", "5": "dim", "6": "dim"},
    state=[["left run", "4 5 6 7"], ["right run", "0 1 2"], ["seam", "7 → 0"]])
add(act=1,
    note="At any mid, compare endpoints to find the sorted half. If target lies "
         "inside that half's known range, search it; otherwise search the other. "
         "Either way half the array goes — still ~log n.",
    marks={str(k): "dim" for k in range(len(nums))},
    state=[["scan at n=1000", "~1000"], ["binary at n=1000", "~10"]])

# ---- Act 2: binary search over the rotation ----
def win_marks(lo, hi, mid=None, sorted_half=None, extra=None):
    """sorted_half: ('L', lo, mid) or ('R', mid, hi) to shade the trusted run good."""
    m = {}
    for k in range(len(nums)):
        if lo <= k <= hi:
            m[str(k)] = "active" if k == mid else "dim"
        else:
            m[str(k)] = "bad"
    if sorted_half:
        side, a, b = sorted_half
        for k in range(a, b + 1):
            if k != mid:
                m[str(k)] = "good"
    if extra:
        m.update(extra)
    return m


steps = 0
add(act=2, cells=nums, code="fast", line=0,
    intro="each step: name the sorted half (green), then keep or drop it by range.",
    invariant="if target is present it is inside [lo, hi].",
    note=f"Binary search for {T}. Window [lo, hi]; at mid, one half is sorted and "
         "tells us where target can be.",
    pointers={"lo": 0, "hi": len(nums) - 1},
    marks=win_marks(0, len(nums) - 1),
    state=[["lo", 0], ["hi", len(nums) - 1], ["target", T], ["steps", 0]])

lo, hi = 0, len(nums) - 1
ans = -1
while lo <= hi:
    steps += 1
    mid = lo + (hi - lo) // 2
    add(act=2, code="fast", line=2,
        note=f"Window [{lo}, {hi}]. mid={mid}, nums[mid]={nums[mid]}.",
        pointers={"lo": lo, "mid": mid, "hi": hi},
        marks=win_marks(lo, hi, mid),
        state=[["lo", lo], ["mid", mid], ["hi", hi], ["nums[mid]", nums[mid]], ["steps", steps]])
    if nums[mid] == T:
        ans = mid
        add(act=2, code="fast", line=4,
            note=f"nums[{mid}] = {T} = target. Found in {steps} steps, not {work}.",
            pointers={"lo": lo, "mid": mid, "hi": hi},
            marks=win_marks(lo, hi, extra={str(mid): "good"}),
            state=[["answer", mid], ["steps", steps], ["vs scan", work]],
            banner=f"Found {T} at index {mid}   — {steps} steps vs {work} scanned")
        break
    if nums[lo] <= nums[mid]:  # left sorted
        inside = nums[lo] <= T < nums[mid]
        add(act=2, code="fast", line=6 if inside else 8,
            note=f"nums[lo]={nums[lo]} <= nums[mid]={nums[mid]}: LEFT [{lo}, {mid}] is "
                 f"sorted (green). Is {nums[lo]} <= {T} < {nums[mid]}? "
                 + ("Yes → search left." if inside else "No → search right."),
            pointers={"lo": lo, "mid": mid, "hi": hi},
            marks=win_marks(lo, hi, mid, sorted_half=("L", lo, mid)),
            state=[["sorted half", f"[{lo}, {mid}] left"],
                   ["target in it?", "yes" if inside else "no"],
                   [("hi →" if inside else "lo →"), (mid - 1 if inside else mid + 1)]])
        if inside:
            hi = mid - 1
        else:
            lo = mid + 1
    else:  # right sorted
        inside = nums[mid] < T <= nums[hi]
        add(act=2, code="fast", line=11 if inside else 13,
            note=f"nums[lo]={nums[lo]} > nums[mid]={nums[mid]}: RIGHT [{mid}, {hi}] is "
                 f"sorted (green). Is {nums[mid]} < {T} <= {nums[hi]}? "
                 + ("Yes → search right." if inside else "No → search left."),
            pointers={"lo": lo, "mid": mid, "hi": hi},
            marks=win_marks(lo, hi, mid, sorted_half=("R", mid, hi)),
            state=[["sorted half", f"[{mid}, {hi}] right"],
                   ["target in it?", "yes" if inside else "no"],
                   [("lo →" if inside else "hi →"), (mid + 1 if inside else mid - 1)]])
        if inside:
            lo = mid + 1
        else:
            hi = mid - 1

# ---- Act 3: edge case — target absent in a rotated array ----
edge = [4, 5, 6, 7, 0, 1, 2]
ET = 3
add(act=3, cells=edge, code="fast", line=0,
    intro="the same sorted-half logic prunes correctly even when nothing matches.",
    invariant="each step still discards a half we've proven target can't be in.",
    note=f"Edge case: target {ET} is absent. The window must still collapse to "
         "empty without ever losing the target.",
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
    if edge[lo] <= edge[mid]:
        inside = edge[lo] <= ET < edge[mid]
        for k in range(lo, mid):
            m[str(k)] = "good"
        side = "left"
        nxt = f"hi → {mid - 1}" if inside else f"lo → {mid + 1}"
    else:
        inside = edge[mid] < ET <= edge[hi]
        for k in range(mid + 1, hi + 1):
            m[str(k)] = "good"
        side = "right"
        nxt = f"lo → {mid + 1}" if inside else f"hi → {mid - 1}"
    add(act=3, code="fast", line=2,
        note=f"Window [{lo}, {hi}]. mid={mid}, nums[mid]={edge[mid]}. {side} half "
             f"sorted; {ET} {'inside' if inside else 'not inside'} → {nxt}.",
        pointers={"lo": lo, "mid": mid, "hi": hi}, marks=m,
        state=[["lo", lo], ["mid", mid], ["hi", hi], ["nums[mid]", edge[mid]]])
    if edge[lo] <= edge[mid]:
        if edge[lo] <= ET < edge[mid]:
            hi = mid - 1
        else:
            lo = mid + 1
    else:
        if edge[mid] < ET <= edge[hi]:
            lo = mid + 1
        else:
            hi = mid - 1
add(act=3, code="fast", line=15,
    note=f"lo={lo} > hi={hi}: window empty, {ET} is not in the array. Return -1.",
    marks={str(k): "bad" for k in range(len(edge))},
    state=[["lo", lo], ["hi", hi], ["answer", -1]],
    banner=f"{ET} absent — window emptied, return -1")

trace = {
    "player": "linear",
    "title": "Search in Rotated Array — one sorted half tells you where to look",
    "acts": ["Linear scan", "The structure", "Binary search over the rotation",
             "Edge case: target absent"],
    "code": {"linear": LINEAR, "fast": FAST},
    "legend": [["active", "current mid"], ["good", "the sorted half / answer"],
               ["bad", "discarded half"], ["dim", "still in the window"]],
    "cells": nums, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
