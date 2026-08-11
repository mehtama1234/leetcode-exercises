"""Rich full-arc trace for Merge Intervals, mirroring solution.py.

Linear renderer: each interval is a cell labeled "start-end" (sorted by start).
Pointers mark the interval being read; marks show which run is being built (good)
vs absorbed (dim). The sidebar carries the running merged interval / output list.
Writes trace.json.
"""
import json
import os

frames = []

SORT = [
    "ordered = sorted(intervals, key=lambda iv: iv[0])",
    "merged = [ordered[0][:]]",
    "for start, end in ordered[1:]:",
    "    last = merged[-1]",
    "    if start <= last[1]:      # overlap or touch",
    "        last[1] = max(last[1], end)",
    "    else:                     # gap — previous run done",
    "        merged.append([start, end])",
]
BRUTE = [
    "for i in range(n):",
    "    for j in range(n):",
    "        if i != j and overlap(iv[i], iv[j]):",
    "            ...   # merge and rescan from scratch",
]


def add(**f):
    frames.append(f)


def lbl(iv):
    return f"{iv[0]}-{iv[1]}"


# ---------------------------------------------------------------------------
raw = [[1, 3], [2, 6], [8, 10], [15, 18]]
# unsorted-looking arc: show sort first, then sweep.

# ---- Act 0: the naive idea (compare every pair) ----
labels0 = [lbl(iv) for iv in raw]
add(act=0, cells=list(range(len(raw))), labels=labels0, code="brute", line=0,
    intro="every interval compared against every other, then rescan when two merge.",
    invariant="nothing is sorted yet, so an overlap could sit anywhere.",
    note="Naive: for each interval, scan all the others looking for an overlap. "
         "Then merge and start the whole scan over. O(n^2) and messy.",
    pointers={"i": 0, "j": 1}, marks={"0": "active", "1": "dim"},
    state=[["i", 0], ["j", 1], ["comparisons", 0]])

work = 0
for i in range(len(raw)):
    for j in range(len(raw)):
        if i == j:
            continue
        work += 1
add(act=0, cells=list(range(len(raw))), labels=labels0, code="brute", line=2,
    note=f"Just the pair scan is {work} comparisons for 4 intervals — and each real "
         "merge would force another full pass. The far-apart compares are wasted.",
    marks={str(k): "dim" for k in range(len(raw))},
    state=[["comparisons", work], ["pattern", "~ n*n per merge"]])

# ---- Act 1: the waste, and the fix (sort) ----
add(act=1, cells=list(range(len(raw))), labels=labels0,
    intro="once sorted by start, the only thing that can overlap the run you're "
          "building is the very next interval.",
    note="The waste is comparing intervals that are far apart. Sort by start and "
         "that vanishes: earlier-starting intervals are already handled.",
    marks={str(k): "dim" for k in range(len(raw))},
    state=[["idea", "sort by start"], ["then", "one left-to-right sweep"]])

ordered = sorted(raw, key=lambda iv: iv[0])
labels1 = [lbl(iv) for iv in ordered]
add(act=1, cells=list(range(len(ordered))), labels=labels1, code="sort", line=0,
    invariant="starts only increase left to right.",
    note=f"Sorted by start: {labels1}. Now a single sweep can decide extend-the-last "
         "vs start-new for each interval.",
    marks={str(k): "active" for k in range(len(ordered))},
    state=[["order", "by start"], ["sweep cost", "O(n)"]])

# ---- Act 2: the sweep (fast) ----
merged = [ordered[0][:]]


def sb():
    rows = [[lbl(iv), "kept" if k < len(merged) - 1 else "building"]
            for k, iv in enumerate(merged)]
    return {"title": "merged so far", "rows": rows}


add(act=2, cells=list(range(len(ordered))), labels=labels1, code="sort", line=1,
    intro="the running interval grows to the right; a gap seals it and opens a new one.",
    invariant="merged holds finished runs, and its last entry is still growing.",
    note=f"Start the first run as {lbl(merged[0])} and read the rest one by one.",
    pointers={"read": 0}, marks={"0": "good"}, sidebar=sb(),
    state=[["building", lbl(merged[0])], ["output size", 1]])

