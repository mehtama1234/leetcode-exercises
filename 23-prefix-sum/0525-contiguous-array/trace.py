"""Rich full-arc trace for Contiguous Array, mirroring find_max_length in
solution.py. Shows the brute force re-walking every tail, names the waste, then
relabels 0 -> -1 and runs the one-pass prefix-balance + first-seen map (equal
prefixes bracket a balanced run) with a live sidebar, and finishes on a
never-balances edge case. Writes trace.json.
"""
import json
import os

nums = [0, 0, 1, 0, 0, 0, 1, 1]  # answer 6
frames = []

BRUTE = [
    "best = 0",
    "for start in range(n):",
    "    balance = 0",
    "    for end in range(start, n):",
    "        balance += 1 if nums[end]==1 else -1",
    "        if balance == 0:",
    "            best = max(best, end - start + 1)",
]
FAST = [
    "best, balance = 0, 0",
    "first_seen = {0: -1}",
    "for i, x in enumerate(nums):",
    "    balance += 1 if x==1 else -1",
    "    if balance in first_seen:",
    "        best = max(best, i - first_seen[balance])",
    "    else:",
    "        first_seen[balance] = i",
]


def add(**f):
    frames.append(f)


# ---- Act 0: brute force — every subarray's balance ----
work = 0
best = 0
bnums = nums[:5]  # [0, 0, 1, 0, 0]; the full array runs in the fast act
add(act=0, cells=bnums, labels=list(range(len(bnums))), code="brute", line=1,
    intro="each start re-walks the tail counting balance from zero — the same steps, redone.",
    invariant="best = longest balanced subarray found among all starts tried so far.",
    note="Brute force: for each start, walk the tail tracking balance (1 -> +1, 0 -> -1); "
         "balance 0 means equal 0s and 1s.",
    pointers={"start": 0}, marks={"0": "active"},
    state=[["best", 0], ["steps", 0]])
for start in range(len(bnums)):
    balance = 0
    for end in range(start, len(bnums)):
        balance += 1 if bnums[end] == 1 else -1
        work += 1
        bal0 = balance == 0
        if bal0:
            best = max(best, end - start + 1)
        add(act=0, code="brute", line=6 if bal0 else 4,
            note=f"start {start}..end {end}: balance = {balance}."
                 + (f" Balanced! length {end-start+1}, best {best}." if bal0 else ""),
            pointers={"start": start, "end": end}, window=[start, end],
            marks={**{str(m): ("good" if bal0 else "active") for m in range(start, end + 1)},
                   str(start): "active"},
            state=[["start", start], ["end", end], ["balance", balance],
                   ["best", best], ["steps", work]])
add(act=0, code="brute", line=6,
    note=f"On five numbers that took {work} steps, each start re-walking the same tail. "
         "It grows as the square of the length.",
    marks={str(m): "dim" for m in range(len(bnums))},
    state=[["best (slice)", best], ["steps", work]])

# ---- Act 1: the waste ----
add(act=1,
    intro="relabel 0 -> -1 and 'equal 0s and 1s' becomes 'the run sums to 0' — a prefix-sum question.",
    note="Replace each 0 with -1. Then a run is balanced when its sum is 0, i.e. its two "
         "end prefixes are EQUAL: prefix[i] == prefix[j+1].",
    marks={str(m): "dim" for m in range(len(nums))},
    state=[["steps (brute)", work], ["insight", "equal prefixes bracket balance"]])
add(act=1,
    note="So the longest balanced run ending at j is j minus the FIRST index where that "
         "prefix value appeared. Remember each prefix's earliest index — one pass.",
    marks={str(m): "dim" for m in range(len(nums))},
    state=[["remember", "earliest index per prefix"], ["cost", "one pass"]])

# ---- Act 2: one pass, first-seen map ----
best = 0
balance = 0
first_seen = {0: -1}


def sb():
    return {"title": "first_seen (prefix -> earliest index)",
            "rows": [[str(kk), str(vv)] for kk, vv in first_seen.items()]}


