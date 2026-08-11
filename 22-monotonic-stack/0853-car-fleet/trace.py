"""Rich full-arc trace for Car Fleet (linear renderer).
No wasteful baseline to race here, so the arc is: the rule (a car can only catch
up, never pass) -> sort nearest-target-first and run the arrival-time stack ->
two edge cases (all merge into one / nobody catches up). Cells are cars in sorted
order; each cell shows arrival time; the sidebar is the stack of fleet-leader times.
Mirrors car_fleet in solution.py. Writes trace.json.
"""
import json
import os

target = 12
position = [10, 8, 0, 5, 3]
speed = [2, 4, 1, 1, 3]
frames = []

CODE = [
    "cars = sorted(zip(position, speed), reverse=True)",
    "for pos, spd in cars:          # nearest target first",
    "    time = (target - pos) / spd",
    "    if not stack or time > stack[-1]:",
    "        stack.append(time)     # slower -> new fleet",
    "    # else: time <= leader -> catches up, merges",
    "return len(stack)",
]


def add(**f):
    frames.append(f)


def sb(stack):
    return {"title": "stack: leader arrival times",
            "rows": [[f"leader {i}", f"t={t:g}"] for i, t in enumerate(stack)]}


cars = sorted(zip(position, speed), reverse=True)
labels = [f"p{p}" for p, s in cars]
times = [(target - p) / s for p, s in cars]
cells = [f"{t:g}" for t in times]

# ---- Act 0: the rule ----
add(act=0, cells=[f"p{p} v{s}" for p, s in zip(position, speed)],
    labels=list(range(len(position))), code="ct", line=0,
    intro="a faster car behind a slower one just bunches up — it can never pass.",
    invariant="cars keep their order to the target; catching up only merges fleets.",
    note=f"Cars race to target {target}. A car that catches the one ahead joins it at "
    "the slower speed. We count distinct fleets that arrive.",
    pointers={}, marks={}, state=[["target", target], ["cars", len(position)]])
add(act=0, cells=[f"p{p} v{s}" for p, s in cars], labels=list(range(len(cars))),
    code="ct", line=0,
    note="Sort by start position, nearest the target first. Now a car can only be caught "
    "by cars behind it (further from target).",
    pointers={}, marks={str(i): "dim" for i in range(len(cars))},
    state=[["sorted (pos desc)", str([p for p, s in cars])]])
add(act=0, cells=cells, labels=list(range(len(cars))), code="ct", line=2,
    intro="free-running arrival time = (target - pos) / speed — the cell values now.",
    note="For each car compute its free-running arrival time (target - pos)/speed. "
    "Slower or further cars arrive later.",
    pointers={}, marks={}, state=[["arrival times", str([f'{t:g}' for t in times])]])

# ---- Act 1: run the stack ----
stack = []
add(act=1, cells=cells, labels=list(range(len(cars))), code="ct", line=1,
    intro="the stack holds fleet-leader arrival times, increasing from the target outward.",
    invariant="a car arriving no later than the leader ahead merges into it.",
    note="Walk cars nearest-first. If a car arrives LATER than the current leader it is "
    "too slow to catch up -> new fleet. Otherwise it catches the fleet ahead and merges.",
    pointers={"i": 0}, marks={}, sidebar=sb(stack), state=[["fleets", 0]])
for i, (pos, spd) in enumerate(cars):
    time = (target - pos) / spd
    new_fleet = (not stack) or time > stack[-1]
    if new_fleet:
        stack.append(time)
        add(act=1, code="ct", line=4,
            note=f"car {i} (pos {pos}, arrives t={time:g}) is slower than the leader ahead "
                 f"-> starts a NEW fleet.",
            pointers={"i": i}, marks={str(i): "good"}, sidebar=sb(stack),
            state=[["car", i], ["arrival", f"{time:g}"], ["fleets", len(stack)]])
    else:
        add(act=1, code="ct", line=5,
            note=f"car {i} (pos {pos}, arrives t={time:g}) reaches the target no later than "
                 f"leader t={stack[-1]:g} -> catches up and MERGES.",
            pointers={"i": i}, marks={str(i): "bad"}, sidebar=sb(stack),
            state=[["car", i], ["arrival", f"{time:g}"], ["merges into", f"t={stack[-1]:g}"],
                   ["fleets", len(stack)]])
