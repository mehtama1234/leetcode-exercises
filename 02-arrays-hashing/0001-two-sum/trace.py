"""Full-arc step trace for Two Sum: brute force -> the waste -> fast hash map ->
edge case. Mirrors the two functions in solution.py. Writes trace.json.
"""
import json
import os

nums = [2, 7, 11, 15]
T = 26  # answer is indices [2, 3]  (11 + 15)
frames = []


def add(**f):
    frames.append(f)


# ---- Act 0: brute force, try every pair (and re-walk the tail each time) ----
add(act=0, cells=nums, note=f"Brute force: test every pair. Target is {T}. "
    f"Anchor i, then let j sweep everything to its right.",
    pointers={"i": 0, "j": 1}, marks={"0": "active", "1": "dim"})

comparisons = 0
found = None
for i in range(len(nums)):
    for j in range(i + 1, len(nums)):
        comparisons += 1
        s = nums[i] + nums[j]
        hit = s == T
        add(act=0,
            note=f"i={i} ({nums[i]}), j={j} ({nums[j]}): {nums[i]}+{nums[j]}={s}. "
                 + ("Match!" if hit else f"Not {T}, slide j on."),
            pointers={"i": i, "j": j},
            marks={str(i): "active",
                   str(j): "good" if hit else "dim"})
        if hit:
            found = (i, j)
            break
    if found:
        break

add(act=0, note=f"Found after {comparisons} comparisons. But notice how much "
    f"sweeping that took for just four numbers.",
    pointers={"i": found[0], "j": found[1]},
    marks={str(found[0]): "good", str(found[1]): "good"})

# ---- Act 1: name the waste ----
add(act=1, note=f"The waste: i=0 checked 3 pairs, i=1 checked 2, i=2 checked 1 "
    f"— {comparisons} checks. Every anchor re-walks the tail the anchor before it "
    f"already walked.", marks={str(k): "dim" for k in range(len(nums))})
add(act=1, note="For n numbers that is about n(n-1)/2 checks. n=1000 -> ~500,000. "
    "The repeated tail-walking is the thing to remove.",
    marks={str(k): "dim" for k in range(len(nums))})

# ---- Act 2: fast hash map, one pass, same target ----
seen = {}


def sidebar():
    return {"title": "seen  (value -> index)",
            "rows": [[str(k), str(v)] for k, v in seen.items()]}


add(act=2, note="Same target, but now we remember as we go. For each x, its "
    "partner is forced: T - x. So we only ask: have we seen it?",
    pointers={"i": 0}, marks={"0": "active"}, sidebar=sidebar())
for i, x in enumerate(nums):
    need = T - x
    add(act=2, note=f"x={x} at index {i}. Partner needed = {T} - {x} = {need}. "
        f"Seen {need} already?", pointers={"i": i},
        marks={str(i): "active"}, sidebar=sidebar())
    if need in seen:
        j = seen[need]
        add(act=2, note=f"Yes — {need} was filed at index {j}. One pass, no tail sweeps.",
            pointers={"i": i}, marks={str(j): "good", str(i): "good"},
            sidebar=sidebar(),
            banner=f"Found [{j}, {i}]   {nums[j]} + {nums[i]} = {T}")
        break
    seen[x] = i
    add(act=2, note=f"No. File {x} -> {i} and step right.", pointers={"i": i},
        marks={str(i): "dim"}, sidebar=sidebar())

# ---- Act 3: edge case, a duplicate value ----
edge = [3, 3]
seen = {}
add(act=3, cells=edge, labels=[0, 1],
    note="Edge case: two equal numbers, target 6. Why doesn't the 3 just pair "
    "with itself? Because we check BEFORE we file.",
    pointers={"i": 0}, marks={"0": "active"}, sidebar=sidebar())
for i, x in enumerate(edge):
    need = 6 - x
    if need in seen:
        j = seen[need]
        add(act=3, note=f"x=3 at index {i}. Need 3 — and a different 3 was filed at "
            f"index {j}. That is a real pair.",
            pointers={"i": i}, marks={str(j): "good", str(i): "good"},
            sidebar=sidebar(), banner="Found [0, 1]   3 + 3 = 6")
        break
    add(act=3, note=f"x=3 at index {i}. Need 3, nothing filed yet, so file 3 -> {i}. "
        f"The lone 3 can't match itself.",
        pointers={"i": i}, marks={str(i): "dim"}, sidebar=sidebar())
    seen[x] = i

trace = {"player": "linear",
         "title": "Two Sum - from every-pair to one honest pass",
         "acts": ["Brute force: try every pair", "The waste",
                  "Fast: hash map, one pass", "Edge case: [3, 3]"],
         "cells": nums, "frames": frames}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
