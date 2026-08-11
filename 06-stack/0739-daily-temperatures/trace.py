"""Full-arc trace for Daily Temperatures, mirroring solution.py: the O(n^2)
scan-forward brute force and the O(n) monotonic-decreasing stack. Linear
renderer: temperatures as a row of cells, the growing `answer` shown by marks +
sidebar, and the stack of waiting-day indices in the sidebar. A work counter
makes brute-vs-fast visible. Writes trace.json.
"""
import json
import os

temps = [73, 74, 75, 71, 69, 72, 76, 73]
# answer = [1, 1, 4, 2, 1, 1, 0, 0]
frames = []

BRUTE = [
    "for i in range(n):",
    "    for j in range(i+1, n):",
    "        if temps[j] > temps[i]:",
    "            answer[i] = j - i",
    "            break",
]
FAST = [
    "for i, temp in enumerate(temps):",
    "    while stack and temps[stack[-1]] < temp:",
    "        prev = stack.pop()",
    "        answer[prev] = i - prev",
    "    stack.append(i)",
]


def add(**f):
    frames.append(f)


# ---- Act 0: brute force (first few days only, to show the re-scan) ----
n = len(temps)
work = 0
answer = [0] * n
add(act=0, cells=temps, code="brute", line=0,
    intro="every day scans forward on its own — a long cool spell gets re-walked again and again.",
    invariant="answer[k] is set for every day k already fully scanned.",
    note="Brute force: stand on day i and walk forward until a warmer day appears.",
    pointers={"i": 0, "j": 1}, marks={"0": "active"},
    state=[["i", 0], ["scans", 0]])
for i in range(n):
    for j in range(i + 1, n):
        work += 1
        warmer = temps[j] > temps[i]
        add(act=0, code="brute", line=2,
            note=f"Day {i} ({temps[i]}) vs day {j} ({temps[j]}). "
                 + (f"Warmer — wait is {j - i} days." if warmer else "Not warmer, keep scanning."),
            pointers={"i": i, "j": j},
            marks={str(i): "active", str(j): "good" if warmer else "dim"},
            state=[["i", i], ["j", j], ["scans", work]])
        if warmer:
            answer[i] = j - i
            break
add(act=0, code="brute", line=4,
    note=f"Brute answer = {answer}. It cost {work} forward-scans because cool stretches get re-walked.",
    marks={str(k): "good" for k in range(n)},
    state=[["answer", str(answer)], ["scans", work]])

# ---- Act 1: the waste ----
add(act=1,
    intro="days 2, 3, 4 all re-scan the same cooling tail — that overlap is the waste.",
    note=f"Each day re-scans a tail earlier days already covered: {work} scans for 8 days. "
         "For a long descent this is ~n*n / 2 work.",
    marks={str(k): "dim" for k in range(n)},
    state=[["scans (brute)", work], ["pattern", "~ n*n / 2"]])
add(act=1,
    note="But a day, once beaten, is answered forever. If we remember the days still waiting, "
         "each is resolved exactly once. That is a stack.",
    marks={str(k): "dim" for k in range(n)},
    state=[["idea", "remember waiters"], ["target", "O(n)"]])

# ---- Act 2: monotonic stack ----
answer = [0] * n
stack = []
pops = 0


def sidebar(stack, answer):
    rows = [[f"day {idx}", f"{temps[idx]}°"] for idx in stack]
    if not rows:
        rows = [["(empty)", ""]]
    return {"title": "stack: days waiting (cool->warm bottom->top... top=coolest)", "rows": rows}


def marks_for(i, stack, resolved):
    m = {}
    for idx in stack:
        m[str(idx)] = "dim"      # still waiting
    for idx in resolved:
        m[str(idx)] = "good"     # just answered
    m[str(i)] = "active"         # today
    return m


