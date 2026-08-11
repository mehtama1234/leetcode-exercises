"""Full-arc trace for 3Sum: brute every triple -> the waste -> sort + fix an anchor
+ two-pointer the tail (Two Sum, n times) -> edge case (duplicates must not repeat).
Mirrors solution.py. Writes trace.json.
"""
import json
import os

nums = [-1, 0, 1, 2, -1, -4]  # answer [[-1,-1,2], [-1,0,1]]
frames = []

BRUTE = [
    "for i in range(n):",
    "  for j in range(i+1, n):",
    "    for k in range(j+1, n):",
    "      if nums[i]+nums[j]+nums[k] == 0:",
    "        found.add(sorted triple)",
]
FAST = [
    "nums = sorted(nums)",
    "for i in range(n):",
    "  if nums[i] == nums[i-1]: continue   # skip dup anchor",
    "  left, right = i+1, n-1",
    "  while left < right:",
    "    s = nums[i] + nums[left] + nums[right]",
    "    if s < 0: left += 1",
    "    elif s > 0: right -= 1",
    "    else: record; skip dups; move both",
]


def add(**f):
    frames.append(f)


# ---- Act 0: brute force — every triple ----
work = 0
found = set()
add(act=0, cells=nums, labels=list(range(len(nums))), code="brute", line=0,
    intro="three nested loops — each element re-scans two tails behind it.",
    invariant="every ordered triple before this i,j,k has been summed.",
    note="Brute force: sum every triple, keep the ones that hit zero (dedupe with a set).",
    pointers={"i": 0, "j": 1, "k": 2},
    marks={"0": "active", "1": "dim", "2": "dim"},
    state=[["i", 0], ["j", 1], ["k", 2], ["triples", 0]])
n = len(nums)
for i in range(n):
    for j in range(i + 1, n):
        for k in range(j + 1, n):
            work += 1
            hit = nums[i] + nums[j] + nums[k] == 0
            if hit:
                found.add(tuple(sorted((nums[i], nums[j], nums[k]))))
            # surface only zero-hits and the very first few to stay readable
            if hit or work <= 3:
                add(act=0, code="brute", line=3 if hit else 2,
                    note=f"triple ({nums[i]},{nums[j]},{nums[k]}) sums to "
                         f"{nums[i]+nums[j]+nums[k]}. " + ("Zero — keep it." if hit else "Not zero."),
                    pointers={"i": i, "j": j, "k": k}, arc=[i, k],
                    marks={str(i): "active",
                           str(j): "good" if hit else "dim",
                           str(k): "good" if hit else "dim"},
                    state=[["i", i], ["j", j], ["k", k],
                           ["sum", nums[i] + nums[j] + nums[k]], ["triples", work]])
add(act=0, code="brute", line=4,
    note=f"Found {len(found)} unique triplets — but it summed {work} triples for "
         f"{n} numbers. That's n-cubed work.",
    marks={str(k): "dim" for k in range(n)},
    state=[["unique triplets", len(found)], ["triples", work]])

# ---- Act 1: the waste ----
add(act=1,
    intro="the triple counter — n-cubed — is the pile we cut down to n-squared.",
    note=f"{work} triples for 6 numbers. In general ~n-cubed, and we still had to dedupe "
    "with a set. Sorting first fixes both problems at once.",
    marks={str(k): "dim" for k in range(n)},
    state=[["triples (brute)", work], ["pattern", "~ n*n*n"]])
add(act=1,
    note="Sort the array. Then fix one number nums[i]; the other two must sum to -nums[i] "
    "— that's Two Sum on a sorted tail, solvable by converging pointers in one pass.",
    marks={str(k): "dim" for k in range(n)},
    state=[["pattern", "sort + n * TwoSum"], ["result", "~ n*n"]])

# ---- Act 2: fast — sort, fix anchor, two-pointer the tail ----
snums = sorted(nums)
add(act=2, cells=snums, labels=list(range(len(snums))), code="fast", line=0,
    intro="equal numbers now sit together, so skipping a repeat kills duplicate triplets.",
    invariant="results holds every unique zero triplet whose anchor index is < i.",
    note=f"Sorted: {snums}. Fix an anchor i, two-pointer the tail for -nums[i].",
    pointers={"i": 0},
    marks={"0": "active"},
    state=[["sorted", str(snums)], ["result", "[]"]])
