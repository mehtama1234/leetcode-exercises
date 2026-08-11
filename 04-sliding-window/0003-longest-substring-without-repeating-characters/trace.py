"""Full-arc trace for Longest Substring Without Repeating Characters:
brute force -> the waste -> sliding window -> edge case. Mirrors solution.py.
"""
import json
import os

s = "abcabcbb"
cells = list(s)
frames = []


def add(**f):
    frames.append(f)


def setrows(title, items):
    return {"title": title, "rows": [[c, ""] for c in items]}


# ---- Act 0: brute force — start fresh from each index ----
add(act=0, cells=cells, labels=list(range(len(s))),
    note="Brute force: from each start, extend until a repeat appears; remember "
    "the longest clean run. Watch the first two starts.",
    pointers={"start": 0, "end": 0}, window=[0, 0], marks={"0": "active"})
for start in range(2):  # show two starts, then summarize
    win = []
    end = start
    while end < len(s) and s[end] not in win:
        win.append(s[end])
        add(act=0, note=f"start={start}: window \"{''.join(win)}\" is still clean "
            f"(length {len(win)}).",
            pointers={"start": start, "end": end}, window=[start, end],
            marks={str(k): "active" for k in range(start, end + 1)},
            sidebar=setrows("this window", win))
        end += 1
    if end < len(s):
        add(act=0, note=f"start={start}: '{s[end]}' repeats — stop this start, "
            f"then throw the whole window away and start over at {start+1}.",
            pointers={"start": start, "end": end}, window=[start, end],
            marks={str(start): "bad", str(end): "bad"},
            sidebar=setrows("this window", win))

# ---- Act 1: the waste ----
add(act=1, note="The waste: start=1 re-reads 'b','c' that start=0 just read. Every "
    "start re-scans characters an earlier start already checked.",
    marks={str(k): "dim" for k in range(len(s))})
add(act=1, note="That double-reading is about n*n work. The fix: never move start "
    "backward — keep one window and only ever grow or shrink it.",
    marks={str(k): "dim" for k in range(len(s))})

# ---- Act 2: sliding window, one left-to-right pass ----
window = set()
left = 0
best = 0
best_span = (0, 0)
add(act=2, cells=cells, note="One window, two markers. Grow right. If right brings a "
    "repeat, shrink from the left until it's gone. left never rewinds.",
    pointers={"L": 0, "R": 0}, window=[0, 0], marks={"0": "active"},
    sidebar=setrows("window", []))
for right, ch in enumerate(s):
    while ch in window:
        add(act=2, note=f"'{ch}' is already in the window. Drop '{s[left]}' on the "
            f"left and move left forward.",
            pointers={"L": left, "R": right}, window=[left, right],
            marks={str(left): "bad", str(right): "active"},
            sidebar=setrows("window", sorted(window)))
        window.remove(s[left]); left += 1
    window.add(ch)
    span = right - left + 1
    if span > best:
        best = span; best_span = (left, right)
    add(act=2, note=f"'{ch}' is new. Window s[{left}..{right}] = \"{s[left:right+1]}\", "
        f"length {span}. Best so far: {best}.",
        pointers={"L": left, "R": right}, window=[left, right],
        marks={str(k): "active" for k in range(left, right + 1)},
        sidebar=setrows("window", sorted(window)))
a, b = best_span
add(act=2, note=f"Longest clean run: \"{s[a:b+1]}\", length {best}.",
    pointers={"L": a, "R": b}, window=[a, b],
    marks={str(k): "good" for k in range(a, b + 1)},
    banner=f"Longest without repeats: \"{s[a:b+1]}\"  (length {best})")

# ---- Act 3: edge case, all identical ----
e = "bbbb"
add(act=3, cells=list(e), labels=list(range(len(e))),
    note="Edge case: every character the same. The window can never hold two, so "
    "left keeps chasing right and the answer is 1.",
    pointers={"L": 0, "R": 0}, window=[0, 0], marks={"0": "active"},
    sidebar=setrows("window", ["b"]))
win = set(["b"]); left = 0
for right in range(1, len(e)):
    add(act=3, note=f"'b' at {right} repeats. Drop left 'b', move left to {right}.",
        pointers={"L": left, "R": right}, window=[left, right],
        marks={str(left): "bad", str(right): "active"}, sidebar=setrows("window", ["b"]))
    left = right
add(act=3, note="Window never grows past length 1.",
    pointers={"L": len(e) - 1, "R": len(e) - 1}, window=[len(e) - 1, len(e) - 1],
    marks={str(len(e) - 1): "good"}, banner="Longest without repeats: \"b\"  (length 1)")

trace = {"player": "linear",
         "title": "Longest Substring Without Repeating Characters - from restart-every-time to one window",
         "acts": ["Brute force: every start", "The waste",
                  "Fast: sliding window", "Edge case: \"bbbb\""],
         "cells": cells, "labels": list(range(len(s))), "frames": frames}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
