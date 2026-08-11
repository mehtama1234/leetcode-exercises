"""Rich full-arc trace for Meeting Rooms (can one person attend all?), mirroring
solution.py.

Linear renderer: each meeting is a cell labeled "start-end" (sorted by start).
Pointers mark the adjacent pair being checked; marks show clear (good) vs clash
(bad). The state HUD carries the running answer and a comparison counter so the
brute all-pairs waste is visible.
Writes trace.json.
"""
import json
import os

frames = []

BRUTE = [
    "for i in range(n):",
    "    for j in range(i+1, n):",
    "        if overlap(iv[i], iv[j]):",
    "            return False",
    "return True",
]
FAST = [
    "ordered = sorted(intervals, key=lambda iv: iv[0])",
    "for i in range(1, len(ordered)):",
    "    if ordered[i][0] < ordered[i-1][1]:   # starts before last ends",
    "        return False",
    "return True",
]


def add(**f):
    frames.append(f)


def lbl(iv):
    return f"{iv[0]}-{iv[1]}"


# ---------------------------------------------------------------------------
raw = [[0, 30], [5, 10], [15, 20]]

# ---- Act 0: brute — check every pair ----
labels0 = [lbl(iv) for iv in raw]
add(act=0, cells=list(range(len(raw))), labels=labels0, code="brute", line=0,
    intro="every unordered pair tested for overlap — most compares are avoidable.",
    invariant="no ordering assumed, so a clash could be any two meetings.",
    note="Brute: test all pairs for overlap. Any overlap means one person can't "
         "attend everything.",
    pointers={"i": 0, "j": 1}, marks={"0": "active", "1": "active"},
    state=[["i", 0], ["j", 1], ["comparisons", 0]])

work = 0
found = None
for i in range(len(raw)):
    for j in range(i + 1, len(raw)):
        work += 1
        a, b = raw[i], raw[j]
        clash = max(a[0], b[0]) < min(a[1], b[1])
        add(act=0, cells=list(range(len(raw))), labels=labels0, code="brute", line=2,
            note=f"{lbl(a)} vs {lbl(b)}: " +
                 ("they overlap — can't attend both." if clash else "no overlap."),
            pointers={"i": i, "j": j}, arc=[i, j],
            marks={str(i): "active", str(j): "bad" if clash else "good"},
            state=[["pair", f"{lbl(a)} , {lbl(b)}"], ["overlap", clash],
                   ["comparisons", work]])
        if clash and found is None:
            found = (i, j)
add(act=0, cells=list(range(len(raw))), labels=labels0, code="brute", line=3,
    note=f"Answer is False, but it cost {work} pair checks. For n meetings that is "
         "n(n-1)/2 — many between meetings that can't possibly touch.",
    marks={str(k): "dim" for k in range(len(raw))},
    state=[["answer", "False"], ["comparisons", work], ["pattern", "~ n*n / 2"]])

# ---- Act 1: the fix — sort, then only adjacent pairs matter ----
add(act=1, cells=list(range(len(raw))), labels=labels0,
    intro="after sorting by start, if any two overlap then two ADJACENT ones do.",
    note="The waste is comparing meetings far apart in time. Sort by start: the "
         "earliest-starting meeting that could overlap you is the very next one.",
    marks={str(k): "dim" for k in range(len(raw))},
    state=[["idea", "sort by start"], ["then", "check neighbors only"]])

ordered = sorted(raw, key=lambda iv: iv[0])
labels1 = [lbl(iv) for iv in ordered]
add(act=1, cells=list(range(len(ordered))), labels=labels1, code="fast", line=0,
    invariant="starts increase left to right, so only neighbors can be the first clash.",
    note=f"Sorted by start: {labels1}. Now one linear scan over neighbors settles it.",
    marks={str(k): "active" for k in range(len(ordered))},
    state=[["order", "by start"], ["scan cost", "O(n)"]])

# ---- Act 2: fast — adjacent scan ----
checks = 0
verdict = True
add(act=2, cells=list(range(len(ordered))), labels=labels1, code="fast", line=1,
    intro="a clash is next_start < current_end; equality is back-to-back, fine.",
    invariant="everything left of i has been confirmed non-overlapping.",
    note="Walk neighbors: each meeting must end no later than the next one starts.",
    marks={"0": "good"}, state=[["checks", 0]])

for i in range(1, len(ordered)):
    checks += 1
    prev, cur = ordered[i - 1], ordered[i]
    clash = cur[0] < prev[1]
    m = {str(k): "good" for k in range(i)}
    m[str(i)] = "bad" if clash else "active"
    add(act=2, cells=list(range(len(ordered))), labels=labels1, code="fast",
        line=3 if clash else 2, pointers={"prev": i - 1, "next": i}, arc=[i - 1, i],
        note=f"{lbl(cur)} starts at {cur[0]} " +
             (f"< {prev[1]} (prev end) — they overlap. Answer False."
              if clash else f">= {prev[1]} (prev end) — clear so far."),
        marks=m, state=[["next start", cur[0]], ["prev end", prev[1]],
                        ["clash", clash], ["checks", checks]])
    if clash:
        verdict = False
        break

if verdict:
    add(act=2, cells=list(range(len(ordered))), labels=labels1, code="fast", line=4,
        note="Every neighbor was clear. One person can attend them all.",
        marks={str(k): "good" for k in range(len(ordered))},
        banner=f"{labels1}: can attend all -> True   ({checks} checks vs {work} brute)",
        state=[["answer", "True"], ["checks", checks], ["vs brute", work]])
else:
    add(act=2, cells=list(range(len(ordered))), labels=labels1, code="fast", line=3,
        note=f"First clash found at neighbor {checks} — stop early. Only {checks} check(s) "
             f"vs {work} brute comparisons.",
        marks={str(k): "bad" if k <= i else "dim" for k in range(len(ordered))},
        banner=f"{labels1}: can attend all -> False   ({checks} checks vs {work} brute)",
        state=[["answer", "False"], ["checks", checks], ["vs brute", work]])

# ---- Act 3: edge — back-to-back meetings ----
edge = [[1, 5], [5, 10]]
eord = sorted(edge, key=lambda iv: iv[0])
elabels = [lbl(iv) for iv in eord]
add(act=3, cells=list(range(len(eord))), labels=elabels, code="fast", line=1,
    intro="one ending exactly when the next begins is NOT an overlap.",
    invariant="the test is strict <, so touching endpoints pass.",
    note=f"Edge case: {elabels}. The first ends at 5, the second starts at 5.",
    marks={"0": "good"}, state=[["prev end", 5], ["next start", 5]])
add(act=3, cells=list(range(len(eord))), labels=elabels, code="fast", line=2,
    note="next start 5 is NOT < prev end 5 — back-to-back, no overlap. Answer True.",
    pointers={"prev": 0, "next": 1}, arc=[0, 1],
    marks={"0": "good", "1": "good"},
    banner="1-5, 5-10: can attend all -> True   (touching endpoints are fine)",
    state=[["answer", "True"]])

trace = {
    "player": "linear",
    "title": "Meeting Rooms — sort, then only neighbors can clash",
    "acts": ["Brute: every pair", "The fix: sort by start",
             "Fast: neighbor scan", "Edge case: back-to-back"],
    "code": {"brute": BRUTE, "fast": FAST},
    "legend": [["active", "pair being checked / clear"], ["good", "no overlap"],
               ["bad", "overlap — can't attend both"], ["dim", "skipped"]],
    "cells": list(range(len(raw))), "labels": labels0, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
