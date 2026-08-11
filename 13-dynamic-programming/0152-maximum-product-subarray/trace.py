"""Full-arc trace for Maximum Product Subarray (linear renderer).
Arc: brute re-multiplies every subarray -> the waste -> rolling max AND min in
one pass -> edge (sign flips). Mirrors solution.py. Writes trace.json.
"""
import json
import os

nums = [2, 3, -2, 4]  # answer 6: [2,3]
n = len(nums)
frames = []

BRUTE = [
    "best = nums[0]",
    "for i in range(n):",
    "    prod = 1",
    "    for j in range(i, n):",
    "        prod *= nums[j]",
    "        best = max(best, prod)",
]
FAST = [
    "best = cur_max = cur_min = nums[0]",
    "for x in nums[1:]:",
    "    cands = (x, cur_max*x, cur_min*x)",
    "    cur_max = max(cands)",
    "    cur_min = min(cands)",
    "    best = max(best, cur_max)",
]


def add(**f):
    frames.append(f)


# ---- Act 0: brute force ----
work = 0
best = nums[0]
add(act=0, cells=nums, code="brute", line=0,
    intro="j re-multiplies the whole tail for every start i — overlapping prefixes.",
    invariant="best holds the largest product of any subarray seen so far.",
    note="Brute force: for each start i, extend to each end j and keep a running "
    "product, tracking the best.",
    pointers={"i": 0, "j": 0}, marks={"0": "active"},
    state=[["best", best], ["multiplies", 0]])
for i in range(n):
    prod = 1
    for j in range(i, n):
        prod *= nums[j]
        work += 1
        best = max(best, prod)
        add(act=0, code="brute", line=5,
            note=f"subarray [{i}..{j}] product = {prod}. best = {best}.",
            pointers={"i": i, "j": j}, window=[i, j],
            marks={str(i): "active", str(j): "dim"},
            state=[["i", i], ["j", j], ["product", prod], ["best", best], ["multiplies", work]])
add(act=0, code="brute", line=5,
    note=f"Answer {best}, but it cost {work} multiplications on four numbers — every "
    "start re-multiplied the same prefix the previous start already did.",
    marks={"0": "good", "1": "good"}, window=[0, 1],
    state=[["answer", best], ["multiplies", work]])

# ---- Act 1: the waste ----
add(act=1,
    intro="the multiply counter climbing is the repeated prefix work.",
    note=f"n=4 cost {work} multiplies (~n*n/2). Every start re-walks the tail the "
    "previous start already walked. For n=1000 that is ~500,000.",
    marks={str(k): "dim" for k in range(n)},
    state=[["multiplies (brute)", work], ["pattern", "~ n*n / 2"]])
add(act=1,
    note="We want one pass. The catch: a negative flips sign, so the SMALLEST product "
    "so far can become the largest at the next negative. So we must carry both a "
    "running max and a running min.",
    marks={"2": "bad"}, state=[["hazard", "negatives flip sign"], ["carry", "max AND min"]])

# ---- Act 2: fast rolling max/min ----
best = cur_max = cur_min = nums[0]
add(act=2, cells=nums, code="fast", line=0,
    intro="one pass carrying both extremes; the min is there to catch a sign flip.",
    invariant="cur_max / cur_min = best & worst product of a subarray ending here.",
    note=f"Seed all three from nums[0] = {nums[0]}.",
    pointers={"x": 0}, marks={"0": "active"},
    state=[["cur_max", cur_max], ["cur_min", cur_min], ["best", best]])
for idx in range(1, n):
    x = nums[idx]
    cands = (x, cur_max * x, cur_min * x)
    cur_max = max(cands)
    cur_min = min(cands)
    best = max(best, cur_max)
    add(act=2, code="fast", line=5,
        note=f"x = {x}. candidates {cands} -> cur_max {cur_max}, cur_min {cur_min}. "
        f"best = {best}.",
        pointers={"x": idx}, marks={str(idx): "active"},
        state=[["x", x], ["cur_max", cur_max], ["cur_min", cur_min], ["best", best]])
add(act=2, code="fast", line=5,
    note=f"One pass, {n} steps, no re-multiplying. Answer {best}.",
    marks={"0": "good", "1": "good"}, window=[0, 1],
    state=[["answer", best], ["steps", n], ["vs brute", work]],
    banner=f"Max product = {best}  ([2, 3])  — {n} steps vs {work} brute multiplies")

# ---- Act 3: edge — the sign flip pays off ----
edge = [-2, 3, -4]  # answer 24: two negatives multiply big
best = cm = cn = edge[0]
add(act=3, cells=edge, labels=[0, 1, 2], code="fast", line=0,
    intro="watch the running min turn into the answer when the second negative lands.",
    invariant="the most-negative product is kept precisely so it can flip to largest.",
    note=f"Edge case {edge}: two negatives. Seed all three from {edge[0]}.",
    pointers={"x": 0}, marks={"0": "active"},
    state=[["cur_max", cm], ["cur_min", cn], ["best", best]])
for idx in range(1, len(edge)):
    x = edge[idx]
    cands = (x, cm * x, cn * x)
    cm = max(cands)
    cn = min(cands)
    best = max(best, cm)
    add(act=3, code="fast", line=5,
        note=f"x = {x}. candidates {cands} -> cur_max {cm}, cur_min {cn}. best = {best}.",
        pointers={"x": idx}, marks={str(idx): "active"},
        state=[["x", x], ["cur_max", cm], ["cur_min", cn], ["best", best]])
add(act=3, code="fast", line=5,
    note="The kept min (-6) times the last -4 became +24 — that is why we track the "
    "min. Answer 24.",
    marks={"0": "good", "1": "good", "2": "good"}, window=[0, 2],
    state=[["answer", best]], banner="Two negatives -> 24  (the min flipped to max)")

trace = {
    "player": "linear",
    "title": "Maximum Product Subarray - one pass carrying max AND min",
    "acts": ["Brute: every subarray", "The waste", "Fast: rolling max/min", "Edge: sign flip"],
    "code": {"brute": BRUTE, "fast": FAST},
    "legend": [["active", "current element"], ["good", "the winning subarray"], ["bad", "negative (sign flip)"], ["dim", "scanned"]],
    "cells": nums, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
