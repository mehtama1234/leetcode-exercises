"""Rich full-arc trace for Non-overlapping Intervals, mirroring solution.py.

Linear renderer: each interval is a cell labeled "start-end". Act 1 sorts by
START (the intuitive greedy); the final act sorts by END (the provably-optimal
greedy). Pointers mark the interval being read; marks show kept (good) vs removed
(bad). The state HUD carries kept_end and the running removed count.
Writes trace.json.
"""
import json
import os

frames = []

BY_START = [
    "ordered = sorted(intervals, key=lambda iv: iv[0])",
    "prev_end = ordered[0][1]; removed = 0",
    "for start, end in ordered[1:]:",
    "    if start < prev_end:           # overlap — drop one",
    "        removed += 1",
    "        prev_end = min(prev_end, end)   # keep earlier-ending",
    "    else:",
    "        prev_end = end",
]
BY_END = [
    "ordered = sorted(intervals, key=lambda iv: iv[1])",
    "kept_end = ordered[0][1]; kept = 1",
    "for start, end in ordered[1:]:",
    "    if start >= kept_end:          # fits after last kept",
    "        kept += 1",
    "        kept_end = end",
    "    # else overlaps a kept one -> removed",
    "return len(intervals) - kept",
]


def add(**f):
    frames.append(f)


def lbl(iv):
    return f"{iv[0]}-{iv[1]}"


# ---------------------------------------------------------------------------
raw = [[1, 2], [2, 3], [3, 4], [1, 3]]

# ---- Act 0: reframe — "remove fewest" == "keep most" ----
labels0 = [lbl(iv) for iv in raw]
add(act=0, cells=list(range(len(raw))), labels=labels0,
    intro="deleting the fewest is the same as keeping the most non-overlapping ones.",
    invariant="removed = total - kept, always.",
    note="Remove the fewest to make them disjoint = keep the most that don't "
         "overlap. That's the classic activity-selection problem.",
    marks={str(k): "active" for k in range(len(raw))},
    state=[["total", len(raw)], ["reframe", "keep the most"]])

# ---- Act 1: intuitive greedy — sort by START ----
so = sorted(raw, key=lambda iv: iv[0])
slabels = [lbl(iv) for iv in so]
add(act=1, cells=list(range(len(so))), labels=slabels, code="start", line=0,
    intro="on a clash, keep whichever ends earlier — it frees more of the line.",
    invariant="prev_end tracks the earliest end among what we've committed to keep.",
    note=f"Sort by start: {slabels}. Walk it; on overlap, drop one and keep the "
         "earlier-ending interval.",
    marks={"0": "good"}, state=[["prev_end", so[0][1]], ["removed", 0]])

prev_end = so[0][1]
removed = 0
kept_mask = {0: True}
for idx in range(1, len(so)):
    start, end = so[idx]
    if start < prev_end:
        removed += 1
        dropped = [start, end] if end >= prev_end else [prev_end]  # narrative only
        keep_earlier = min(prev_end, end)
        m = {str(k): ("good" if kept_mask.get(k) else "bad") for k in range(idx)}
        m[str(idx)] = "bad" if end >= prev_end else "active"
        kept_mask[idx] = end < prev_end
        note = (f"{lbl([start, end])} starts at {start} < {prev_end} (prev end) — "
                f"overlap. Keep the earlier-ending one; prev_end -> {keep_earlier}. "
                "removed +1.")
        prev_end = keep_earlier
        add(act=1, cells=list(range(len(so))), labels=slabels, code="start", line=5,
            note=note, pointers={"read": idx}, marks=m,
            state=[["reading", lbl([start, end])], ["prev_end", prev_end],
                   ["removed", removed]])
    else:
        kept_mask[idx] = True
        prev_end = end
        m = {str(k): ("good" if kept_mask.get(k) else "bad") for k in range(idx + 1)}
        add(act=1, cells=list(range(len(so))), labels=slabels, code="start", line=7,
            note=f"{lbl([start, end])} starts at {start} >= {prev_end if False else start} "
                 f"— no overlap with the last kept. Keep it; prev_end -> {end}.",
            pointers={"read": idx}, marks=m,
            state=[["reading", lbl([start, end])], ["prev_end", prev_end],
                   ["removed", removed]])
add(act=1, cells=list(range(len(so))), labels=slabels, code="start", line=4,
    note=f"removed = {removed}. Correct — but the min() bookkeeping hides WHY it's "
         "optimal. Sorting by end makes that obvious.",
    marks={str(k): ("good" if kept_mask.get(k) else "bad") for k in range(len(so))},
    state=[["removed", removed]])

