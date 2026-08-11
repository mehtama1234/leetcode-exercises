"""Full-arc linear trace for Find Median from Data Stream (295).

Mirrors solution.py: the naive sorted-list-with-O(n)-shift, why keeping the whole
stream sorted is waste, then the two-heaps split (max-heap `low` + min-heap
`high`) whose tops give the median in O(1). The stream is the linear row; `low`
and `high` are drawn as two stacked sidebar tables (two sidebars-worth of rows for
the two-heaps median). Writes trace.json.
"""
import json
import os
import heapq

frames = []


def add(**f):
    frames.append(f)


NAIVE = [
    "lo, hi = binary search insert point",
    "self._nums.insert(lo, num)   # O(n) shift",
    "# median = middle by index",
]
FAST = [
    "heappush(low, -num)              # into max-heap",
    "heappush(high, -heappop(low))    # move top across",
    "if len(high) > len(low):",
    "    heappush(low, -heappop(high))  # rebalance",
    "# median from the two tops, O(1)",
]

stream = [1, 2, 3]  # medians: 1, 1.5, 2.0


def two_sidebars(low, high, median):
    """low is a max-heap of negated values; high a min-heap.
    Render both halves in one sidebar table: low (bottom half) then high (top half),
    with each heap's boundary top marked."""
    low_vals = sorted((-v for v in low), reverse=True)   # largest first = top
    high_vals = sorted(high)                              # smallest first = top
    rows = []
    rows.append(["── low (max-heap) ──", f"{len(low_vals)} vals"])
    for i, v in enumerate(low_vals):
        rows.append([("top → " if i == 0 else "   ") + str(v), "≤ median"])
    rows.append(["── high (min-heap) ──", f"{len(high_vals)} vals"])
    for i, v in enumerate(high_vals):
        rows.append([("top → " if i == 0 else "   ") + str(v), "≥ median"])
    return {"title": f"two heaps split at the middle  (median {median})", "rows": rows}


def median(low, high):
    if len(low) > len(high):
        return float(-low[0])
    if not low and not high:
        return "—"
    if not low:                     # mid-step, before rebalance
        return float(high[0])
    return (-low[0] + high[0]) / 2


# ---- Act 0: naive sorted list with O(n) shift ----
nums = []
add(act=0, cells=[], code="naive", line=1,
    intro="every add keeps the WHOLE stream sorted — an O(n) shift each time.",
    invariant="_nums is fully sorted after every add.",
    note="Naive: keep a sorted list. Binary-search the spot (O(log n)) but shift the "
         "tail to insert (O(n)).",
    state=[["stored", 0], ["per add", "O(n) shift"]])
for x in stream:
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    nums.insert(lo, x)
    n = len(nums)
    mid = n // 2
    med = float(nums[mid]) if n % 2 else (nums[mid - 1] + nums[mid]) / 2
    mid_marks = {}
    if n % 2:
        mid_marks[str(mid)] = "good"
    else:
        mid_marks[str(mid - 1)] = "good"
        mid_marks[str(mid)] = "good"
    add(act=0, cells=list(nums), labels=list(range(n)), code="naive", line=1,
        note=f"add({x}): insert at index {lo}, shifting the tail. Sorted → {nums}. "
             f"median = {med}.",
        marks=mid_marks,
        state=[["added", x], ["stored", n], ["median", med]],
        banner=f"add({x}) → median {med}")

add(act=0, code="naive", line=1,
    note="Each add pays an O(n) shift to keep everything sorted — but the median only "
         "needs the one or two middle values.",
    state=[["kept sorted", "all n"], ["median needs", "middle 1–2"]])

# ---- Act 1: the waste ----
add(act=1,
    intro="we sort the entire stream but only ever read the center.",
    note="Keeping all n numbers in order costs O(n) per insert. The median never reads "
         "anything but the middle — the rest of the order is waste.",
    state=[["per add", "O(n)"], ["median reads", "1–2 middle values"]])
add(act=1,
    note="Split the stream in two: a max-heap `low` (smaller half, its LARGEST on top) "
         "and a min-heap `high` (larger half, its SMALLEST on top). The two tops are the "
         "middle — median in O(1), each add O(log n).",
    state=[["low", "max-heap (smaller half)"], ["high", "min-heap (larger half)"], ["per add", "O(log n)"]])

