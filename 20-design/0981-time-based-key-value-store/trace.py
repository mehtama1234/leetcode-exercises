"""Rich full-arc trace for Time Based Key-Value Store (linear renderer).
Design + search problem, so the arc is: the naive back-scan (O(n)) -> binary
search for the floor timestamp (O(log n)) -> an edge (query before any value).
The key's timestamp history is the linear `cells` row; the parallel values live
in a `sidebar`. Mirrors bisect_right(ts, t) then take index i-1. Writes trace.json.
"""
import json
import os
from bisect import bisect_right

frames = []

NAIVE = [
    "# get(key, t): scan history backward",
    "for i in range(len(ts) - 1, -1, -1):",
    "    if ts[i] <= t:",
    "        return values[i]",
    "return ''",
]
FAST = [
    "# times are already sorted (set() increases t)",
    "i = bisect_right(ts, t)   # first ts strictly > t",
    "if i == 0: return ''      # everything is later",
    "return values[i - 1]      # the floor: largest ts <= t",
]


def add(**f):
    frames.append(f)


# History for key "k": v1@10, v2@20, v3@30 (matches solution's 2nd test).
ts = [10, 20, 30]
vals = ["v1", "v2", "v3"]


def sidebar(hi=None):
    rows = []
    for i, (t, v) in enumerate(zip(ts, vals)):
        mark = " <-" if i == hi else ""
        rows.append([f"t={t}", v + mark])
    return {"title": "values[key] (by time)", "rows": rows}


def cells_labels():
    return list(ts), list(ts)  # show timestamps as both value and label


# ---- Act 0: naive backward scan ----
c, lb = cells_labels()
work = 0
add(act=0, cells=c, labels=lb, code="naive", line=0,
    intro="how many entries the naive scan walks to answer one get — the work we delete.",
    invariant="the history is stored in time order (set() timestamps only grow).",
    note="get('k', 25): find the value in effect at time 25 — the one set at the "
    "largest timestamp <= 25. Naive: scan history from newest back.",
    pointers={"t?": 2}, marks={"2": "active"},
    state=[["query t", 25], ["history", "10,20,30"], ["compares", 0]])
# scan backward from index 2
for i in range(len(ts) - 1, -1, -1):
    work += 1
    hit = ts[i] <= 25
    add(act=0, code="naive", line=2, sidebar=sidebar(i if hit else None),
        note=f"ts[{i}] = {ts[i]}. Is {ts[i]} <= 25? " + ("Yes — this is the floor." if hit
             else "No, too new — keep going back."),
        pointers={"i": i}, marks={str(i): "good" if hit else "bad"},
        state=[["i", i], [f"ts[{i}]", ts[i]], ["compares", work]])
    if hit:
        ans_i = i
        break
add(act=0, code="naive", line=3,
    note=f"Answer: values[{ans_i}] = '{vals[ans_i]}'. It cost {work} steps here; on a long "
    f"history a far-back query walks the whole list — O(n).",
    pointers={"i": ans_i}, marks={str(ans_i): "good"}, sidebar=sidebar(ans_i),
    state=[["answer", vals[ans_i]], ["compares", work]])

# ---- Act 1: binary search for the floor ----
add(act=1, cells=c, labels=lb, code="fast", line=0,
    intro="the history is SORTED, so we jump to the boundary instead of walking to it.",
    invariant="bisect_right returns the first index with ts strictly greater than t.",
    note="Same get('k', 25). Timestamps are already sorted, so binary-search the "
    "boundary: the first timestamp strictly greater than 25.",
    pointers={"t?": 2}, marks={"0": "dim", "1": "dim", "2": "dim"}, sidebar=sidebar(),
    state=[["query t", 25], ["method", "bisect_right"]])
i = bisect_right(ts, 25)  # -> 2 (first ts > 25 is 30 at index 2)
add(act=1, code="fast", line=1,
    note=f"bisect_right(ts, 25) = {i}: index of the first timestamp (>{25}). "
    f"ts[{i}] = {ts[i]} is the first one too new.",
    pointers={"i": i}, marks={str(i): "bad"}, sidebar=sidebar(),
    state=[["i (bisect)", i], ["ts[i]", ts[i]]])
add(act=1, code="fast", line=3,
    note=f"The entry just before it, index {i-1}, is the floor: ts[{i-1}] = {ts[i-1]} <= 25. "
    f"Return values[{i-1}] = '{vals[i-1]}' in O(log n) — no scan.",
    pointers={"floor": i - 1}, marks={str(i - 1): "good", str(i): "dim"},
    sidebar=sidebar(i - 1),
    state=[["floor idx", i - 1], ["answer", vals[i - 1]]],
    banner=f"get('k', 25) = '{vals[i-1]}'  (largest timestamp <= 25 is {ts[i-1]})")
# exact hit example
i2 = bisect_right(ts, 20)  # -> 2, floor index 1 -> v2
add(act=1, code="fast", line=3,
    note=f"Exact hit: get('k', 20). bisect_right lands past the equal timestamp, so "
    f"index {i2-1} = ts {ts[i2-1]} is returned: '{vals[i2-1]}'.",
    pointers={"floor": i2 - 1}, marks={str(i2 - 1): "good"}, sidebar=sidebar(i2 - 1),
    state=[["get('k',20)", vals[i2 - 1]]])

# ---- Act 2: edge — query before any value ----
add(act=2, cells=c, labels=lb, code="fast", line=2,
    intro="if every stored time is later than t, bisect returns 0 and there is no floor.",
    invariant="i == 0 means no timestamp is <= t, so the answer is the empty string.",
    note="Edge: get('k', 9), before the first set at t=10.",
    pointers={"t?": 0}, marks={"0": "dim", "1": "dim", "2": "dim"}, sidebar=sidebar(),
    state=[["query t", 9]])
i3 = bisect_right(ts, 9)  # -> 0
add(act=2, code="fast", line=2,
    note=f"bisect_right(ts, 9) = {i3}. i == 0 means every stored timestamp is later "
    f"than 9 — nothing was in effect yet. Return ''.",
    pointers={"i": 0}, marks={"0": "bad"}, sidebar=sidebar(),
    state=[["i", i3], ["answer", '""']],
    banner="get('k', 9) = ''  (no timestamp <= 9)")
add(act=2, code="fast", line=2,
    note="A missing key behaves the same: no history, so ''. set() is O(1) (just "
    "append); get() is O(log n) binary search.",
    marks={"0": "dim", "1": "dim", "2": "dim"},
    state=[["set", "O(1) append"], ["get", "O(log n)"]])

trace = {
    "player": "linear",
    "title": "Time Based Key-Value Store - binary-search the floor timestamp",
    "acts": ["Naive: scan history back", "Binary search the floor", "Edge: before any value"],
    "code": {"naive": NAIVE, "fast": FAST},
    "legend": [["active", "timestamp we're testing"], ["good", "the floor / answer"],
               ["bad", "too new / no floor"], ["dim", "not in play"]],
    "cells": ts, "labels": ts, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
