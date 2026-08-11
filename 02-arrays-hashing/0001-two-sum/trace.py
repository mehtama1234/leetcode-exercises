"""Rich full-arc trace for Two Sum, mirroring the two functions in solution.py.
Carries code-line highlights, a live state HUD (incl. a work counter), pairing
arcs, per-act intro + invariant, and a legend. Writes trace.json.
"""
import json
import os

nums = [2, 7, 11, 15]
T = 26  # answer indices [2, 3]  (11 + 15)
frames = []

BRUTE = [
    "for i in range(n):",
    "    for j in range(i+1, n):",
    "        if nums[i] + nums[j] == target:",
    "            return [i, j]",
]
FAST = [
    "seen = {}",
    "for i, x in enumerate(nums):",
    "    need = target - x",
    "    if need in seen:",
    "        return [seen[need], i]",
    "    seen[x] = i",
]


def add(**f):
    frames.append(f)


# ---- Act 0: brute force ----
work = 0
found = None
add(act=0, cells=nums, code="brute", line=0,
    intro="j sweep the whole tail for every i — the same ground, again and again.",
    invariant="we have tested every pair before this i, in order.",
    note=f"Brute force: test every pair against target {T}. Anchor i, sweep j right.",
    pointers={"i": 0, "j": 1}, marks={"0": "active", "1": "dim"},
    state=[["i", 0], ["j", 1], ["target", T], ["comparisons", 0]])
for i in range(len(nums)):
    for j in range(i + 1, len(nums)):
        work += 1
        s = nums[i] + nums[j]
        hit = s == T
        add(act=0, code="brute", line=2 if not hit else 3,
            note=f"nums[{i}]+nums[{j}] = {nums[i]}+{nums[j]} = {s}. "
                 + ("Match." if hit else f"Not {T}."),
            pointers={"i": i, "j": j}, arc=[i, j],
            marks={str(i): "active", str(j): "good" if hit else "dim"},
            state=[["i", i], ["j", j], [f"nums[{i}]+nums[{j}]", s], ["comparisons", work]])
        if hit:
            found = (i, j)
            break
    if found:
        break
add(act=0, code="brute", line=3,
    note=f"Found [{found[0]}, {found[1]}] — but it cost {work} comparisons for four numbers.",
    pointers={"i": found[0], "j": found[1]}, arc=list(found),
    marks={str(found[0]): "good", str(found[1]): "good"},
    state=[["answer", f"[{found[0]}, {found[1]}]"], ["comparisons", work]])

# ---- Act 1: the waste ----
add(act=1,
    intro="how fast the comparison counter climbed — that is the work we delete.",
    note=f"i=0 checked 3 pairs, i=1 checked 2, i=2 checked 1 = {work} checks. Each i "
    f"re-walks the tail the last i already walked.",
    marks={str(k): "dim" for k in range(len(nums))},
    state=[["comparisons (brute)", work], ["pattern", "~ n*n / 2"]])
add(act=1,
    note="For n numbers that is about n(n-1)/2. n=1000 → ~500,000 checks. The repeated "
    "tail-walking is the whole waste.",
    marks={str(k): "dim" for k in range(len(nums))},
    state=[["at n=1000", "~500,000"], ["what we want", "~1,000"]])

# ---- Act 2: fast hash map ----
seen = {}
checks = 0


def sidebar():
    return {"title": "seen (value → index)", "rows": [[str(k), str(v)] for k, v in seen.items()]}


add(act=2, code="fast", line=0,
    intro="the partner is FOUND in the map, never searched for.",
    invariant="seen holds every value to the left of i.",
    note="Same target, but remember as we go. Each x has one forced partner: target - x.",
    pointers={"i": 0}, marks={"0": "active"}, sidebar=sidebar(),
    state=[["target", T], ["checks", 0]])
for i, x in enumerate(nums):
    need = T - x
    checks += 1
    add(act=2, code="fast", line=3,
        note=f"x = {x}. Partner needed = {T} - {x} = {need}. Is {need} in seen?",
        pointers={"i": i}, marks={str(i): "active"}, sidebar=sidebar(),
        state=[["i", i], ["x", x], ["need", need], ["checks", checks]])
    if need in seen:
        j = seen[need]
        add(act=2, code="fast", line=4,
            note=f"Yes — {need} was filed at index {j}. One pass, no tail sweeps.",
            pointers={"i": i}, arc=[j, i], marks={str(j): "good", str(i): "good"},
            sidebar=sidebar(),
            state=[["answer", f"[{j}, {i}]"], ["checks", checks], ["vs brute", work]],
            banner=f"Found [{j}, {i}]   {nums[j]} + {nums[i]} = {T}   — {checks} checks vs {work} brute")
        break
    seen[x] = i
    add(act=2, code="fast", line=5,
        note=f"No. File {x} → {i} into seen and step right.",
        pointers={"i": i}, marks={str(i): "dim"}, sidebar=sidebar(),
        state=[["i", i], ["filed", f"{x}→{i}"], ["checks", checks]])

# ---- Act 3: edge case ----
edge = [3, 3]
seen = {}
add(act=3, cells=edge, labels=[0, 1], code="fast", line=0,
    intro="we check BEFORE we file — that is why a lone 3 can't pair with itself.",
    invariant="a value is only in seen if it sat at an earlier index.",
    note="Edge case: two equal numbers, target 6. Does 3 pair with itself?",
    pointers={"i": 0}, marks={"0": "active"}, sidebar=sidebar(),
    state=[["target", 6]])
for i, x in enumerate(edge):
    need = 6 - x
    if need in seen:
        j = seen[need]
        add(act=3, code="fast", line=4,
            note=f"x=3 at index {i}. A different 3 was filed at index {j} — a real pair.",
            pointers={"i": i}, arc=[j, i], marks={str(j): "good", str(i): "good"},
            sidebar=sidebar(), state=[["answer", "[0, 1]"]],
            banner="Found [0, 1]   3 + 3 = 6")
        break
    add(act=3, code="fast", line=5,
        note=f"x=3 at index {i}. seen is empty, so file 3 → {i}. The lone 3 can't match itself.",
        pointers={"i": i}, marks={str(i): "dim"}, sidebar=sidebar(),
        state=[["i", i], ["filed", f"3→{i}"]])
    seen[x] = i

trace = {
    "player": "linear",
    "title": "Two Sum — from every-pair to one honest pass",
    "acts": ["Brute force: every pair", "The waste", "Fast: hash map", "Edge case: [3, 3]"],
    "code": {"brute": BRUTE, "fast": FAST},
    "legend": [["active", "current i / x"], ["good", "the matching pair"], ["dim", "filed / skipped"]],
    "cells": nums, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
