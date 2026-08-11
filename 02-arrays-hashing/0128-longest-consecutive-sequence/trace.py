"""Full-arc trace for Longest Consecutive Sequence, mirroring solution.py: the
sort-then-scan baseline and the O(n) hash-set scan that only starts counting at a
run's true beginning (x with x-1 absent). Linear renderer: nums as cells, a
`present` set in the sidebar, marks tracing each run. A "walk steps" counter
shows why skipping non-starts keeps it linear. Writes trace.json.
"""
import json
import os

nums = [100, 4, 200, 1, 3, 2]
# longest run: 1,2,3,4 -> length 4
frames = []

SORT = [
    "ordered = sorted(set(nums))",
    "best = current = 1",
    "for i in range(1, len(ordered)):",
    "    if ordered[i] == ordered[i-1] + 1:",
    "        current += 1; best = max(best, current)",
    "    else:",
    "        current = 1",
]
FAST = [
    "present = set(nums)",
    "for x in present:",
    "    if x - 1 in present:",
    "        continue            # not a run start",
    "    length = 1; y = x",
    "    while y + 1 in present:",
    "        y += 1; length += 1",
    "    best = max(best, length)",
]


def add(**f):
    frames.append(f)


# ---- Act 0: sort baseline ----
ordered = sorted(set(nums))
add(act=0, cells=nums, code="sort", line=0,
    intro="once sorted, consecutive integers sit next to each other, so one walk counts runs.",
    invariant="best is the longest +1 run seen in the sorted prefix so far.",
    note="Baseline: sort, then scan for the longest ascending run of +1 steps. Correct, but the sort is n log n.",
    marks={str(i): "dim" for i in range(len(nums))},
    state=[["nums", str(nums)]])
add(act=0, cells=ordered, labels=list(range(len(ordered))), code="sort", line=2,
    note=f"sorted+deduped = {ordered}. Now walk it, extending the run on each +1 step.",
    marks={str(i): "active" for i in range(len(ordered))},
    state=[["ordered", str(ordered)]])
best = current = 1
for i in range(1, len(ordered)):
    step = ordered[i] == ordered[i - 1] + 1
    if step:
        current += 1
        best = max(best, current)
    else:
        current = 1
    add(act=0, code="sort", line=4 if step else 6,
        note=f"{ordered[i - 1]} -> {ordered[i]}: "
             + (f"consecutive, run = {current}." if step else "break, run resets to 1."),
        pointers={"i": i}, marks={str(i): "good" if step else "bad", str(i - 1): "dim"},
        state=[["ordered[i]", ordered[i]], ["current run", current], ["best", best]])
add(act=0, code="sort", line=4,
    note=f"Longest run is {best} (the 1,2,3,4). Right answer — but sorting cost n log n, and the problem wants O(n).",
    banner=f"best = {best} — but we paid a sort we don't need",
    state=[["best", best], ["cost", "O(n log n)"]])

# ---- Act 1: the insight ----
add(act=1,
    intro="a set gives O(1) 'is x+1 here?', so we can walk a run without sorting — if we start at the right end.",
    note="Put everything in a set. To avoid re-walking a run from its middle, only START counting where a run "
         "begins: x is a start exactly when x-1 is NOT in the set.",
    state=[["idea", "set + start-only walk"], ["start test", "x-1 absent"]])
add(act=1,
    note="Because each run is walked forward exactly once (from its start), total steps ~ number of elements. "
         "That is the O(n).",
    state=[["walks per run", 1], ["target", "O(n)"]])

# ---- Act 2: hash set scan ----
present = set(nums)
# deterministic order for the animation
order = sorted(present)
idx_of = {v: nums.index(v) for v in present}
best = 0
steps = 0


def sidebar():
    return {"title": "present (set)", "rows": [[str(v), "in"] for v in sorted(present)]}


add(act=2, cells=nums, code="fast", line=0,
    intro="values whose predecessor is present are skipped — only true starts trigger a walk.",
    invariant="best is the longest run whose start we have already processed.",
    note="All values in a set. Visit each; skip any that is inside a run; walk forward from each start.",
    sidebar=sidebar(), marks={str(i): "dim" for i in range(len(nums))},
    state=[["best", 0], ["walk steps", 0]])