# ---- Act 2: fast two heaps ----
low, high = [], []
add(act=2, cells=[], code="fast", line=4,
    intro="watch the split stay balanced: low never smaller than high, tops = middle.",
    invariant="every value in low ≤ every value in high; sizes differ by ≤ 1 (low holds the extra).",
    note="Two empty heaps. Each add: push to low, shove low's top across to high, then "
         "rebalance sizes.",
    sidebar={"title": "two heaps (empty)", "rows": [["low", "(empty)"], ["high", "(empty)"]]},
    state=[["low size", 0], ["high size", 0]])

seen = []
for x in stream:
    seen.append(x)
    # Step 1
    heapq.heappush(low, -x)
    heapq.heappush(high, -heapq.heappop(low))
    add(act=2, cells=list(seen), labels=list(range(len(seen))), code="fast", line=1,
        marks={str(len(seen) - 1): "active"},
        note=f"add({x}): push into low, then move low's largest across to high — "
             f"this guarantees low ≤ high.",
        sidebar=two_sidebars(low, high, "(rebalancing)"),
        state=[["added", x], ["low size", len(low)], ["high size", len(high)]])
    # Step 2 rebalance
    rebalanced = False
    if len(high) > len(low):
        heapq.heappush(low, -heapq.heappop(high))
        rebalanced = True
    med = median(low, high)
    add(act=2, cells=list(seen), labels=list(range(len(seen))), code="fast",
        line=3 if rebalanced else 4,
        note=(f"high grew bigger — hand its smallest back to low. " if rebalanced else
              "Sizes already balanced. ")
             + (f"median = low's top = {med}." if len(low) > len(high)
                else f"median = (low top + high top)/2 = {med}."),
        marks={str(len(seen) - 1): "dim"},
        sidebar=two_sidebars(low, high, med),
        state=[["low size", len(low)], ["high size", len(high)], ["median", med]],
        banner=f"add({x}) → median {med}   (O(1) from the two tops)")

# verify
import statistics
assert median(low, high) == statistics.median(seen), (median(low, high), seen)

# ---- Act 3: edge case (single number, then negatives crossing zero) ----
low2, high2 = [], []
edge = [5]
for x in edge:
    heapq.heappush(low2, -x)
    heapq.heappush(high2, -heapq.heappop(low2))
    if len(high2) > len(low2):
        heapq.heappush(low2, -heapq.heappop(high2))
med2 = median(low2, high2)
assert med2 == 5.0
add(act=3, cells=[5], labels=[0], code="fast", line=4,
    intro="one number is its own median — low holds it, high is empty.",
    invariant="when the count is odd, low has the extra and its top IS the median.",
    note="Edge: a single add(5). low holds 5, high is empty, so median = low's top = 5.0.",
    marks={"0": "good"},
    sidebar=two_sidebars(low2, high2, med2),
    state=[["low size", len(low2)], ["high size", len(high2)], ["median", med2]],
    banner="add(5) → median 5.0")

# even count crossing zero: -3,-3,4,4 -> median 0.5
low3, high3 = [], []
seen3 = []
for x in [-3, -3, 4, 4]:
    seen3.append(x)
    heapq.heappush(low3, -x)
    heapq.heappush(high3, -heapq.heappop(low3))
    if len(high3) > len(low3):
        heapq.heappush(low3, -heapq.heappop(high3))
med3 = median(low3, high3)
assert med3 == 0.5, med3
add(act=3, cells=list(seen3), labels=list(range(len(seen3))), code="fast", line=4,
    note="Even count across zero: [-3,-3,4,4]. low top = -3, high top = 4, "
         "median = (-3 + 4)/2 = 0.5.",
    marks={"1": "good", "2": "good"},
    sidebar=two_sidebars(low3, high3, med3),
    state=[["low top", -low3[0]], ["high top", high3[0]], ["median", med3]],
    banner="median = 0.5")

trace = {
    "player": "linear",
    "title": "Find Median from a Stream — two heaps split at the middle",
    "acts": ["Naive: sorted list + O(n) shift", "The waste", "Fast: two heaps", "Edge: single / crossing zero"],
    "code": {"naive": NAIVE, "fast": FAST},
    "legend": [["active", "the number just added"], ["good", "the middle value(s)"],
               ["dim", "settled into a half"]],
    "cells": [],
    "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