# ---- Act 2: the optimal greedy — sort by END ----
eo = sorted(raw, key=lambda iv: iv[1])
elabels = [lbl(iv) for iv in eo]
add(act=2, cells=list(range(len(eo))), labels=elabels, code="end", line=0,
    intro="always take the earliest-finishing interval — it leaves the most room.",
    invariant="kept_end is the end of the last interval we committed to keep.",
    note=f"Sort by END: {elabels}. Greedily keep each interval that starts at or "
         "after the last kept one's end.",
    marks={"0": "good"}, state=[["kept_end", eo[0][1]], ["kept", 1]])

kept_end = eo[0][1]
kept = 1
keptmask = {0: True}
for idx in range(1, len(eo)):
    start, end = eo[idx]
    if start >= kept_end:
        kept += 1
        keptmask[idx] = True
        m = {str(k): ("good" if keptmask.get(k) else "bad") for k in range(idx)}
        m[str(idx)] = "good"
        note = (f"{lbl([start, end])} starts at {start} >= {kept_end} (kept_end) — "
                f"it fits. Keep it; kept_end -> {end}.")
        kept_end = end
        add(act=2, cells=list(range(len(eo))), labels=elabels, code="end", line=5,
            note=note, pointers={"read": idx}, marks=m,
            state=[["reading", lbl([start, end])], ["kept_end", kept_end],
                   ["kept", kept]])
    else:
        keptmask[idx] = False
        m = {str(k): ("good" if keptmask.get(k) else "bad") for k in range(idx)}
        m[str(idx)] = "bad"
        add(act=2, cells=list(range(len(eo))), labels=elabels, code="end", line=6,
            note=f"{lbl([start, end])} starts at {start} < {kept_end} (kept_end) — it "
                 "overlaps a kept interval. Remove it.",
            pointers={"read": idx}, marks=m,
            state=[["reading", lbl([start, end])], ["kept_end", kept_end],
                   ["kept", kept]])

ans = len(raw) - kept
add(act=2, cells=list(range(len(eo))), labels=elabels, code="end", line=7,
    note=f"Kept {kept}, so removed = {len(raw)} - {kept} = {ans}. Earliest-finish is "
         "provably optimal (an exchange argument).",
    marks={str(k): ("good" if keptmask.get(k) else "bad") for k in range(len(eo))},
    banner=f"{elabels}: remove {ans}   (kept {kept} of {len(raw)}, sorted by end)",
    state=[["kept", kept], ["removed", ans]])

# ---- Act 3: edge — three identical intervals ----
edge = [[1, 2], [1, 2], [1, 2]]
eeo = sorted(edge, key=lambda iv: iv[1])
eel = [lbl(iv) for iv in eeo]
add(act=3, cells=[0, 1, 2], labels=eel, code="end", line=1,
    intro="duplicates all overlap — keep one, remove the rest.",
    invariant="an interval is kept only if it starts at or after kept_end.",
    note=f"Edge case: {eel}. All three are the same 1-2. Keep the first.",
    marks={"0": "good"}, state=[["kept_end", 2], ["kept", 1]])
ekept = 1
for idx in range(1, 3):
    m = {"0": "good"}
    for k in range(1, idx):
        m[str(k)] = "bad"
    m[str(idx)] = "bad"
    add(act=3, cells=[0, 1, 2], labels=eel, code="end", line=6,
        note=f"1-2 starts at 1 < 2 (kept_end) — overlaps the kept one. Remove it.",
        pointers={"read": idx}, marks=m,
        state=[["reading", "1-2"], ["kept_end", 2], ["kept", 1]])
add(act=3, cells=[0, 1, 2], labels=eel, code="end", line=7,
    note="Kept 1 of 3, so remove 2.",
    marks={"0": "good", "1": "bad", "2": "bad"},
    banner="1-2, 1-2, 1-2: remove 2   (keep one duplicate)",
    state=[["kept", 1], ["removed", 2]])

trace = {
    "player": "linear",
    "title": "Non-overlapping Intervals — keep the most, sort by end",
    "acts": ["Reframe: keep the most", "Intuitive greedy: sort by start",
             "Optimal greedy: sort by end", "Edge case: duplicates"],
    "code": {"start": BY_START, "end": BY_END},
    "legend": [["active", "interval being read"], ["good", "kept"],
               ["bad", "removed"], ["dim", "inactive"]],
    "cells": list(range(len(raw))), "labels": labels0, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
