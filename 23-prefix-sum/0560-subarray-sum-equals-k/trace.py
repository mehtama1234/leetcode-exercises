"""Rich full-arc trace for Subarray Sum Equals K, mirroring subarray_sum in
solution.py. Shows the brute force re-walking every tail, names the waste, then
runs the one-pass prefix-sum + hash-map count with a live sidebar of prefix-sum
frequencies, and finishes on a negatives edge case. Writes trace.json.
"""
import json
import os

nums = [3, 4, 7, 2, -3, 1, 4, 2]
k = 7  # answer 4
frames = []

BRUTE = [
    "count = 0",
    "for start in range(n):",
    "    running = 0",
    "    for end in range(start, n):",
    "        running += nums[end]",
    "        if running == k:",
    "            count += 1",
]
FAST = [
    "count, running = 0, 0",
    "seen = {0: 1}",
    "for x in nums:",
    "    running += x",
    "    count += seen.get(running - k, 0)",
    "    seen[running] = seen.get(running, 0) + 1",
]


def add(**f):
    frames.append(f)


# ---- Act 0: brute force — every subarray ----
work = 0
count = 0
bnums = nums[:4]  # [3, 4, 7, 2]; the full array runs in the fast act
add(act=0, cells=bnums, labels=list(range(len(bnums))), code="brute", line=1,
    intro="every start re-adds the tail it shares with the start before it — the same running sums, recomputed.",
    invariant="count = number of subarrays tried so far that sum to k.",
    note=f"Brute force: for each start, extend end and keep a running sum; count when it "
         f"hits k = {k}.",
    pointers={"start": 0}, marks={"0": "active"},
    state=[["k", k], ["count", 0], ["additions", 0]])
for start in range(len(bnums)):
    running = 0
    for end in range(start, len(bnums)):
        running += bnums[end]
        work += 1
        hit = running == k
        if hit:
            count += 1
        add(act=0, code="brute", line=6 if hit else 4,
            note=f"start {start}..end {end}: running = {running}."
                 + (f" == {k}! count -> {count}." if hit else ""),
            pointers={"start": start, "end": end}, window=[start, end],
            marks={**{str(m): ("good" if hit else "active") for m in range(start, end + 1)},
                   str(start): "active"},
            state=[["start", start], ["end", end], ["running", running],
                   ["count", count], ["additions", work]])
add(act=0, code="brute", line=6,
    note=f"On four numbers that took {work} additions, most re-walking tails an earlier "
         "start already summed. It grows as the square of the length.",
    marks={str(m): "dim" for m in range(len(bnums))},
    state=[["count (slice)", count], ["additions", work]])

# ---- Act 1: the waste ----
add(act=1,
    intro="a subarray sum is a difference of two prefix sums — so we only need prefix sums, once.",
    note=f"{work} additions for just 4 numbers. A subarray (i..j) sums to k exactly when "
         "prefix[j+1] - prefix[i] == k. So prefix[i] == prefix[j+1] - k.",
    marks={str(m): "dim" for m in range(len(nums))},
    state=[["additions (brute)", work], ["pattern", "~ n*n / 2"]])
add(act=1,
    note="Sweep once holding the running prefix sum. At each step ask: how many earlier "
         "prefixes equal (running - k)? A count-map answers that in O(1).",
    marks={str(m): "dim" for m in range(len(nums))},
    state=[["question", "count of running - k"], ["cost", "one pass"]])

# ---- Act 2: one pass, prefix-sum count-map ----
count = 0
running = 0
seen = {0: 1}


def sb():
    return {"title": "seen (prefix sum -> count)",
            "rows": [[str(kk), str(vv)] for kk, vv in seen.items()]}


add(act=2, cells=nums, code="fast", line=1,
    intro="the sidebar counts how often each prefix sum has appeared. Seed {0:1} handles subarrays starting at index 0.",
    invariant="seen holds the frequency of every prefix sum for cells to the LEFT of the current one.",
    note=f"One pass. running = prefix sum so far; seen = how many times each prefix "
         "occurred. Seed seen = {0: 1}.",
    pointers={"x": 0}, marks={"0": "active"}, sidebar=sb(),
    state=[["k", k], ["running", 0], ["count", 0]])
for idx, x in enumerate(nums):
    running += x
    need = running - k
    hits = seen.get(need, 0)
    count += hits
    seen[running] = seen.get(running, 0) + 1
    add(act=2, code="fast", line=4,
        note=f"x = {x}: running = {running}. need = running - k = {running} - {k} = "
             f"{need}. seen has {need} {hits} time(s) -> count += {hits} (= {count}). "
             f"Then file running = {running}.",
        pointers={"x": idx}, marks={str(idx): "good" if hits else "active"}, sidebar=sb(),
        state=[["x", x], ["running", running], ["need", need], ["hits", hits],
               ["count", count]])
add(act=2, code="fast", line=5,
    note=f"One pass over all eight numbers finds {count} subarrays summing to {k}. Every "
         "subarray was counted by a single map lookup — no tail re-walking.",
    marks={str(m): "dim" for m in range(len(nums))}, sidebar=sb(),
    state=[["answer", count], ["brute (4 nums)", work]],
    banner=f"Subarrays summing to {k} = {count}   — one counted pass")

# ---- Act 3: edge case — negatives, sliding window fails ----
edge = [1, -1, 0]
ek = 0  # answer 3: [1,-1], [0], [1,-1,0]
count = 0
running = 0
seen = {0: 1}
add(act=3, cells=edge, labels=[0, 1, 2], code="fast", line=1,
    intro="negatives mean a longer subarray can sum LOWER — a sliding window can't work, but the count-map still does.",
    invariant="the count-map counts every earlier prefix, so it finds matches a window would miss.",
    note="Edge case: [1,-1,0], k=0. Negatives rule out a sliding window; prefix sums "
         "don't care.",
    pointers={"x": 0}, marks={"0": "active"}, sidebar=sb(),
    state=[["k", 0], ["running", 0], ["count", 0]])
for idx, x in enumerate(edge):
    running += x
    need = running - ek
    hits = seen.get(need, 0)
    count += hits
    add(act=3, code="fast", line=4,
        note=f"x = {x}: running = {running}. need = {need}. seen has it {hits} time(s) -> "
             f"count = {count}.",
        pointers={"x": idx}, marks={str(idx): "good" if hits else "active"}, sidebar=sb(),
        state=[["x", x], ["running", running], ["need", need], ["count", count]])
    seen[running] = seen.get(running, 0) + 1
add(act=3, code="fast", line=5,
    note=f"count = {count}: [1,-1], [0], and [1,-1,0] all sum to 0. The {{0:1}} seed and "
         "the repeated prefix 0 caught them all.",
    marks={"0": "good", "1": "good", "2": "good"}, sidebar=sb(),
    state=[["answer", count]],
    banner="[1,-1,0], k=0 -> 3 subarrays (negatives handled)")

trace = {
    "player": "linear",
    "title": "Subarray Sum Equals K — from every-subarray to one counted pass",
    "acts": ["Brute force: every subarray", "The waste",
             "Fast: prefix sum + count-map", "Edge case: negatives"],
    "code": {"brute": BRUTE, "fast": FAST},
    "legend": [["active", "current x"], ["good", "completes a subarray summing to k"],
               ["dim", "filed into the map"]],
    "cells": nums, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