add(act=2, cells=temps, code="fast", line=0,
    intro="today is the 'next warmer day' for every waiting day it beats — pop and answer them all.",
    invariant="the stack holds waiting days with strictly decreasing temperatures (top = coolest).",
    note="One pass. Keep a stack of days still waiting for something warmer.",
    pointers={"i": 0}, marks={"0": "active"}, sidebar=sidebar([], answer),
    state=[["pops", 0]])
for i, temp in enumerate(temps):
    resolved = []
    while stack and temps[stack[-1]] < temp:
        prev = stack.pop()
        answer[prev] = i - prev
        pops += 1
        resolved.append(prev)
        add(act=2, code="fast", line=3,
            note=f"Day {i} ({temp}°) is warmer than waiting day {prev} ({temps[prev]}°). "
                 f"Answer[{prev}] = {i} - {prev} = {i - prev}. Pop it.",
            pointers={"i": i}, marks=marks_for(i, stack, resolved), sidebar=sidebar(stack, answer),
            state=[["today", f"day {i} = {temp}°"], ["resolved", f"day {prev} -> {i - prev}"], ["pops", pops]])
    stack.append(i)
    add(act=2, code="fast", line=4,
        note=f"Day {i} ({temp}°) now waits for its own warmer day. Push it.",
        pointers={"i": i}, marks=marks_for(i, stack, []), sidebar=sidebar(stack, answer),
        state=[["stack depth", len(stack)], ["answer so far", str(answer)]])
add(act=2, code="fast", line=4,
    note=f"Done in one pass. answer = {answer}. Days {stack} never warmed, so they stay 0. "
         f"{pops} pops + {n} pushes vs {work} brute scans.",
    marks={str(k): "good" for k in range(n)}, sidebar=sidebar(stack, answer),
    banner=f"answer = {answer}   — {n + pops} stack ops vs {work} brute scans",
    state=[["answer", str(answer)], ["total ops", n + pops], ["vs brute", work]])

# ---- Act 3: edge case, strictly cooling ----
edge = [90, 80, 70, 60]
answer = [0] * len(edge)
stack = []
add(act=3, cells=edge, code="fast", line=0,
    intro="if it only ever cools, nobody is beaten — the stack just grows and every answer stays 0.",
    invariant="a day leaves the stack only when a later, warmer day arrives.",
    note="Edge case: temperatures strictly decreasing. No day ever finds a warmer one.",
    pointers={"i": 0}, marks={"0": "active"},
    sidebar={"title": "stack: days waiting", "rows": [["(empty)", ""]]},
    state=[["answer", str(answer)]])
for i, temp in enumerate(edge):
    stack.append(i)
    rows = [[f"day {idx}", f"{edge[idx]}°"] for idx in stack]
    add(act=3, code="fast", line=4,
        note=f"Day {i} ({temp}°) is cooler than the top, so nothing pops. Push it and keep waiting.",
        pointers={"i": i}, marks={str(k): "dim" for k in stack[:-1]} | {str(i): "active"},
        sidebar={"title": "stack: days waiting", "rows": rows},
        state=[["stack depth", len(stack)], ["answer", str(answer)]])
add(act=3, code="fast", line=4,
    note=f"The pass ends with all {len(edge)} days still on the stack. None warmed, so answer = {answer}.",
    marks={str(k): "bad" for k in range(len(edge))},
    sidebar={"title": "stack: never resolved", "rows": [[f"day {idx}", f"{edge[idx]}°"] for idx in stack]},
    banner=f"answer = {answer} — a cooling run leaves every day at 0",
    state=[["answer", str(answer)]])

trace = {
    "player": "linear",
    "title": "Daily Temperatures — a stack of days still waiting to warm",
    "acts": ["Brute force: scan forward", "The waste", "Fast: monotonic stack", "Edge case: only cooling"],
    "code": {"brute": BRUTE, "fast": FAST},
    "legend": [["active", "today"], ["good", "just answered / resolved"], ["dim", "still waiting"], ["bad", "never warms"]],
    "cells": temps, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
