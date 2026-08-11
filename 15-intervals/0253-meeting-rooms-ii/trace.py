"""Rich full-arc trace for Meeting Rooms II (minimum rooms), mirroring solution.py.

Linear renderer: meetings shown as cells labeled "start-end" (sorted by start).
The sweep-line act walks split start/end events; the running room count and its
peak live in the state HUD (the answer is the peak concurrency). The heap act
shows the min-heap of busy-room end times in the sidebar.
Writes trace.json.
"""
import json
import os
import heapq

frames = []

SWEEP = [
    "starts = sorted(iv[0] for iv in intervals)",
    "ends   = sorted(iv[1] for iv in intervals)",
    "rooms = peak = 0; i = j = 0",
    "while i < n:",
    "    if starts[i] < ends[j]:   # a meeting begins",
    "        rooms += 1; peak = max(peak, rooms); i += 1",
    "    else:                     # a meeting frees a room",
    "        rooms -= 1; j += 1",
    "return peak",
]
HEAP = [
    "ordered = sorted(intervals, key=lambda iv: iv[0])",
    "ends = []                       # min-heap of busy end times",
    "for start, end in ordered:",
    "    if ends and ends[0] <= start:   # a room is free — reuse",
    "        heapq.heapreplace(ends, end)",
    "    else:                           # all busy — open a room",
    "        heapq.heappush(ends, end)",
    "return len(ends)",
]


def add(**f):
    frames.append(f)


def lbl(iv):
    return f"{iv[0]}-{iv[1]}"


# ---------------------------------------------------------------------------
raw = [[0, 30], [5, 10], [15, 20]]
ordered = sorted(raw, key=lambda iv: iv[0])
labels = [lbl(iv) for iv in ordered]
cells = list(range(len(ordered)))

# ---- Act 0: the question ----
add(act=0, cells=cells, labels=labels,
    intro="the answer is the most meetings live at the same instant, no more.",
    invariant="a room is needed only while a meeting is actually running.",
    note="Minimum rooms = peak concurrency. Forget which room is which; just count "
         "how many meetings are running at once, and take the high-water mark.",
    marks={str(k): "active" for k in range(len(ordered))},
    state=[["meetings", len(ordered)], ["want", "peak overlap"]])

# ---- Act 1: sweep line over split events ----
starts = sorted(iv[0] for iv in raw)
ends = sorted(iv[1] for iv in raw)
n = len(raw)

# precompute a timeline of events to narrate
events = []
i = j = 0
rooms = peak = 0
while i < n:
    if starts[i] < ends[j]:
        events.append(("start", starts[i]))
        i += 1
    else:
        events.append(("end", ends[j]))
        j += 1
while j < n:
    events.append(("end", ends[j]))
    j += 1

add(act=1, cells=cells, labels=labels, code="sweep", line=0,
    intro="each meeting becomes a +1 start event and a -1 end event on a timeline.",
    invariant="rooms = starts seen so far minus ends seen so far.",
    note=f"Split into sorted starts {starts} and ends {ends}. Sweep both, ends "
         "before starts on a tie so a freed room can be reused.",
    marks={str(k): "dim" for k in range(len(ordered))},
    state=[["starts", str(starts)], ["ends", str(ends)], ["rooms", 0], ["peak", 0]])

rooms = peak = 0
for kind, t in events:
    if kind == "start":
        rooms += 1
        peak = max(peak, rooms)
        # mark cells whose interval is live at time t
        m = {str(k): ("bad" if ordered[k][0] <= t < ordered[k][1] else "dim")
             for k in range(len(ordered))}
        add(act=1, cells=cells, labels=labels, code="sweep", line=5,
            note=f"A meeting begins at t={t}. rooms -> {rooms}. "
                 + (f"New peak {peak}." if rooms == peak else f"Peak still {peak}."),
            marks=m, state=[["event", f"start @ {t}"], ["rooms", rooms], ["peak", peak]])
    else:
        rooms -= 1
        m = {str(k): ("bad" if ordered[k][0] <= t < ordered[k][1] else "dim")
             for k in range(len(ordered))}
        add(act=1, cells=cells, labels=labels, code="sweep", line=7,
            note=f"A meeting ends at t={t}. A room frees up. rooms -> {rooms}.",
            marks=m, state=[["event", f"end @ {t}"], ["rooms", rooms], ["peak", peak]])

