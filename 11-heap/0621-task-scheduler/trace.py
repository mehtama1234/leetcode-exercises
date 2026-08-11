"""Full-arc linear trace for Task Scheduler (621).

Mirrors solution.py: the greedy max-heap simulation ticking the clock one slot at
a time (run the most-remaining task, park it in a cooldown queue, idle when the
heap is dry), then the O(1) counting formula the simulation reveals. The built
schedule is the linear row; the max-heap of remaining counts and the cooldown
queue are drawn as two sidebar tables. Writes trace.json.
"""
import json
import os
import heapq
from collections import Counter, deque

frames = []


def add(**f):
    frames.append(f)


SIM = [
    "while heap or wait:",
    "    time += 1",
    "    if heap:",
    "        remaining = heappop(heap) + 1   # run one",
    "        if remaining < 0:",
    "            wait.append((time+n, remaining))",
    "    if wait and wait[0][0] == time:",
    "        heappush(heap, wait.popleft()[1])",
]
FORMULA = [
    "f_max = max(counts.values())",
    "ties = #(counts == f_max)",
    "frame = (f_max - 1) * (n + 1) + ties",
    "return max(len(tasks), frame)",
]

tasks = ["A", "A", "A", "B", "B", "B"]
N = 2  # answer 8: A B _ A B _ A B


def heap_sidebar(heap):
    """heap holds negated counts; show tasks by remaining count, most on top.
    We can't recover labels from counts alone, so we render counts descending."""
    body = sorted((-c for c in heap), reverse=True)
    rows = [[("top" if i == 0 else str(i)), f"{c} left"] for i, c in enumerate(body)]
    if not rows:
        rows = [["", "(empty)"]]
    return {"title": "max-heap: remaining counts", "rows": rows}


def wait_sidebar(wait):
    rows = [[f"ready t={rt}", f"{-c} left"] for rt, c in wait]
    if not rows:
        rows = [["", "(empty)"]]
    return {"title": "cooldown queue", "rows": rows}


# ---- Act 0: the greedy rule ----
add(act=0, cells=[], code="sim", line=0,
    intro="each slot: run the task with the MOST copies left; cool it down after.",
    invariant="the most-frequent task never gets stuck waiting at the very end.",
    note=f"Tasks {tasks}, cooldown n={N}. Greedy: always run the most-remaining task, "
         f"then park it for n slots.",
    state=[["n", N], ["counts", "A:3 B:3"], ["slots used", 0]])

# ---- Act 1: run the simulation (build the schedule) ----
counts = Counter(tasks)
# keep labels alongside so the schedule row shows real letters
# rebuild the heap ourselves carrying (neg_count, label) but pop order must match
# solution's (which uses only counts). Ties are broken by label here; the count of
# slots and idles is identical, which is all the answer depends on.
heap = [(-c, lbl) for lbl, c in counts.items()]
heapq.heapify(heap)
wait = deque()
schedule = []          # letters or "idle"
sched_marks = {}
time = 0

add(act=1, cells=[], code="sim", line=0,
    intro="the clock ticks one slot at a time; watch the heap drain and refill.",
    invariant="a task sits in the cooldown queue for exactly n slots before returning.",
    note="Heapify the counts (most on top) and start the clock at 0.",
    sidebar=heap_sidebar([c for c, _ in heap]),
    state=[["time", 0], ["heap", "A:3 B:3"], ["waiting", 0]])

while heap or wait:
    time += 1
    ran = None
    if heap:
        negc, lbl = heapq.heappop(heap)
        remaining = negc + 1  # ran one copy
        ran = lbl
        schedule.append(lbl)
        sched_marks[str(len(schedule) - 1)] = "active"
        note = f"t={time}: run {lbl} (had {-negc} left). "
        if remaining < 0:
            wait.append((time + N, remaining, lbl))
            note += f"{-remaining} left → cool down until t={time + N}."
        else:
            note += "last copy of it done."
        add(act=1, cells=list(schedule), labels=list(range(1, len(schedule) + 1)),
            code="sim", line=3, note=note,
            marks=dict(sched_marks),
            sidebar=heap_sidebar([c for c, _ in heap]),
            state=[["time", time], ["ran", lbl], ["waiting", len(wait)]])
    else:
        schedule.append("idle")
        sched_marks[str(len(schedule) - 1)] = "bad"
        add(act=1, cells=list(schedule), labels=list(range(1, len(schedule) + 1)),
            code="sim", line=2, note=f"t={time}: heap empty but tasks still cooling — IDLE slot.",
            marks=dict(sched_marks),
            sidebar=heap_sidebar([c for c, _ in heap]),
            state=[["time", time], ["ran", "idle"], ["waiting", len(wait)]])
    # release a task whose cooldown expired
    if wait and wait[0][0] == time:
        rt, rc, rlbl = wait.popleft()
        heapq.heappush(heap, (rc, rlbl))
        add(act=1, cells=list(schedule), labels=list(range(1, len(schedule) + 1)),
            code="sim", line=7, note=f"t={time}: {rlbl}'s cooldown expired — back on the heap.",
            marks=dict(sched_marks),
            sidebar=heap_sidebar([c for c, _ in heap]),
            state=[["time", time], ["released", rlbl], ["waiting", len(wait)]])

