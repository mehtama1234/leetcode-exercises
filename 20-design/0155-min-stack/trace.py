"""Rich full-arc trace for Min Stack (linear renderer).
Design problems have no wasteful brute baseline in the usual sense, but getMin
DOES have a slow version: scan the whole stack every time. So the arc is:
  Act 0  the naive getMin scans the stack -> O(n) per query (a work counter climbs)
  Act 1  the trick: carry a running min alongside each element -> getMin is mins[-1], O(1)
  Act 2  edge: duplicate minimums -> parallel mins stack keeps the min correct after a pop
Mirrors solution.py exactly: push appends val and pushes min(val, mins[-1]);
pop pops both; getMin returns mins[-1]. Writes trace.json.
"""
import json
import os

frames = []

NAIVE = [
    "def getMin():           # naive",
    "    m = stack[0]",
    "    for x in stack:     # scan every element",
    "        m = min(m, x)",
    "    return m",
]
TRICK = [
    "def push(val):",
    "    stack.append(val)",
    "    cur = val if not mins else min(val, mins[-1])",
    "    mins.append(cur)     # min so far, at this level",
    "def pop():",
    "    stack.pop(); mins.pop()",
    "def getMin():",
    "    return mins[-1]      # O(1), no scan",
]


def add(**f):
    frames.append(f)


def sidebar(mins):
    # mins[i] = min of stack[0..i]; show level -> value, top last.
    return {"title": "mins  (min of stack[0..i])",
            "rows": [[str(i), str(v)] for i, v in enumerate(mins)]}


# =====================================================================
# Act 0 — the naive way: getMin scans the whole stack, every call.
# =====================================================================
stack0 = [-2, 0, -3]
add(act=0, cells=list(stack0), code="naive", line=0,
    intro="each getMin re-walks the ENTIRE stack — the work counter is the cost we delete.",
    invariant="the true minimum is somewhere in the stack; naive re-finds it each time.",
    note="A plain stack (push/pop/top) can't answer getMin without looking. The naive "
    "fix: scan all of stack for the smallest. That is O(n) per query.",
    pointers={"top": 2}, marks={"0": "dim", "1": "dim", "2": "active"},
    state=[["stack", "[-2, 0, -3]"], ["scans", 0]])

work = 0
m = stack0[0]
for i, x in enumerate(stack0):
    work += 1
    m = min(m, x)
    add(act=0, code="naive", line=3,
        note=f"Compare element {x}: running min = {m}. One more step of the scan.",
        pointers={"top": 2, "i": i},
        marks={str(i): "active", **{str(k): "dim" for k in range(3) if k != i}},
        state=[["element", x], ["min so far", m], ["scans", work]])
add(act=0, code="naive", line=4,
    note=f"getMin returned {m}, but it cost {work} comparisons. Call getMin a million "
    f"times and you re-scan a million times — pure repeated work.",
    pointers={"top": 2}, marks={"2": "good", "0": "dim", "1": "dim"},
    state=[["getMin", m], ["cost", "O(n) each call"], ["scans", work]],
    banner=f"Naive getMin = {m}  —  {work} comparisons for one query")

# =====================================================================
# Act 1 — the trick: a parallel mins stack. getMin = mins[-1], O(1).
# Mirrors push(): cur = val if not mins else min(val, mins[-1]).
# =====================================================================
stack = []
mins = []
add(act=1, cells=[], code="trick", line=0,
    intro="a second stack records the min-so-far at every level — getMin just reads its top.",
    invariant="mins[i] is always the minimum of stack[0..i]; mins[-1] is the current min.",
    note="The trick: alongside each pushed value, remember the minimum of everything at "
    "or below it. Push -2, 0, -3 and watch mins track it.",
    pointers={}, sidebar=sidebar(mins),
    state=[["stack", "[]"], ["mins", "[]"]])

