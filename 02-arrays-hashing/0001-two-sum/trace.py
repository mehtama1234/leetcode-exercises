"""Emit a step trace for the Two Sum hash-map walk (mirrors solution.py).

Writes trace.json next to this file; the site embeds it and viz.js replays it.
"""
import json
import os

nums = [2, 7, 11, 15]
target = 9
seen: dict[int, int] = {}
frames = []


def sidebar():
    return {"title": "seen  (value -> index)",
            "rows": [[str(k), str(v)] for k, v in seen.items()]}


frames.append({
    "note": "Start. The 'seen' map is empty. We walk left to right, once.",
    "pointers": {"i": 0}, "marks": {"0": "active"}, "sidebar": sidebar()})

for i, x in enumerate(nums):
    need = target - x
    frames.append({
        "note": f"At index {i}, value {x}. The partner it needs is "
                f"{target} - {x} = {need}. Have we already seen {need}?",
        "pointers": {"i": i}, "marks": {str(i): "active"}, "sidebar": sidebar()})
    if need in seen:
        j = seen[need]
        frames.append({
            "note": f"Yes — {need} was filed at index {j}. Done.",
            "pointers": {"i": i}, "marks": {str(j): "good", str(i): "good"},
            "sidebar": sidebar(),
            "banner": f"Found [{j}, {i}]   {nums[j]} + {nums[i]} = {target}"})
        break
    seen[x] = i
    frames.append({
        "note": f"No. So we remember it: file {x} -> {i} into the map, then step right.",
        "pointers": {"i": i}, "marks": {str(i): "dim"}, "sidebar": sidebar()})

trace = {"player": "linear",
         "title": "Two Sum - one pass, remembering what we have seen",
         "cells": nums, "frames": frames}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