for x in order:
    xi = idx_of[x]
    if x - 1 in present:
        add(act=2, code="fast", line=3,
            note=f"{x}: {x - 1} is in the set, so {x} is in the middle of a run — skip it.",
            marks={str(xi): "bad"}, sidebar=sidebar(),
            state=[["x", x], ["x-1 present?", "yes"], ["action", "skip"]])
        continue
    # x is a run start
    length = 1
    y = x
    run_idxs = [xi]
    add(act=2, code="fast", line=4,
        note=f"{x}: {x - 1} is absent, so {x} STARTS a run. Walk forward while y+1 is present.",
        marks={str(xi): "active"}, sidebar=sidebar(),
        state=[["start", x], ["length", 1]])
    while y + 1 in present:
        y += 1
        length += 1
        steps += 1
        yi = idx_of[y]
        run_idxs.append(yi)
        add(act=2, code="fast", line=6,
            note=f"{y} is present -> extend. Run is now {x}..{y}, length {length}.",
            marks={str(k): "good" for k in run_idxs} | {str(yi): "active"}, sidebar=sidebar(),
            state=[["run", f"{x}..{y}"], ["length", length], ["walk steps", steps]])
    best = max(best, length)
    add(act=2, code="fast", line=7,
        note=f"Run {x}..{y} ended at length {length}. best = {best}.",
        marks={str(k): "good" for k in run_idxs}, sidebar=sidebar(),
        state=[["run length", length], ["best", best], ["walk steps", steps]])
add(act=2, code="fast", line=7,
    note=f"Longest run = {best} (1,2,3,4), found in {steps} total walk steps — each run walked once.",
    marks={str(idx_of[v]): "good" for v in [1, 2, 3, 4]},
    banner=f"best = {best} in one linear pass — no sort",
    state=[["best", best], ["walk steps", steps]])

# ---- Act 3: edge case, duplicates + isolated value ----
edge = [1, 2, 0, 1]
# longest run 0,1,2 -> length 3; duplicate 1 must not inflate it
present = set(edge)
order = sorted(present)
idx_of = {v: edge.index(v) for v in present}
best = 0


def sidebar_e():
    return {"title": "present (set) — dupes collapse", "rows": [[str(v), "in"] for v in sorted(present)]}


add(act=3, cells=edge, code="fast", line=0,
    intro="the duplicate 1 collapses in the set, so it cannot pad the run length.",
    invariant="the set holds distinct values, so a repeat is walked at most once.",
    note="Edge case: [1, 2, 0, 1]. Two 1's, but the set keeps one. Longest run is 0,1,2 = 3, not 4.",
    sidebar=sidebar_e(), marks={"3": "dim"},
    state=[["edge", str(edge)], ["set", str(sorted(present))]])
for x in order:
    xi = idx_of[x]
    if x - 1 in present:
        add(act=3, code="fast", line=3,
            note=f"{x}: {x - 1} present, so not a start — skip.",
            marks={str(xi): "bad"}, sidebar=sidebar_e(),
            state=[["x", x], ["action", "skip"]])
        continue
    length = 1
    y = x
    run_idxs = [xi]
    while y + 1 in present:
        y += 1
        length += 1
        run_idxs.append(idx_of[y])
    best = max(best, length)
    add(act=3, code="fast", line=7,
        note=f"Start {x}: run {x}..{y}, length {length}. best = {best}.",
        marks={str(k): "good" for k in run_idxs}, sidebar=sidebar_e(),
        state=[["run", f"{x}..{y}"], ["length", length], ["best", best]])
add(act=3, code="fast", line=7,
    note=f"best = {best}. The duplicate 1 did not inflate the run — the set saw it once.",
    marks={str(idx_of[v]): "good" for v in [0, 1, 2]},
    banner=f"best = {best} — duplicates collapse in the set",
    state=[["best", best]])

trace = {
    "player": "linear",
    "title": "Longest Consecutive Sequence — walk each run once, from its start",
    "acts": ["Baseline: sort + scan", "The insight", "Fast: set, start-only walk", "Edge case: duplicates"],
    "code": {"sort": SORT, "fast": FAST},
    "legend": [["active", "current value / walking"], ["good", "part of a counted run"], ["bad", "skipped (not a start)"], ["dim", "inactive"]],
    "cells": nums, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