for val in (-2, 0, -3):
    stack.append(val)
    cur = val if not mins else min(val, mins[-1])
    mins.append(cur)
    top = len(stack) - 1
    add(act=1, cells=list(stack), code="trick", line=2,
        note=f"push({val}): min so far = "
             + (f"{val} (stack was empty)" if len(mins) == 1
                else f"min({val}, {mins[-2]}) = {cur}") + ".",
        pointers={"top": top},
        marks={str(top): "active", **{str(k): "dim" for k in range(top)}},
        sidebar=sidebar(mins),
        state=[["pushed", val], ["cur min", cur], ["mins top", mins[-1]]])

top = len(stack) - 1
add(act=1, code="trick", line=7,
    note=f"getMin just reads mins[-1] = {mins[-1]} — no scan, O(1). The smallest value "
    "was tracked as we went.",
    pointers={"top": top}, marks={str(top): "good",
                                  **{str(k): "dim" for k in range(top)}},
    sidebar=sidebar(mins),
    state=[["getMin", mins[-1]], ["cost", "O(1)"]],
    banner=f"getMin = {mins[-1]}  in one read (mins[-1]) vs a full scan")

# pop once: removes -3 from both; min returns to 0's level.
stack.pop()
mins.pop()
top = len(stack) - 1
add(act=1, cells=list(stack), code="trick", line=5,
    note=f"pop() removes {(-3)} from BOTH stacks. mins[-1] drops back to {mins[-1]} — "
    "the min of what remains, with no work.",
    pointers={"top": top}, marks={str(top): "good",
                                  **{str(k): "dim" for k in range(top)}},
    sidebar=sidebar(mins),
    state=[["popped", -3], ["getMin now", mins[-1]]])

# =====================================================================
# Act 2 — edge: duplicate minimums. push 1,1,0; pop the 0; getMin still 1.
# =====================================================================
stack = []
mins = []
add(act=2, cells=[], code="trick", line=0,
    intro="two equal minimums must both be recorded — popping one must not lose the min.",
    invariant="every level stores its own min-so-far, so duplicates are counted separately.",
    note="Edge: duplicate minimums. Push 1, 1, 0. If we only stored ONE copy of the min "
    "we'd lose it on the first pop — the parallel stack avoids that.",
    pointers={}, sidebar=sidebar(mins),
    state=[["stack", "[]"], ["mins", "[]"]])

for val in (1, 1, 0):
    stack.append(val)
    cur = val if not mins else min(val, mins[-1])
    mins.append(cur)
    top = len(stack) - 1
    add(act=2, cells=list(stack), code="trick", line=2,
        note=f"push({val}): min so far = {cur}. Each level keeps its own min, so both 1s "
             "are recorded independently." if val == 1 else
             f"push({val}): {val} is the new minimum; mins top = {cur}.",
        pointers={"top": top},
        marks={str(top): "active", **{str(k): "dim" for k in range(top)}},
        sidebar=sidebar(mins),
        state=[["pushed", val], ["cur min", cur]])

top = len(stack) - 1
add(act=2, code="trick", line=7,
    note=f"getMin = {mins[-1]} (the 0 on top).",
    pointers={"top": top}, marks={str(top): "good",
                                  **{str(k): "dim" for k in range(top)}},
    sidebar=sidebar(mins), state=[["getMin", mins[-1]]])

# pop the 0
stack.pop()
mins.pop()
top = len(stack) - 1
add(act=2, cells=list(stack), code="trick", line=5,
    note=f"pop() removes the 0. mins[-1] is now {mins[-1]} — still correct, because the "
    "second 1 recorded its own min-so-far. Nothing had to be re-scanned.",
    pointers={"top": top}, marks={str(top): "good",
                                  **{str(k): "dim" for k in range(top)}},
    sidebar=sidebar(mins),
    state=[["popped", 0], ["getMin now", mins[-1]]],
    banner=f"After popping the 0, getMin = {mins[-1]} — the duplicate 1 kept the min")

trace = {
    "player": "linear",
    "title": "Min Stack - carry the running minimum instead of scanning for it",
    "acts": ["Naive: scan for the min (O(n))", "The trick: a parallel mins stack",
             "Edge: duplicate minimums"],
    "code": {"naive": NAIVE, "trick": TRICK},
    "legend": [["active", "top / element scanned"], ["good", "the current min"],
               ["dim", "below the top"]],
    "cells": [], "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
