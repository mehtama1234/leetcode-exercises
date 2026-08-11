"""Full-arc trace for Maximum Average Subarray I: re-sum every window -> the waste
(the k-1 overlap re-added) -> slide a running sum (drop leaver, add newcomer) ->
edge case (k == 1). Mirrors solution.py. Writes trace.json.
"""
import json
import os

nums = [1, 12, -5, -6, 50, 3]
k = 4  # answer 12.75  (window [12,-5,-6,50] sum 51)
frames = []

BRUTE = [
    "for i in range(n - k + 1):",
    "    window_sum = sum(nums[i:i+k])",
    "    best = max(best, window_sum)",
    "return best / k",
]
FAST = [
    "window_sum = sum(nums[:k])",
    "best = window_sum",
    "for i in range(k, n):",
    "    window_sum += nums[i] - nums[i-k]",
    "    best = max(best, window_sum)",
    "return best / k",
]


def add(**f):
    frames.append(f)


# ---- Act 0: brute — re-sum each window from scratch ----
adds = 0
best = float("-inf")
best_i = 0
add(act=0, cells=nums, labels=list(range(len(nums))), code="brute", line=0,
    intro="every window is summed from zero — neighbours share k-1 numbers, re-added each time.",
    invariant="best holds the largest window sum among windows starting before i.",
    note=f"Brute force: for each start, add all {k} numbers fresh. Keep the biggest sum.",
    pointers={"start": 0}, window=[0, k - 1],
    marks={str(j): "active" for j in range(k)},
    state=[["start", 0], ["best sum", "-inf"], ["additions", 0]])
for i in range(len(nums) - k + 1):
    wsum = 0
    for j in range(i, i + k):
        wsum += nums[j]
        adds += 1
    better = wsum > best
    if better:
        best = wsum
        best_i = i
    add(act=0, code="brute", line=1,
        note=f"start {i}: sum(nums[{i}..{i+k-1}]) = {wsum} ({k} fresh adds). "
             + (f"New best {best}." if better else f"Best stays {best}."),
        pointers={"start": i}, window=[i, i + k - 1],
        marks={str(j): ("good" if better else "active") for j in range(i, i + k)},
        state=[["start", i], ["window sum", wsum], ["best sum", best], ["additions", adds]])
add(act=0, code="brute", line=3,
    note=f"Best sum {best} at start {best_i} → average {best/k}. But it did {adds} additions "
         f"for {len(nums)} numbers.",
    pointers={"start": best_i}, window=[best_i, best_i + k - 1],
    marks={str(j): "good" for j in range(best_i, best_i + k)},
    state=[["best average", best / k], ["additions", adds]])

# ---- Act 1: the waste ----
add(act=1,
    intro="the addition counter — k adds per window when only 2 ever change.",
    note=f"{adds} additions. Two neighbouring windows share {k-1} numbers; brute re-adds "
    "them every single step. That overlap is the whole waste.",
    marks={str(j): "dim" for j in range(len(nums))},
    state=[["additions (brute)", adds], ["pattern", "~ n*k"]])
add(act=1,
    note="Sliding a window one step drops just the leftmost number and gains one on the "
    "right. Keep a running sum and update it with two operations — never re-sum.",
    marks={str(j): "dim" for j in range(len(nums))},
    state=[["adds per step", 2], ["pattern", "~ n"]])

# ---- Act 2: fast — running sum ----
wsum = sum(nums[:k])
best = wsum
best_i = 0
ops = k  # the initial sum
add(act=2, cells=nums, labels=list(range(len(nums))), code="fast", line=0,
    intro="the sum is carried, not rebuilt — each slide is one add and one subtract.",
    invariant="window_sum always equals the sum of the current k-wide window.",
    note=f"Sum the first window once: {nums[:k]} = {wsum}. Now slide.",
    pointers={"L": 0, "R": k - 1}, window=[0, k - 1],
    marks={str(j): "active" for j in range(k)},
    state=[["window sum", wsum], ["best sum", best], ["ops", ops]])
for i in range(k, len(nums)):
    leaver = nums[i - k]
    newcomer = nums[i]
    wsum += newcomer - leaver
    ops += 2
    better = wsum > best
    if better:
        best = wsum
        best_i = i - k + 1
    add(act=2, code="fast", line=3,
        note=f"slide right: drop nums[{i-k}]={leaver}, add nums[{i}]={newcomer}. "
             f"sum {wsum}. " + (f"New best {best}." if better else f"Best {best}."),
        pointers={"L": i - k + 1, "R": i}, window=[i - k + 1, i],
        marks={**{str(i - k): "bad"},
               **{str(j): ("good" if better else "active") for j in range(i - k + 1, i + 1)}},
        state=[["dropped", leaver], ["added", newcomer], ["window sum", wsum],
               ["best sum", best], ["ops", ops]])
add(act=2, code="fast", line=5,
    note=f"Best window sum {best} at start {best_i} → average {best/k}. One add + one "
         f"subtract per step.",
    pointers={"L": best_i, "R": best_i + k - 1}, window=[best_i, best_i + k - 1],
    marks={str(j): "good" for j in range(best_i, best_i + k)},
    state=[["best average", best / k], ["ops", ops], ["vs brute", adds]],
    banner=f"Max average {best/k}   window {nums[best_i:best_i+k]}   — {ops} ops vs {adds} brute")

# ---- Act 3: edge case, k == 1 ----
edge = [0, 4, 0, 3, 2]
ek = 1  # answer 4.0 — just the max element
wsum = sum(edge[:ek])
best = wsum
best_i = 0
add(act=3, cells=edge, labels=list(range(len(edge))), code="fast", line=0,
    intro="a width-1 window has no overlap to reuse — it just walks the array picking the max.",
    invariant="window_sum equals the single element under the window.",
    note="Edge case: k = 1. Each window is one number, so the answer is just the maximum.",
    pointers={"L": 0, "R": 0}, window=[0, 0], marks={"0": "active"},
    state=[["window sum", wsum], ["best sum", best]])
for i in range(ek, len(edge)):
    wsum += edge[i] - edge[i - ek]
    better = wsum > best
    if better:
        best = wsum
        best_i = i
    add(act=3, code="fast", line=3,
        note=f"window = [{edge[i]}]. " + (f"New best {best}." if better else f"Best {best}."),
        pointers={"L": i, "R": i}, window=[i, i],
        marks={str(i): "good" if better else "active"},
        state=[["value", edge[i]], ["best sum", best]])
add(act=3, code="fast", line=5,
    note=f"Largest single value {best} → average {best/ek}.",
    pointers={"L": best_i, "R": best_i}, window=[best_i, best_i],
    marks={str(best_i): "good"},
    state=[["best average", best / ek]],
    banner=f"Max average {best/ek}   (k=1, just the max element)")

trace = {
    "player": "linear",
    "title": "Maximum Average Subarray I — from re-summing to a running sum",
    "acts": ["Brute force: re-sum each window", "The waste",
             "Fast: slide a running sum", "Edge case: k = 1"],
    "code": {"brute": BRUTE, "fast": FAST},
    "legend": [["active", "current window"], ["good", "best window so far"],
               ["bad", "number leaving the window"], ["dim", "inactive"]],
    "cells": nums, "labels": list(range(len(nums))), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
