"""Rich full-arc trace for Insert Interval, mirroring solution.py.

Linear renderer: each existing interval is a cell labeled "start-end" (already
sorted, disjoint). Pointers mark the interval being read; marks show the three
phases — before (dim), overlapping/absorbed (active/bad), after (good). The
sidebar carries the growing new interval and the output list.
Writes trace.json.
"""
import json
import os

frames = []

FAST = [
    "start, end = new_interval",
    "while i < n and intervals[i][1] < start:   # before",
    "    result.append(intervals[i]); i += 1",
    "while i < n and intervals[i][0] <= end:     # overlap",
    "    start = min(start, intervals[i][0])",
    "    end   = max(end,   intervals[i][1])",
    "    i += 1",
    "result.append([start, end])",
    "while i < n:                                # after",
    "    result.append(intervals[i]); i += 1",
]


def add(**f):
    frames.append(f)


def lbl(iv):
    return f"{iv[0]}-{iv[1]}"


def run(act, intervals, new, intro=None, invariant=None, head=None,
        final_banner=None):
    labels = [lbl(iv) for iv in intervals]
    n = len(intervals)
    cells = list(range(n))
    start, end = new[0], new[1]
    result = []

    def sb(phase):
        rows = [["new", lbl([start, end])], ["phase", phase]]
        rows += [["out", lbl(iv)] for iv in result]
        return {"title": "building", "rows": rows}

    first = True

    def mk(**kw):
        nonlocal first
        base = dict(act=act, cells=cells, labels=labels)
        if first:
            if intro:
                base["intro"] = intro
            if invariant:
                base["invariant"] = invariant
            first = False
        base.update(kw)
        add(**base)

    mk(code="fast", line=0,
       note=head or f"Insert {lbl(new)} into {labels}. The list is already sorted and "
                    "disjoint, so one left-to-right pass in three phases does it.",
       marks={str(k): "dim" for k in range(n)}, sidebar=sb("start"),
       state=[["new", lbl([start, end])], ["i", 0]])

    i = 0
    # Phase 1: before
    while i < n and intervals[i][1] < start:
        m = {str(k): "good" for k in range(i)}
        m[str(i)] = "dim"
        result.append(intervals[i])
        mk(code="fast", line=2, pointers={"i": i}, marks=m, sidebar=sb("before"),
           note=f"{lbl(intervals[i])} ends at {intervals[i][1]} < {start} (new start) "
                "— it can't touch the new one. Copy it straight through.",
           state=[["i", i], ["ends", intervals[i][1]], ["< new start", start]])
        i += 1

    # Phase 2: overlap
    absorbed = False
    while i < n and intervals[i][0] <= end:
        absorbed = True
        os_, oe = start, end
        start = min(start, intervals[i][0])
        end = max(end, intervals[i][1])
        m = {str(k): "good" for k in range(i)}
        m[str(i)] = "active"
        mk(code="fast", line=5, pointers={"i": i}, marks=m, sidebar=sb("overlap"),
           note=f"{lbl(intervals[i])} starts at {intervals[i][0]} <= {oe} (new end) "
                f"— overlap. Widen new to {lbl([start, end])}.",
           state=[["absorbing", lbl(intervals[i])], ["new", lbl([start, end])]])
        i += 1
    result.append([start, end])
    m = {str(k): "good" for k in range(i)}
    mk(code="fast", line=7, marks=m, sidebar=sb("placed"),
       note=(f"No more overlaps. Drop the widened {lbl([start, end])} into place."
             if absorbed else
             f"Nothing overlapped. Drop {lbl([start, end])} into place."),
       state=[["placed", lbl([start, end])], ["i", i]])

    # Phase 3: after
    while i < n:
        result.append(intervals[i])
        m = {str(k): "good" for k in range(i + 1)}
        mk(code="fast", line=9, pointers={"i": i}, marks=m, sidebar=sb("after"),
           note=f"{lbl(intervals[i])} starts after the merged interval ends — copy "
                "the rest straight through.",
           state=[["i", i], ["copying", lbl(intervals[i])]])
        i += 1

    res = [lbl(iv) for iv in result]
    mk(code="fast", line=7, marks={str(k): "good" for k in range(n)},
       sidebar=sb("done"), banner=final_banner or f"{labels} + {lbl(new)} -> {res}",
       note=f"Result stays sorted and merged: {res}.",
       state=[["result", str(res)]])


# ---- Act 0: absorb a middle run ----
run(0, [[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8],
    intro="watch the new interval GROW as it swallows every one it overlaps.",
    invariant="everything left of i is already settled in result.",
    head="Insert 4-8. Phase 1 copies what ends before 4; phase 2 absorbs "
         "everything it overlaps; phase 3 copies the rest.")

# ---- Act 1: goes before everything ----
run(1, [[3, 5], [7, 9]], [1, 2],
    intro="phase 2 fires immediately; phases 1 and 3 do the copying.",
    head="Insert 1-2 into 3-5, 7-9. It ends before anything starts, so it just "
         "leads the list.")

# ---- Act 2: swallowed by an existing interval ----
run(2, [[1, 5]], [2, 3],
    intro="a new interval INSIDE an existing one adds nothing — max/min keep 1-5.",
    invariant="min(start) and max(end) never shrink the covering interval.",
    head="Insert 2-3 into 1-5. 1-5 starts at 1 <= 3, so it's absorbed; min/max "
         "leave 1-5 unchanged.",
    final_banner="1-5 + 2-3 -> 1-5   (new interval swallowed)")

trace = {
    "player": "linear",
    "title": "Insert Interval — before, absorb, after in one pass",
    "acts": ["Absorb a run", "Goes before everything", "Swallowed by an existing one"],
    "code": {"fast": FAST},
    "legend": [["active", "overlapping — being absorbed"], ["good", "settled in output"],
               ["dim", "copied through (before the new one)"]],
    "cells": [0, 1, 2, 3, 4],
    "labels": ["1-2", "3-5", "6-7", "8-10", "12-16"], "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
