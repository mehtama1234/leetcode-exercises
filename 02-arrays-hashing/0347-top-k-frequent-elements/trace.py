"""Full-arc trace for Top K Frequent Elements, mirroring solution.py: the
count-then-sort baseline and the O(n) bucket-by-frequency pass (frequency is a
bounded integer, so it indexes an array — counting-sort placement replaces the
comparison sort). Linear renderer: nums as cells; counts and frequency buckets in
the sidebar. Writes trace.json.
"""
import json
import os

nums = [1, 1, 1, 2, 2, 3]
k = 2
# counts: 1->3, 2->2, 3->1 ; top 2 = [1, 2]
frames = []

SORT = [
    "counts = Counter(nums)",
    "ordered = sorted(counts, key=counts.get, reverse=True)",
    "return ordered[:k]",
]
FAST = [
    "counts = Counter(nums)",
    "buckets = [[] for _ in range(n+1)]",
    "for value, freq in counts.items():",
    "    buckets[freq].append(value)",
    "for freq in range(n, 0, -1):",
    "    for value in buckets[freq]:",
    "        result.append(value)",
    "        if len(result) == k: return result",
]


def add(**f):
    frames.append(f)


def counts_sidebar(counts, title="counts (value -> freq)"):
    rows = [[str(v), str(c)] for v, c in counts.items()]
    if not rows:
        rows = [["(empty)", ""]]
    return {"title": title, "rows": rows}


n = len(nums)

# ---- Act 0: count, then sort by frequency ----
counts = {}
add(act=0, cells=nums, code="sort", line=0,
    intro="count everything, then order the distinct values by frequency and take the first k.",
    invariant="counts holds the exact frequency of every value seen so far.",
    note=f"Baseline: tally counts, then SORT distinct values by frequency descending, take top {k}.",
    pointers={"i": 0}, marks={"0": "active"}, sidebar=counts_sidebar(counts),
    state=[["k", k]])
for i, x in enumerate(nums):
    counts[x] = counts.get(x, 0) + 1
    add(act=0, code="sort", line=0,
        note=f"nums[{i}] = {x}. counts[{x}] -> {counts[x]}.",
        pointers={"i": i}, marks={str(i): "active"}, sidebar=counts_sidebar(counts),
        state=[["x", x], [f"counts[{x}]", counts[x]]])
ordered = sorted(counts, key=lambda v: counts[v], reverse=True)
add(act=0, code="sort", line=1,
    note=f"Distinct values by frequency: {[(v, counts[v]) for v in ordered]}. Sorting all distinct values costs n log n.",
    sidebar=counts_sidebar(counts),
    state=[["sorted", str(ordered)]])
add(act=0, code="sort", line=2,
    note=f"Take the first {k}: {ordered[:k]}. Correct — but we sorted everything just to read off the top few.",
    sidebar=counts_sidebar(counts),
    banner=f"top {k} = {ordered[:k]} — but we paid a full sort",
    state=[["answer", str(ordered[:k])], ["cost", "O(n log n)"]])

# ---- Act 1: the insight ----
add(act=1,
    intro="a frequency is an integer in 1..n, so it can be an ARRAY INDEX — no comparisons needed.",
    note="A value's frequency is between 1 and n. Make buckets[f] = values seen exactly f times. Then read "
         "buckets from the top frequency down. The frequency IS the sort key, and it lives in a bounded range.",
    state=[["idea", "bucket by frequency"], ["target", "O(n)"]])

# ---- Act 2: bucket by frequency ----
counts = {}
for x in nums:
    counts[x] = counts.get(x, 0) + 1
buckets = [[] for _ in range(n + 1)]


def buckets_sidebar(buckets, hi=None):
    rows = []
    for f in range(len(buckets) - 1, 0, -1):
        marker = "  <-" if f == hi else ""
        rows.append([f"freq {f}", (", ".join(map(str, buckets[f])) or "-") + marker])
    return {"title": "buckets (freq -> values)", "rows": rows}


