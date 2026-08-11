"""Step trace for the sliding-window walk of Longest Substring Without Repeating
Characters (mirrors solution.py). Writes trace.json next to this file.
"""
import json
import os

s = "abcabcbb"
cells = list(s)
window: set[str] = set()
left = 0
best = 0
best_span = (0, 0)
frames = []


def sidebar():
    return {"title": "window contents",
            "rows": [[c, ""] for c in sorted(window)]}


frames.append({
    "note": "Two markers, left and right, bound a window with no repeats. "
            "Grow right; if it brings a repeat, pull left until it's gone.",
    "pointers": {"L": 0, "R": 0}, "window": [0, 0], "marks": {"0": "active"},
    "sidebar": sidebar()})

for right, ch in enumerate(s):
    while ch in window:
        frames.append({
            "note": f"'{ch}' at index {right} is already inside the window. "
                    f"Drop '{s[left]}' at the left and move left forward.",
            "pointers": {"L": left, "R": right}, "window": [left, right],
            "marks": {str(left): "bad", str(right): "active"}, "sidebar": sidebar()})
        window.remove(s[left])
        left += 1
    window.add(ch)
    span = right - left + 1
    if span > best:
        best = span
        best_span = (left, right)
    marks = {str(k): "active" for k in range(left, right + 1)}
    frames.append({
        "note": f"'{ch}' is new. Window is s[{left}..{right}] = "
                f"\"{s[left:right+1]}\", length {span}. Best so far: {best}.",
        "pointers": {"L": left, "R": right}, "window": [left, right],
        "marks": marks, "sidebar": sidebar()})

a, b = best_span
frames.append({
    "note": f"Done. Longest run with no repeat is \"{s[a:b+1]}\", length {best}.",
    "pointers": {"L": a, "R": b}, "window": [a, b],
    "marks": {str(k): "good" for k in range(a, b + 1)},
    "banner": f"Longest without repeats: \"{s[a:b+1]}\"  (length {best})"})

trace = {"player": "linear",
         "title": "Longest Substring Without Repeating Characters - a window that never holds a repeat",
         "cells": cells, "labels": list(range(len(cells))), "frames": frames}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
