"""Rich full-arc trace for Range Sum Query - Immutable, mirroring NumArray in
solution.py. Shows the brute force re-adding a range per query, names the waste,
builds the prefix array once, then answers each range as a single subtraction.
Writes trace.json.
"""
import json
import os

nums = [-2, 0, 3, -5, 2, -1]
queries = [(0, 2), (2, 5), (0, 5)]  # answers 1, -1, -3
frames = []

BRUTE = [
    "def sumRange(left, right):",
    "    return sum(nums[left : right+1])",
]
BUILD = [
    "prefix = [0] * (n + 1)",
    "for i, x in enumerate(nums):",
    "    prefix[i+1] = prefix[i] + x",
]
FAST = [
    "def sumRange(left, right):",
    "    return prefix[right+1] - prefix[left]",
]


def add(**f):
    frames.append(f)


# ---- Act 0: brute force — re-add each range ----
work = 0
add(act=0, cells=nums, code="brute", line=0,
    intro="every query walks its whole range and adds — overlapping queries re-add the same cells.",
    invariant="sumRange returns the exact sum of nums[left..right] by literally adding it.",
    note="Brute force: to answer a range, add up every element from left to right.",
    marks={"0": "active"},
    state=[["queries", len(queries)], ["additions", 0]])
for (l, r) in queries:
    total = 0
    for k in range(l, r + 1):
        total += nums[k]
        work += 1
        add(act=0, code="brute", line=1,
            note=f"sumRange({l},{r}): add nums[{k}] = {nums[k]} -> running {total}.",
            window=[l, r],
            marks={**{str(m): "good" for m in range(l, k + 1)}, str(k): "active"},
            state=[["range", f"[{l},{r}]"], ["running", total], ["additions", work]])
    add(act=0, code="brute", line=1,
        note=f"sumRange({l},{r}) = {total}.",
        window=[l, r], marks={str(m): "good" for m in range(l, r + 1)},
        state=[["range", f"[{l},{r}]"], ["sum", total], ["additions", work]])
add(act=0, code="brute", line=1,
    note=f"Three queries cost {work} additions, and overlapping ranges re-added the same "
         "cells. With thousands of queries this is the waste.",
    marks={str(k): "dim" for k in range(len(nums))},
    state=[["additions (brute)", work], ["pattern", "q * range length"]])

# ---- Act 1: the waste ----
add(act=1,
    intro="every query re-sums a prefix of the array — but a prefix sum never changes; compute it once.",
    note="The sum of nums[left..right] is (sum of first right+1) minus (sum of first "
         "left). Both are prefix sums — compute them ALL once, up front.",
    marks={str(k): "dim" for k in range(len(nums))},
    state=[["insight", "range = prefix - prefix"], ["build cost", "one pass"]])
add(act=1,
    note="After that, each query is a single subtraction: no scan, regardless of how "
         "wide the range or how many queries.",
    marks={str(k): "dim" for k in range(len(nums))},
    state=[["per query", "O(1)"], ["was", "O(range)"]])

# ---- Act 2: build the prefix array, then subtract ----
prefix = [0] * (len(nums) + 1)
# show prefix as its own labeled row (index 0..n), values built up
plabels = list(range(len(nums) + 1))
add(act=2, cells=prefix[:], labels=plabels, code="build", line=0,
    intro="prefix[i] = sum of the first i numbers. prefix[0] = 0 so range sums need no edge case.",
    invariant="prefix[i] holds nums[0] + ... + nums[i-1]; length n+1.",
    note="Build once: prefix has n+1 slots, prefix[0] = 0 (nothing summed yet).",
    marks={"0": "good"},
    state=[["prefix len", len(prefix)], ["additions", 0]])
buildwork = 0
for i, x in enumerate(nums):
    prefix[i + 1] = prefix[i] + x
    buildwork += 1
    add(act=2, cells=prefix[:], labels=plabels, code="build", line=2,
        note=f"prefix[{i+1}] = prefix[{i}] + nums[{i}] = {prefix[i]} + {x} = {prefix[i+1]}.",
        marks={**{str(m): "good" for m in range(i + 1)}, str(i + 1): "active"},
        state=[["i", i], ["nums[i]", x], [f"prefix[{i+1}]", prefix[i + 1]],
               ["additions", buildwork]])
add(act=2, cells=prefix[:], labels=plabels, code="build", line=2,
    note=f"Prefix array built in {buildwork} additions — once, forever. Now every query "
         "is one subtraction.",
    marks={str(m): "good" for m in range(len(prefix))},
    state=[["prefix", str(prefix)], ["build additions", buildwork]])
# now answer the queries as subtractions
for (l, r) in queries:
    ans = prefix[r + 1] - prefix[l]
    add(act=2, cells=prefix[:], labels=plabels, code="fast", line=1,
        note=f"sumRange({l},{r}) = prefix[{r+1}] - prefix[{l}] = {prefix[r+1]} - "
             f"{prefix[l]} = {ans}. No scan.",
        arc=[l, r + 1],
        marks={str(r + 1): "good", str(l): "bad"},
        state=[["range", f"[{l},{r}]"], [f"prefix[{r+1}]", prefix[r + 1]],
               [f"prefix[{l}]", prefix[l]], ["sum", ans]],
        banner=f"sumRange({l},{r}) = {prefix[r+1]} - {prefix[l]} = {ans}   — one subtraction")

# ---- Act 3: edge case — single-element range ----
edge_l, edge_r = 3, 3
ans = prefix[edge_r + 1] - prefix[edge_l]
add(act=3, cells=prefix[:], labels=plabels, code="fast", line=1,
    intro="a one-cell range is right+1 exactly one past left — the same subtraction, no special case.",
    invariant="prefix[right+1] - prefix[left] works even when left == right.",
    note=f"Edge case: sumRange(3,3), a single element. prefix[4] - prefix[3] = "
         f"{prefix[4]} - {prefix[3]} = {ans} = nums[3].",
    arc=[edge_l, edge_r + 1],
    marks={str(edge_r + 1): "good", str(edge_l): "bad"},
    state=[["range", "[3,3]"], ["prefix[4]", prefix[4]], ["prefix[3]", prefix[3]],
           ["sum", ans]],
    banner=f"sumRange(3,3) = {prefix[4]} - {prefix[3]} = {ans}   (= nums[3])")

trace = {
    "player": "linear",
    "title": "Range Sum Query — from re-adding to one subtraction",
    "acts": ["Brute force: re-add each range", "The waste",
             "Fast: build prefix, then subtract", "Edge case: single element"],
    "code": {"brute": BRUTE, "build": BUILD, "fast": FAST},
    "legend": [["active", "cell being written / read"], ["good", "prefix[right+1] (kept)"],
               ["bad", "prefix[left] (subtracted off)"], ["dim", "filed away"]],
    "cells": nums, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