for idx in range(1, len(ordered)):
    start, end = ordered[idx]
    last = merged[-1]
    build_idx = idx - 1  # cell index where current run started (its first member)
    if start <= last[1]:  # overlap or touch
        old = last[1]
        last[1] = max(last[1], end)
        m = {str(k): "good" for k in range(idx)}
        m[str(idx)] = "active"
        note = (f"{lbl([start, end])} starts at {start} <= {old} (current end) — they "
                f"touch or overlap. Push the end to max({old}, {end}) = {last[1]}.")
        add(act=2, cells=list(range(len(ordered))), labels=labels1, code="sort", line=5,
            note=note, pointers={"read": idx}, marks=m, sidebar=sb(),
            state=[["reading", lbl([start, end])], ["building", lbl(last)],
                   ["output size", len(merged)]])
    else:  # gap
        m = {str(k): "good" for k in range(idx)}
        m[str(idx)] = "active"
        add(act=2, cells=list(range(len(ordered))), labels=labels1, code="sort", line=7,
            note=f"{lbl([start, end])} starts at {start} > {last[1]} — a gap. "
                 f"Seal {lbl(last)} and open a new run from {lbl([start, end])}.",
            pointers={"read": idx}, marks=m, sidebar=sb(),
            state=[["reading", lbl([start, end])], ["sealed", lbl(last)],
                   ["output size", len(merged)]])
        merged.append([start, end])

result = [lbl(iv) for iv in merged]
add(act=2, cells=list(range(len(ordered))), labels=labels1, code="sort", line=2,
    note=f"One sweep, done. Merged = {result}.",
    marks={str(k): "good" for k in range(len(ordered))}, sidebar=sb(),
    banner=f"Merged {labels1} -> {result}   (one O(n) sweep after the sort)",
    state=[["result", str(result)], ["output size", len(merged)]])

# ---- Act 3: edge case — a swallowed insider ----
edge = [[1, 10], [2, 3], [4, 5]]
eord = sorted(edge, key=lambda iv: iv[0])
elabels = [lbl(iv) for iv in eord]
emerged = [eord[0][:]]


def esb():
    return {"title": "merged so far",
            "rows": [[lbl(iv), "building"] for iv in emerged]}


add(act=3, cells=list(range(len(eord))), labels=elabels, code="sort", line=1,
    intro="max(end, ...) is why a fully-swallowed interval can't shrink the run.",
    invariant="the run's end never moves backward.",
    note=f"Edge case: {elabels}. {lbl([2,3])} and {lbl([4,5])} sit entirely inside "
         f"{lbl([1,10])}. Start the run as {lbl(emerged[0])}.",
    pointers={"read": 0}, marks={"0": "good"}, sidebar=esb(),
    state=[["building", lbl(emerged[0])]])

for idx in range(1, len(eord)):
    start, end = eord[idx]
    last = emerged[-1]
    old = last[1]
    last[1] = max(last[1], end)
    m = {str(k): "good" for k in range(idx)}
    m[str(idx)] = "active"
    add(act=3, cells=list(range(len(eord))), labels=elabels, code="sort", line=5,
        note=f"{lbl([start, end])} starts at {start} <= {old}. max({old}, {end}) = "
             f"{last[1]} — the end holds at 10, the insider is swallowed.",
        pointers={"read": idx}, marks=m, sidebar=esb(),
        state=[["reading", lbl([start, end])], ["building", lbl(last)]])

eresult = [lbl(iv) for iv in emerged]
add(act=3, cells=list(range(len(eord))), labels=elabels, code="sort", line=5,
    note=f"All three collapse into {eresult[0]}. Taking the max, not the last end, "
         "is what kept it correct.",
    marks={str(k): "good" for k in range(len(eord))}, sidebar=esb(),
    banner=f"{elabels} -> {eresult}   (swallowed insiders, one interval out)",
    state=[["result", str(eresult)]])

trace = {
    "player": "linear",
    "title": "Merge Intervals — sort by start, then one honest sweep",
    "acts": ["Naive: every pair", "The fix: sort by start",
             "Fast: one sweep", "Edge case: swallowed insiders"],
    "code": {"brute": BRUTE, "sort": SORT},
    "legend": [["active", "interval being read"], ["good", "part of a kept/merged run"],
               ["dim", "not yet ordered / far apart"]],
    "cells": list(range(len(raw))), "labels": labels0, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