add(act=1, code="ct", line=6,
    note=f"{len(stack)} times were pushed -> {len(stack)} fleets.",
    marks={str(i): "good" for i in range(len(cars))}, sidebar=sb(stack),
    state=[["fleets", len(stack)]],
    banner=f"Fleets = {len(stack)}")

# ---- Act 2: edge case, all merge into one ----
target2, pos2, spd2 = 100, [0, 2, 4], [4, 2, 1]
cars2 = sorted(zip(pos2, spd2), reverse=True)
times2 = [(target2 - p) / s for p, s in cars2]
stack2 = []
add(act=2, cells=[f"{t:g}" for t in times2], labels=list(range(len(cars2))), code="ct", line=1,
    intro="everyone catches the leader ahead — one fleet.",
    invariant="each car arrives no later than the one ahead, so nothing new is pushed.",
    note="Edge A: target 100, cars fast-to-slow front-to-back. Each catches the fleet "
    "ahead, so only one leader is ever pushed.",
    pointers={"i": 0}, marks={}, sidebar={"title": "stack: leader times", "rows": []},
    state=[["fleets", 0]])
for i, (pos, spd) in enumerate(cars2):
    time = (target2 - pos) / spd
    if not stack2 or time > stack2[-1]:
        stack2.append(time)
        m = "good"
    else:
        m = "bad"
    add(act=2, code="ct", line=3,
        note=f"car {i} arrives t={time:g} -> " + ("new fleet." if m == "good" else "merges."),
        pointers={"i": i}, marks={str(i): m},
        sidebar={"title": "stack: leader times", "rows": [[f"leader {k}", f"t={t:g}"] for k, t in enumerate(stack2)]},
        state=[["arrival", f"{time:g}"], ["fleets", len(stack2)]])
add(act=2, code="ct", line=6, note=f"All merge -> {len(stack2)} fleet.",
    marks={str(i): "good" for i in range(len(cars2))},
    state=[["fleets", len(stack2)]], banner="All merge -> 1 fleet")

# ---- Act 3: edge case, nobody catches up ----
target3, pos3, spd3 = 10, [6, 8], [3, 2]
cars3 = sorted(zip(pos3, spd3), reverse=True)  # (8,2),(6,3)
times3 = [(target3 - p) / s for p, s in cars3]  # 1.0, 1.333
stack3 = []
add(act=3, cells=[f"{t:g}" for t in times3], labels=list(range(len(cars3))), code="ct", line=1,
    intro="the car behind is slower and never reaches the leader — two fleets.",
    invariant="a strictly-later arrival always pushes a new leader.",
    note="Edge B: the trailing car arrives later than the one ahead, so it can never "
    "catch up. Two separate fleets.",
    pointers={"i": 0}, marks={}, sidebar={"title": "stack: leader times", "rows": []},
    state=[["fleets", 0]])
for i, (pos, spd) in enumerate(cars3):
    time = (target3 - pos) / spd
    if not stack3 or time > stack3[-1]:
        stack3.append(time)
    add(act=3, code="ct", line=4,
        note=f"car {i} arrives t={time:g} -> new fleet (nobody to catch).",
        pointers={"i": i}, marks={str(i): "good"},
        sidebar={"title": "stack: leader times", "rows": [[f"leader {k}", f"t={t:g}"] for k, t in enumerate(stack3)]},
        state=[["arrival", f"{time:g}"], ["fleets", len(stack3)]])
add(act=3, code="ct", line=6, note=f"Nobody catches up -> {len(stack3)} fleets.",
    marks={"0": "good", "1": "good"},
    state=[["fleets", len(stack3)]], banner="No catch-up -> 2 fleets")

trace = {
    "player": "linear",
    "title": "Car Fleet - an arrival-time stack, sorted nearest the target first",
    "acts": ["The rule", "Run the stack", "Edge: all merge", "Edge: nobody catches up"],
    "code": {"ct": CODE},
    "legend": [["good", "new fleet leader"], ["bad", "merged into fleet ahead"],
               ["dim", "sorted, waiting"]],
    "cells": cells, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