# fade all, show result
final_marks = {str(i): ("bad" if s == "idle" else "good") for i, s in enumerate(schedule)}
add(act=1, cells=list(schedule), labels=list(range(1, len(schedule) + 1)),
    code="sim", line=0,
    note=f"Done at t={time}. Schedule: {' '.join(schedule)}. That's {time} slots.",
    marks=final_marks,
    sidebar=heap_sidebar([]),
    state=[["total slots", time], ["idles", schedule.count("idle")]],
    banner=f"minimum slots = {time}")
SIM_ANSWER = time
assert SIM_ANSWER == 8, SIM_ANSWER

# ---- Act 2: the O(1) formula ----
f_max = max(counts.values())
ties = sum(1 for c in counts.values() if c == f_max)
frame = (f_max - 1) * (N + 1) + ties
answer = max(len(tasks), frame)
assert answer == SIM_ANSWER, (answer, SIM_ANSWER)

# draw the skeleton the formula counts: A . . A . . A  then trailing ties
skeleton = []
for r in range(f_max):
    skeleton.append("A")
    if r < f_max - 1:
        skeleton.extend(["·"] * N)
sk_marks = {str(i): ("good" if v == "A" else "dim") for i, v in enumerate(skeleton)}
add(act=2, cells=list(skeleton), labels=list(range(1, len(skeleton) + 1)),
    code="formula", line=2,
    intro="the answer is set by the most frequent task alone — no simulation.",
    invariant="the skeleton spans (f_max-1) blocks of (n+1), plus a final column.",
    note=f"Most frequent = {f_max} (A). Lay them out with n={N} gaps: "
         f"{(f_max - 1)} blocks of {N + 1} + final column.",
    marks=sk_marks,
    state=[["f_max", f_max], ["ties at max", ties], ["frame", frame]])
add(act=2, code="formula", line=3,
    note=f"frame = ({f_max}-1)*({N}+1) + {ties} = {frame}. Other tasks fill the gaps. "
         f"answer = max(len(tasks)={len(tasks)}, {frame}) = {answer}.",
    marks=sk_marks,
    state=[["frame", frame], ["len(tasks)", len(tasks)], ["answer", answer]],
    banner=f"minimum slots = {answer}   (matches the simulation)")

# ---- Act 3: edge case (no cooldown -> gaps fill, len(tasks) wins) ----
tasks2 = ["A", "A", "A", "B", "B", "B"]
N2 = 0
c2 = Counter(tasks2)
fm2 = max(c2.values())
ties2 = sum(1 for c in c2.values() if c == fm2)
frame2 = (fm2 - 1) * (N2 + 1) + ties2
ans2 = max(len(tasks2), frame2)
assert ans2 == 6, ans2
add(act=3, cells=list(tasks2), labels=list(range(1, len(tasks2) + 1)),
    code="formula", line=3,
    intro="with no cooldown there are no gaps, so len(tasks) wins.",
    invariant="answer is the LARGER of the frame and len(tasks); here len(tasks) dominates.",
    note=f"Edge: same tasks, n=0. frame = ({fm2}-1)*1 + {ties2} = {frame2}, "
         f"but len(tasks) = {len(tasks2)}. Answer = max = {ans2} — just run them all.",
    marks={str(i): "good" for i in range(len(tasks2))},
    state=[["n", N2], ["frame", frame2], ["len(tasks)", len(tasks2)], ["answer", ans2]],
    banner=f"minimum slots = {ans2}")

trace = {
    "player": "linear",
    "title": "Task Scheduler — greedy heap simulation, then the formula",
    "acts": ["The greedy rule", "Simulate with a max-heap", "The O(1) formula", "Edge: n = 0"],
    "code": {"sim": SIM, "formula": FORMULA},
    "legend": [["active", "task run this slot"], ["good", "placed task / anchor"],
               ["bad", "idle slot"], ["dim", "gap to fill"]],
    "cells": [],
    "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