result = []
steps = 0
for i in range(n):
    if snums[i] > 0:
        add(act=2, code="fast", line=1,
            note=f"nums[{i}] = {snums[i]} > 0. Sorted, so every remaining triple is "
                 "positive — no zero left. Stop.",
            pointers={"i": i}, marks={str(i): "dim"},
            state=[["nums[i]", snums[i]], ["result", str(result)]])
        break
    if i > 0 and snums[i] == snums[i - 1]:
        add(act=2, code="fast", line=2,
            note=f"nums[{i}] = {snums[i]} repeats nums[{i-1}] — skip this anchor to avoid "
                 "re-finding the same triplets.",
            pointers={"i": i}, marks={str(i): "dim"},
            state=[["nums[i]", snums[i]], ["skip", "duplicate anchor"]])
        continue
    left, right = i + 1, n - 1
    add(act=2, code="fast", line=3,
        note=f"Anchor nums[{i}] = {snums[i]}. Two-pointer the tail for two numbers "
             f"summing to {-snums[i]}.",
        pointers={"i": i, "L": left, "R": right}, window=[left, right],
        marks={str(i): "active", str(left): "active", str(right): "active"},
        state=[["anchor", snums[i]], ["need", -snums[i]], ["left", left], ["right", right]])
    while left < right:
        s = snums[i] + snums[left] + snums[right]
        steps += 1
        if s < 0:
            add(act=2, code="fast", line=6,
                note=f"{snums[i]}+{snums[left]}+{snums[right]} = {s} < 0 — grow it, move left in.",
                pointers={"i": i, "L": left, "R": right}, window=[left, right],
                marks={str(i): "active", str(left): "active", str(right): "active"},
                state=[["sum", s], ["left", left], ["right", right]])
            left += 1
        elif s > 0:
            add(act=2, code="fast", line=7,
                note=f"{snums[i]}+{snums[left]}+{snums[right]} = {s} > 0 — shrink it, move right in.",
                pointers={"i": i, "L": left, "R": right}, window=[left, right],
                marks={str(i): "active", str(left): "active", str(right): "active"},
                state=[["sum", s], ["left", left], ["right", right]])
            right -= 1
        else:
            result.append([snums[i], snums[left], snums[right]])
            add(act=2, code="fast", line=8,
                note=f"{snums[i]}+{snums[left]}+{snums[right]} = 0 — record "
                     f"[{snums[i]}, {snums[left]}, {snums[right]}], then skip dups both sides.",
                pointers={"i": i, "L": left, "R": right}, window=[left, right], arc=[left, right],
                marks={str(i): "good", str(left): "good", str(right): "good"},
                state=[["found", f"[{snums[i]}, {snums[left]}, {snums[right]}]"],
                       ["result count", len(result)]])
            left += 1
            right -= 1
            while left < right and snums[left] == snums[left - 1]:
                left += 1
            while left < right and snums[right] == snums[right + 1]:
                right -= 1
add(act=2, code="fast", line=8,
    note=f"One anchor sweep each, no set needed. Triplets: {result}.",
    marks={str(k): "dim" for k in range(n)},
    state=[["result", str(result)], ["pointer moves", steps], ["vs brute triples", work]],
    banner=f"3Sum = {result}   — ~n*n moves vs {work} brute triples")

# ---- Act 3: edge case, all duplicates ----
edge = [0, 0, 0, 0]  # answer exactly one [0,0,0]
sedge = sorted(edge)
add(act=3, cells=sedge, labels=list(range(len(sedge))), code="fast", line=2,
    intro="duplicate-skipping stops [0,0,0] from being reported four times.",
    invariant="an anchor equal to its predecessor is skipped outright.",
    note="Edge case: four zeros. The triplet [0,0,0] exists, but must appear only once.",
    pointers={"i": 0, "L": 1, "R": 3}, window=[1, 3],
    marks={"0": "active", "1": "active", "3": "active"},
    state=[["nums", str(sedge)]])
eres = []
ne = len(sedge)
for i in range(ne):
    if i > 0 and sedge[i] == sedge[i - 1]:
        add(act=3, code="fast", line=2,
            note=f"anchor at i={i} is another 0 — skip it, or we'd report [0,0,0] again.",
            pointers={"i": i}, marks={str(i): "dim"},
            state=[["skip", "duplicate anchor"], ["result count", len(eres)]])
        continue
    left, right = i + 1, ne - 1
    while left < right:
        s = sedge[i] + sedge[left] + sedge[right]
        if s == 0:
            eres.append([0, 0, 0])
            add(act=3, code="fast", line=8,
                note="0+0+0 = 0 — record [0,0,0] once, then dup-skip collapses the rest.",
                pointers={"i": i, "L": left, "R": right}, window=[left, right], arc=[left, right],
                marks={str(i): "good", str(left): "good", str(right): "good"},
                state=[["found", "[0, 0, 0]"], ["result count", len(eres)]])
            left += 1
            right -= 1
            while left < right and sedge[left] == sedge[left - 1]:
                left += 1
            while left < right and sedge[right] == sedge[right + 1]:
                right -= 1
        elif s < 0:
            left += 1
        else:
            right -= 1
add(act=3, code="fast", line=8,
    note=f"Result: {eres}. Exactly one triplet despite four zeros.",
    marks={str(k): "dim" for k in range(ne)},
    state=[["result", str(eres)]],
    banner="3Sum = [[0, 0, 0]]   (one triplet, not four)")

trace = {
    "player": "linear",
    "title": "3Sum — from every triple to sort + Two Sum n times",
    "acts": ["Brute force: every triple", "The waste",
             "Fast: sort + fix anchor + two pointers", "Edge case: all zeros"],
    "code": {"brute": BRUTE, "fast": FAST},
    "legend": [["active", "anchor / pointers in play"], ["good", "a zero triplet"],
               ["dim", "discarded / skipped"]],
    "cells": nums, "labels": list(range(len(nums))), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
