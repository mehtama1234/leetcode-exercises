"""Rich full-arc trace for Maximum Subarray, mirroring both functions in
solution.py. Shows the brute force re-summing the same tails, names the waste,
then runs Kadane's greedy pass with the live cur/best choice, and finishes on the
all-negative edge case. Writes trace.json.
"""
import json
import os

nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]  # answer 6 = [4, -1, 2, 1]
frames = []

BRUTE = [
    "best = nums[0]",
    "for i in range(n):",
    "    running = 0",
    "    for j in range(i, n):",
    "        running += nums[j]",
    "        if running > best:",
    "            best = running",
]
FAST = [
    "cur = nums[0]",
    "best = nums[0]",
    "for x in nums[1:]:",
    "    cur = max(x, cur + x)",
    "    best = max(best, cur)",
]


def add(**f):
    frames.append(f)


# ---- Act 0: brute force — every subarray (on a short slice, so the waste is countable) ----
bnums = nums[:5]  # [-2, 1, -3, 4, -1]; the full array runs in the fast act
work = 0
best = bnums[0]
add(act=0, cells=bnums, labels=list(range(len(bnums))), code="brute", line=1,
    intro="every start i re-adds the same tail from scratch — watch running climb from 0 again and again.",
    invariant="best holds the largest subarray sum among all starts tried before this i.",
    note="Brute force: for each start i, extend the end j and keep the running sum. "
         f"Best so far = {best}.",
    pointers={"i": 0}, marks={"0": "active"},
    state=[["i", 0], ["best", best], ["additions", 0]])
for i in range(len(bnums)):
    running = 0
    for j in range(i, len(bnums)):
        running += bnums[j]
        work += 1
        beat = running > best
        if beat:
            best = running
        add(act=0, code="brute", line=6 if beat else 4,
            note=f"start {i}, end {j}: running = {running}."
                 + (f" New best {best}." if beat else f" Best stays {best}."),
            pointers={"i": i, "j": j}, window=[i, j],
            marks={**{str(k): "good" for k in range(i, j + 1)}, str(i): "active"},
            state=[["i", i], ["j", j], ["running", running], ["best", best],
                   ["additions", work]])
add(act=0, code="brute", line=6,
    note=f"On just five numbers that took {work} additions, and most re-added tails "
         "already summed. It grows as the square of the length.",
    marks={str(k): "dim" for k in range(len(bnums))},
    state=[["answer (slice)", best], ["additions", work]])

# ---- Act 1: the waste ----
add(act=1,
    intro="how the addition counter ballooned — each start re-walks a tail its neighbour just walked.",
    note=f"{work} additions for 5 numbers. start 0 summed 5 tails, start 1 summed 4, "
         "and so on — the same suffixes, re-added.",
    marks={str(k): "dim" for k in range(len(nums))},
    state=[["additions (brute)", work], ["pattern", "~ n*n / 2"]])
add(act=1,
    note="For n numbers that is about n(n-1)/2. n=1000 -> ~500,000 additions. We want "
         "one pass that never re-sums a tail.",
    marks={str(k): "dim" for k in range(len(nums))},
    state=[["at n=1000", "~500,000"], ["what we want", "~1,000"]])

# ---- Act 2: Kadane's greedy pass ----
cur = nums[0]
best = nums[0]
add(act=2, cells=nums, code="fast", line=1,
    intro="at each x the choice is only: start fresh at x, or glue x onto cur. best just records the peak.",
    invariant="cur = best subarray sum ENDING at the current index; best = largest cur seen so far.",
    note=f"Kadane: cur = best subarray ending here, best = largest anywhere. "
         f"Seed both with nums[0] = {nums[0]}.",
    pointers={"here": 0}, marks={"0": "active"},
    state=[["cur", cur], ["best", best], ["additions", 0]])
runwork = 0
for idx in range(1, len(nums)):
    x = nums[idx]
    extend = cur + x
    runwork += 1
    restart = x >= extend
    cur = max(x, extend)
    prev_best = best
    best = max(best, cur)
    grew = best > prev_best
    if restart:
        choice = f"drop the negative prefix, start fresh at {x}"
    else:
        choice = f"glue {x} onto cur -> {cur}"
    add(act=2, code="fast", line=3,
        note=f"x = {x}: max({x}, cur+{x}={extend}) = {cur}. " + choice + "."
             + (f" best rises to {best}." if grew else f" best stays {best}."),
        pointers={"here": idx}, window=[idx, idx] if restart else None,
        marks={**({str(idx): "active"} if restart
                  else {str(k): "good" for k in range(idx)}),
               str(idx): "active"},
        state=[["x", x], ["cur+x", extend], ["cur", cur], ["best", best],
               ["additions", runwork]])
add(act=2, code="fast", line=4,
    note=f"One pass over all nine numbers: {runwork} additions, best = {best}, the sum of "
         "[4, -1, 2, 1]. Brute needed that many just for five.",
    marks={"3": "good", "4": "good", "5": "good", "6": "good"},
    state=[["answer", best], ["additions", runwork], ["brute (5 nums)", work]],
    banner=f"Max subarray sum = {best}   ([4, -1, 2, 1])   — {runwork} additions, one pass")

# ---- Act 3: edge case — all negative ----
edge = [-3, -1, -2]
cur = edge[0]
best = edge[0]
add(act=3, cells=edge, labels=[0, 1, 2], code="fast", line=0,
    intro="with no positive number, cur+x is always worse than x alone — so cur just tracks single elements.",
    invariant="a subarray must hold at least one element, so best can be negative.",
    note="Edge case: all negative. We must still return one element — the least negative.",
    pointers={"here": 0}, marks={"0": "active"},
    state=[["cur", cur], ["best", best]])
for idx in range(1, len(edge)):
    x = edge[idx]
    extend = cur + x
    cur = max(x, extend)
    best = max(best, cur)
    add(act=3, code="fast", line=3,
        note=f"x = {x}: max({x}, {extend}) = {cur}. Carrying the prefix only hurts, so "
             f"cur restarts at {x}. best = {best}.",
        pointers={"here": idx}, marks={str(idx): "active"},
        state=[["x", x], ["cur", cur], ["best", best]])
add(act=3, code="fast", line=4,
    note=f"best = {best} — the single least-negative element (-1). Kadane never picks "
         "the empty subarray.",
    marks={"1": "good"},
    state=[["answer", best]],
    banner=f"All negative -> {best}   (the one least-negative element)")

trace = {
    "player": "linear",
    "title": "Maximum Subarray — from every-subarray to one greedy pass (Kadane's)",
    "acts": ["Brute force: every subarray", "The waste", "Fast: Kadane's greedy",
             "Edge case: all negative"],
    "code": {"brute": BRUTE, "fast": FAST},
    "legend": [["active", "current index x"], ["good", "the running / best subarray"],
               ["dim", "filed / discarded"]],
    "cells": nums, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