add(act=1, cells=cells, labels=labels, code="sweep", line=8,
    note=f"Highest the room count ever reached was {peak}. That is the answer.",
    marks={str(k): "good" for k in range(len(ordered))},
    banner=f"{labels}: minimum rooms = {peak}   (peak concurrency)",
    state=[["answer", peak]])

# ---- Act 2: heap view (rooms are real, reuse when free) ----
heap = []


def sb():
    return {"title": "busy rooms (end times, min-heap)",
            "rows": [[str(x), "in use"] for x in sorted(heap)]}


add(act=2, cells=cells, labels=labels, code="heap", line=1,
    intro="the heap holds end times of busy rooms; its size never exceeds the peak.",
    invariant="heap size = rooms currently in use.",
    note="Same answer, rooms made concrete: a min-heap of end times. Reuse the "
         "earliest-freeing room when it's done, else open a new one.",
    marks={str(k): "dim" for k in range(len(ordered))}, sidebar=sb(),
    state=[["rooms in use", 0]])

for idx, (start, end) in enumerate(ordered):
    if heap and heap[0] <= start:
        freed = heapq.heapreplace(heap, end)
        m = {str(k): "good" for k in range(idx)}
        m[str(idx)] = "active"
        add(act=2, cells=cells, labels=labels, code="heap", line=4,
            note=f"{lbl([start, end])}: earliest room freed at {freed} <= {start} — "
                 "reuse it. No new room.",
            pointers={"read": idx}, marks=m, sidebar=sb(),
            state=[["reused room freeing at", freed], ["rooms in use", len(heap)]])
    else:
        heapq.heappush(heap, end)
        m = {str(k): "good" for k in range(idx)}
        m[str(idx)] = "active"
        top = min(heap) if len(heap) > 1 else None
        note = (f"{lbl([start, end])}: no room free by {start}" +
                (f" (earliest frees at {top})" if top is not None else "") +
                " — open a new room.")
        add(act=2, cells=cells, labels=labels, code="heap", line=6,
            note=note, pointers={"read": idx}, marks=m, sidebar=sb(),
            state=[["opened room", "yes"], ["rooms in use", len(heap)]])

add(act=2, cells=cells, labels=labels, code="heap", line=7,
    note=f"The heap peaked at {len(heap)} busy rooms — same {peak} the sweep found.",
    marks={str(k): "good" for k in range(len(ordered))}, sidebar=sb(),
    banner=f"heap agrees: minimum rooms = {len(heap)}",
    state=[["answer", len(heap)]])

# ---- Act 3: edge — back-to-back reuse one room ----
edge = [[1, 5], [5, 10]]
eord = sorted(edge, key=lambda iv: iv[0])
elabels = [lbl(iv) for iv in eord]
add(act=3, cells=[0, 1], labels=elabels, code="heap", line=3,
    intro="one ending exactly when the next begins shares a single room.",
    invariant="reuse fires when the earliest end <= the new start (<= , not <).",
    note=f"Edge case: {elabels}. The first frees its room at 5; the second starts "
         "at 5.",
    marks={"0": "good"}, sidebar={"title": "busy rooms", "rows": [["5", "in use"]]},
    state=[["rooms in use", 1]])
add(act=3, cells=[0, 1], labels=elabels, code="heap", line=4,
    note="5-10 starts at 5, the room frees at 5 (<=) — reuse it. Never two rooms.",
    pointers={"read": 1}, marks={"0": "good", "1": "active"},
    sidebar={"title": "busy rooms", "rows": [["10", "in use"]]},
    banner="1-5, 5-10: minimum rooms = 1   (back-to-back reuse)",
    state=[["answer", 1]])

trace = {
    "player": "linear",
    "title": "Meeting Rooms II — rooms = peak overlap",
    "acts": ["The question: peak overlap", "Fast: sweep line",
             "Heap view: reuse rooms", "Edge case: back-to-back"],
    "code": {"sweep": SWEEP, "heap": HEAP},
    "legend": [["active", "meeting being placed"], ["good", "resolved / answer"],
               ["bad", "live at this instant (counts toward rooms)"], ["dim", "not live"]],
    "cells": cells, "labels": labels, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
