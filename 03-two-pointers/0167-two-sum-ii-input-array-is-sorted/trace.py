"""Full-arc trace for Two Sum II (sorted input): brute every pair -> the waste ->
converging two pointers that use the sort -> edge case (duplicates). Mirrors
solution.py. Writes trace.json.
"""
import json
import os

numbers = [2, 7, 11, 15]
T = 9  # answer 1-indexed [1, 2]
frames = []

BRUTE = [
    "for i in range(n):",
    "    for j in range(i+1, n):",
    "        if numbers[i] + numbers[j] == target:",
    "            return [i+1, j+1]",
]
FAST = [
    "left, right = 0, n-1",
    "while left < right:",
    "    s = numbers[left] + numbers[right]",
    "    if s == target: return [left+1, right+1]",
    "    if s < target: left += 1",
    "    else: right -= 1",
]


def add(**f):
    frames.append(f)


def marks_all(vals, cls):
    return {str(k): cls for k in range(len(vals))}


# ---- Act 0: brute force — every pair, ignoring the sort ----
work = 0
found = None
add(act=0, cells=numbers, labels=list(range(len(numbers))), code="brute", line=0,
    intro="the pairs are tested blind — the fact that the array is sorted is thrown away.",
    invariant="every pair before this i,j has been tested in order.",
    note=f"Brute force: test every pair against target {T}, ignoring that it's sorted.",
    pointers={"i": 0, "j": 1}, marks={"0": "active", "1": "dim"},
    state=[["i", 0], ["j", 1], ["target", T], ["pairs", 0]])
for i in range(len(numbers)):
    for j in range(i + 1, len(numbers)):
        work += 1
        s = numbers[i] + numbers[j]
        hit = s == T
        add(act=0, code="brute", line=2 if not hit else 3,
            note=f"numbers[{i}]+numbers[{j}] = {numbers[i]}+{numbers[j]} = {s}. "
                 + ("Match." if hit else f"Not {T}."),
            pointers={"i": i, "j": j}, arc=[i, j],
            marks={str(i): "active", str(j): "good" if hit else "dim"},
            state=[["i", i], ["j", j], ["sum", s], ["pairs", work]])
        if hit:
            found = (i, j)
            break
    if found:
        break
add(act=0, code="brute", line=3,
    note=f"Found [{found[0]+1}, {found[1]+1}] — but it cost {work} pairs and used nothing "
         "about the array being sorted.",
    pointers={"i": found[0], "j": found[1]}, arc=list(found),
    marks={str(found[0]): "good", str(found[1]): "good"},
    state=[["answer", f"[{found[0]+1}, {found[1]+1}]"], ["pairs", work]])

# ---- Act 1: the waste ----
add(act=1,
    intro="the sort is a free fact — brute paid nothing for it, so it earned nothing.",
    note=f"{work} pairs here, but ~n*n/2 in general. The array is sorted: the sum at the "
    "two ends already tells us which way to move. Brute never asked.",
    marks=marks_all(numbers, "dim"),
    state=[["pairs (brute)", work], ["pattern", "~ n*n / 2"]])
add(act=1,
    note="Put one pointer at the smallest value, one at the largest. Too big? shrink the "
    "big end. Too small? grow the small end. Each move drops a value that can't be in any "
    "answer.",
    marks=marks_all(numbers, "dim"),
    state=[["at n=1000", "~500,000"], ["what we want", "~1,000"]])

# ---- Act 2: fast, converging two pointers ----
left, right = 0, len(numbers) - 1
add(act=2, cells=numbers, labels=list(range(len(numbers))), code="fast", line=0,
    intro="the sum steers the pointers — no value is ever revisited.",
    invariant="the answer, if any, lies within [left, right].",
    note="Two pointers at the ends. The end sum tells us which side to move.",
    pointers={"L": left, "R": right}, window=[left, right],
    marks={str(left): "active", str(right): "active"},
    state=[["target", T], ["left", left], ["right", right]])
while left < right:
    s = numbers[left] + numbers[right]
    if s == T:
        add(act=2, code="fast", line=3,
            note=f"{numbers[left]} + {numbers[right]} = {T}. Exactly the target.",
            pointers={"L": left, "R": right}, window=[left, right], arc=[left, right],
            marks={str(left): "good", str(right): "good"},
            state=[["answer", f"[{left+1}, {right+1}]"], ["steps", "one pass"], ["vs brute", work]],
            banner=f"Found [{left+1}, {right+1}]   {numbers[left]} + {numbers[right]} = {T}")
        break
    too_big = s > T
    add(act=2, code="fast", line=4 if not too_big else 5,
        note=f"{numbers[left]} + {numbers[right]} = {s}. "
             + (f"Too big — shrink the right end." if too_big
                else f"Too small — grow the left end."),
        pointers={"L": left, "R": right}, window=[left, right], arc=[left, right],
        marks={str(left): "active", str(right): "active"},
        state=[["left", left], ["right", right], ["sum", s], ["target", T]])
    if too_big:
        right -= 1
    else:
        left += 1

# ---- Act 3: edge case, duplicates, answer in the middle ----
edge = [1, 2, 3, 4, 4, 9, 56, 90]
ET = 8  # answer [4, 5] (1-indexed): 4 + 4
left, right = 0, len(edge) - 1
add(act=3, cells=edge, labels=list(range(len(edge))), code="fast", line=0,
    intro="duplicates don't confuse it — the sum still points the way to the two 4s.",
    invariant="the answer, if any, lies within [left, right].",
    note=f"Edge case: duplicates and the answer buried in the middle. Target {ET}.",
    pointers={"L": left, "R": right}, window=[left, right],
    marks={str(left): "active", str(right): "active"},
    state=[["target", ET], ["left", left], ["right", right]])
while left < right:
    s = edge[left] + edge[right]
    if s == ET:
        add(act=3, code="fast", line=3,
            note=f"{edge[left]} + {edge[right]} = {ET}. The two 4s in the middle.",
            pointers={"L": left, "R": right}, window=[left, right], arc=[left, right],
            marks={str(left): "good", str(right): "good"},
            state=[["answer", f"[{left+1}, {right+1}]"]],
            banner=f"Found [{left+1}, {right+1}]   {edge[left]} + {edge[right]} = {ET}")
        break
    too_big = s > ET
    add(act=3, code="fast", line=4 if not too_big else 5,
        note=f"{edge[left]} + {edge[right]} = {s}. "
             + ("Too big — move right in." if too_big else "Too small — move left in."),
        pointers={"L": left, "R": right}, window=[left, right],
        marks={str(left): "active", str(right): "active"},
        state=[["left", left], ["right", right], ["sum", s]])
    if too_big:
        right -= 1
    else:
        left += 1

trace = {
    "player": "linear",
    "title": "Two Sum II — using the sort to converge in one pass",
    "acts": ["Brute force: every pair", "The waste",
             "Fast: converge from the ends", "Edge case: duplicates"],
    "code": {"brute": BRUTE, "fast": FAST},
    "legend": [["active", "the two pointers"], ["good", "the matching pair"],
               ["dim", "discarded"]],
    "cells": numbers, "labels": list(range(len(numbers))), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