add(act=2, cells=nums, code="fast", line=1,
    intro="the sidebar keeps the FIRST index each balance appeared. Seed {0:-1} lets runs from the very start count.",
    invariant="first_seen[b] is the earliest index whose prefix balance is b.",
    note="One pass. balance = running prefix (0 -> -1). first_seen = earliest index per "
         "balance value. Seed {0: -1}.",
    pointers={"i": 0}, marks={"0": "active"}, sidebar=sb(),
    state=[["balance", 0], ["best", 0]])
for i, x in enumerate(nums):
    balance += 1 if x == 1 else -1
    if balance in first_seen:
        j = first_seen[balance]
        length = i - j
        beat = length > best
        if beat:
            best = length
        add(act=2, code="fast", line=5,
            note=f"i={i}, x={x}: balance = {balance}, first seen at index {j}. Balanced "
                 f"run {j+1}..{i}, length {length}." + (f" New best {best}." if beat else f" best stays {best}."),
            pointers={"i": i}, window=[j + 1, i], arc=[max(j, 0), i],
            marks={**{str(m): "good" for m in range(j + 1, i + 1)}, str(i): "active"},
            sidebar=sb(),
            state=[["i", i], ["balance", balance], ["first at", j], ["length", length],
                   ["best", best]])
    else:
        first_seen[balance] = i
        add(act=2, code="fast", line=7,
            note=f"i={i}, x={x}: balance = {balance}, new value. File first_seen[{balance}] "
                 f"= {i}.",
            pointers={"i": i}, marks={str(i): "dim"}, sidebar=sb(),
            state=[["i", i], ["balance", balance], ["filed", f"{balance}->{i}"],
                   ["best", best]])
add(act=2, code="fast", line=5,
    note=f"One pass gives best = {best}: the longest stretch bracketed by two equal "
         "prefix balances.",
    marks={str(m): "dim" for m in range(len(nums))}, sidebar=sb(),
    state=[["answer", best], ["brute (5 nums)", work]],
    banner=f"Longest balanced subarray = {best}   — one pass")

# ---- Act 3: edge case — never balances ----
edge = [1, 1, 1, 1]  # answer 0
best = 0
balance = 0
first_seen = {0: -1}
add(act=3, cells=edge, labels=[0, 1, 2, 3], code="fast", line=1,
    intro="all 1s: balance only ever climbs, so no prefix value repeats — nothing is balanced.",
    invariant="best stays 0 unless a prefix balance recurs.",
    note="Edge case: [1,1,1,1]. Every step adds +1, so balance never repeats and no run "
         "is balanced.",
    pointers={"i": 0}, marks={"0": "active"}, sidebar=sb(),
    state=[["balance", 0], ["best", 0]])
for i, x in enumerate(edge):
    balance += 1 if x == 1 else -1
    if balance in first_seen:
        best = max(best, i - first_seen[balance])
        add(act=3, code="fast", line=5,
            note=f"balance {balance} seen before — but this input never repeats a value.",
            pointers={"i": i}, sidebar=sb(),
            state=[["i", i], ["balance", balance], ["best", best]])
    else:
        first_seen[balance] = i
        add(act=3, code="fast", line=7,
            note=f"i={i}: balance = {balance}, brand new. File it. best stays {best}.",
            pointers={"i": i}, marks={str(i): "dim"}, sidebar=sb(),
            state=[["i", i], ["balance", balance], ["best", best]])
add(act=3, code="fast", line=5,
    note=f"best = {best}: no two prefixes matched, so nothing balanced. All-1s can't be "
         "split evenly.",
    marks={str(m): "dim" for m in range(len(edge))}, sidebar=sb(),
    state=[["answer", best]],
    banner="[1,1,1,1] -> 0 (never balances)")

trace = {
    "player": "linear",
    "title": "Contiguous Array — relabel to prefix sums, one pass",
    "acts": ["Brute force: every subarray", "The waste",
             "Fast: relabel + first-seen map", "Edge case: never balances"],
    "code": {"brute": BRUTE, "fast": FAST},
    "legend": [["active", "current index i"], ["good", "a balanced run"],
               ["dim", "prefix filed into the map"]],
    "cells": nums, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
