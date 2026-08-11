"""Full-arc trace for Contains Duplicate, mirroring the two functions in
solution.py: the O(n^2) every-pair brute force and the O(n) hash-set pass.
Linear renderer: a row of cells, named pointers, a `seen` sidebar, a work
counter so brute-vs-fast is visible. Writes trace.json.
"""
import json
import os

nums = [1, 2, 3, 1]  # duplicate 1 at indices 0 and 3
frames = []

BRUTE = [
    "for i in range(n):",
    "    for j in range(i+1, n):",
    "        if nums[i] == nums[j]:",
    "            return True",
    "return False",
]
FAST = [
    "seen = set()",
    "for x in nums:",
    "    if x in seen:",
    "        return True",
    "    seen.add(x)",
    "return False",
]


def add(**f):
    frames.append(f)


# ---- Act 0: brute force ----
work = 0
found = None
add(act=0, cells=nums, code="brute", line=0,
    intro="j re-walks the whole tail for every i — the same ground, again and again.",
    invariant="every pair before this (i, j) has already been compared.",
    note="Brute force: a duplicate is two positions with the same value, so test every pair.",
    pointers={"i": 0, "j": 1}, marks={"0": "active", "1": "dim"},
    state=[["i", 0], ["j", 1], ["comparisons", 0]])
for i in range(len(nums)):
    if found:
        break
    for j in range(i + 1, len(nums)):
        work += 1
        hit = nums[i] == nums[j]
        add(act=0, code="brute", line=2 if not hit else 3,
            note=f"nums[{i}] vs nums[{j}] = {nums[i]} vs {nums[j]}. "
                 + ("Same value — a duplicate." if hit else "Different."),
            pointers={"i": i, "j": j}, arc=[i, j],
            marks={str(i): "active", str(j): "good" if hit else "dim"},
            state=[["i", i], ["j", j], [f"{nums[i]}=={nums[j]}?", str(hit)], ["comparisons", work]])
        if hit:
            found = (i, j)
            break
add(act=0, code="brute", line=3,
    note=f"Found the pair at indices {found[0]} and {found[1]} — but it cost {work} comparisons.",
    pointers={"i": found[0], "j": found[1]}, arc=list(found),
    marks={str(found[0]): "good", str(found[1]): "good"},
    banner=f"True — nums[{found[0]}] == nums[{found[1]}] == {nums[found[0]]}",
    state=[["answer", "True"], ["comparisons", work]])

# ---- Act 1: the waste ----
add(act=1,
    intro="how the comparison counter climbs — that is the work we delete.",
    note=f"i=0 checked 3 pairs, i=1 checked 2, i=2 checked 1 = {work} checks. Each i "
         "re-walks the tail the last i already walked.",
    marks={str(k): "dim" for k in range(len(nums))},
    state=[["comparisons (brute)", work], ["pattern", "~ n*n / 2"]])
add(act=1,
    note="For n values that is about n(n-1)/2. n=1000 -> ~500,000 checks, just to ask "
         "'have I seen this before?'. A set answers that in one step.",
    marks={str(k): "dim" for k in range(len(nums))},
    state=[["at n=1000", "~500,000"], ["what we want", "~1,000"]])

# ---- Act 2: fast hash set ----
seen = set()
checks = 0


def sidebar():
    return {"title": "seen (values so far)", "rows": [[str(v), "in"] for v in seen]}


add(act=2, cells=nums, code="fast", line=0,
    intro="each value is asked once — 'already in seen?' — then filed. No tail walks.",
    invariant="seen holds exactly the values strictly to the left of x.",
    note="Same array, but remember as we go. Check before we add, so the first repeat is caught the moment it lands.",
    pointers={"x": 0}, marks={"0": "active"}, sidebar=sidebar(),
    state=[["checks", 0]])
for i, x in enumerate(nums):
    checks += 1
    if x in seen:
        add(act=2, code="fast", line=3,
            note=f"x = {x} at index {i}. It is already in seen — duplicate found on the spot.",
            pointers={"x": i}, marks={str(i): "good"}, sidebar=sidebar(),
            banner=f"True — {x} was seen before   ({checks} checks vs {work} brute)",
            state=[["answer", "True"], ["checks", checks], ["vs brute", work]])
        break
    add(act=2, code="fast", line=2,
        note=f"x = {x} at index {i}. Not in seen yet.",
        pointers={"x": i}, marks={str(i): "active"}, sidebar=sidebar(),
        state=[["x", x], ["in seen?", "no"], ["checks", checks]])
    seen.add(x)
    add(act=2, code="fast", line=4,
        note=f"File {x} into seen and step right.",
        pointers={"x": i}, marks={str(i): "dim"}, sidebar=sidebar(),
        state=[["filed", x], ["checks", checks]])

# ---- Act 3: edge case, all distinct ----
edge = [1, 2, 3, 4]
seen = set()
add(act=3, cells=edge, code="fast", line=0,
    intro="the loop runs to the end and never returns True — that is a clean 'no duplicate'.",
    invariant="a value only enters seen after we confirm it was not already there.",
    note="Edge case: every value distinct. The set fills, no repeat is ever hit.",
    pointers={"x": 0}, marks={"0": "active"}, sidebar=sidebar(),
    state=[["result so far", "False"]])
for i, x in enumerate(edge):
    seen.add(x)
    add(act=3, code="fast", line=4,
        note=f"x = {x} not in seen. File it and move on.",
        pointers={"x": i}, marks={str(i): "dim"}, sidebar=sidebar(),
        state=[["filed", x]])
add(act=3, code="fast", line=5,
    note="Reached the end with no repeat. Return False.",
    marks={str(k): "good" for k in range(len(edge))}, sidebar=sidebar(),
    banner="False — all four values are distinct",
    state=[["answer", "False"]])

trace = {
    "player": "linear",
    "title": "Contains Duplicate — from every-pair to one honest pass",
    "acts": ["Brute force: every pair", "The waste", "Fast: hash set", "Edge case: all distinct"],
    "code": {"brute": BRUTE, "fast": FAST},
    "legend": [["active", "value under inspection"], ["good", "the duplicate / resolved"], ["dim", "filed / skipped"]],
    "cells": nums, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