add(act=2, cells=nums, code="fast", line=1,
    intro="each distinct value drops into the slot for its own frequency.",
    invariant="buckets[f] lists exactly the values whose count equals f.",
    note=f"Counts are done: {dict(counts)}. Now place each value into buckets[its frequency].",
    sidebar=counts_sidebar(counts),
    state=[["counts", str(dict(counts))]])
for value, freq in counts.items():
    buckets[freq].append(value)
    add(act=2, code="fast", line=3,
        note=f"Value {value} has frequency {freq} -> drop it into buckets[{freq}].",
        sidebar=buckets_sidebar(buckets, hi=freq),
        state=[["value", value], ["freq", freq]])
# walk from high freq down
result = []
add(act=2, code="fast", line=4,
    note="Now walk buckets from the highest frequency down, collecting values.",
    sidebar=buckets_sidebar(buckets),
    state=[["result", "[]"], ["need", k]])
done = False
for freq in range(n, 0, -1):
    for value in buckets[freq]:
        result.append(value)
        add(act=2, code="fast", line=6,
            note=f"buckets[{freq}] has {value} -> take it. result = {result}.",
            sidebar=buckets_sidebar(buckets, hi=freq),
            state=[["took", value], ["at freq", freq], ["result", str(result)]])
        if len(result) == k:
            add(act=2, code="fast", line=7,
                note=f"result has {k} values — stop. No comparison sort was ever run.",
                sidebar=buckets_sidebar(buckets, hi=freq),
                banner=f"top {k} = {result} — one linear bucket pass, no sort",
                state=[["answer", str(result)]])
            done = True
            break
    if done:
        break

# ---- Act 3: edge case, k == number of distinct values ----
enums = [7, 7, 8, 8, 9]
ek = 3
ecounts = {}
for x in enums:
    ecounts[x] = ecounts.get(x, 0) + 1
ebuckets = [[] for _ in range(len(enums) + 1)]
for value, freq in ecounts.items():
    ebuckets[freq].append(value)


def ebuckets_sidebar(hi=None):
    rows = []
    for f in range(len(ebuckets) - 1, 0, -1):
        marker = "  <-" if f == hi else ""
        rows.append([f"freq {f}", (", ".join(map(str, ebuckets[f])) or "-") + marker])
    return {"title": "buckets (freq -> values)", "rows": rows}


add(act=3, cells=enums, code="fast", line=4,
    intro="when k equals the distinct count, we simply drain every bucket — the walk just returns them all.",
    invariant="collecting from high frequency down never returns a value out of order.",
    note=f"Edge case: k = {ek} equals the 3 distinct values (7, 8, 9). counts = {dict(ecounts)}. We collect all of them.",
    sidebar=ebuckets_sidebar(),
    state=[["k", ek], ["distinct", 3]])
eresult = []
done = False
for freq in range(len(enums), 0, -1):
    for value in ebuckets[freq]:
        eresult.append(value)
        add(act=3, code="fast", line=6,
            note=f"buckets[{freq}] -> take {value}. result = {eresult}.",
            sidebar=ebuckets_sidebar(hi=freq),
            state=[["took", value], ["at freq", freq], ["result", str(eresult)]])
        if len(eresult) == ek:
            add(act=3, code="fast", line=7,
                note=f"Collected all {ek}. result = {eresult}.",
                sidebar=ebuckets_sidebar(hi=freq),
                banner=f"top {ek} = {eresult} — every distinct value returned",
                state=[["answer", str(eresult)]])
            done = True
            break
    if done:
        break

trace = {
    "player": "linear",
    "title": "Top K Frequent — the frequency is the index, so no sort",
    "acts": ["Baseline: count + sort", "The insight", "Fast: bucket by frequency", "Edge case: k = distinct count"],
    "code": {"sort": SORT, "fast": FAST},
    "legend": [["active", "value being counted"], ["good", "collected into the answer"], ["dim", "inactive"]],
    "cells": nums, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
