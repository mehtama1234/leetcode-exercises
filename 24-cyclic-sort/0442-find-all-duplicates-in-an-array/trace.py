"""Rich full-arc trace for Find All Duplicates in an Array, mirroring the two
functions in solution.py. Shows the O(n)-extra-space seen-set baseline, then the
sign-flip trick: negate the home index the first time; a home already negative
means its value is a duplicate. Writes trace.json.
"""
import json
import os

nums = [4, 3, 2, 7, 8, 2, 3, 1]  # answer: [2, 3]
frames = []

SET = [
    "seen = set()",
    "for x in nums:",
    "    if x in seen:",
    "        out.append(x)",
    "    seen.add(x)",
    "return out",
]
FAST = [
    "for x in nums:",
    "    v = abs(x)",
    "    home = v - 1",
    "    if nums[home] < 0:",
    "        out.append(v)",
    "    else:",
    "        nums[home] = -nums[home]",
]


def add(**f):
    frames.append(f)


# ---- Act 0: the seen-set baseline (O(n) extra memory) ----
n = len(nums)
add(act=0, cells=nums, code="set", line=0,
    intro="the set grows to n entries — the extra memory the trick removes.",
    invariant="seen holds every value from nums[0..i-1].",
    note="Baseline: keep a set of what we've seen; if a value is already in it, it's "
         "a duplicate. Correct, but the set is O(n) extra memory.",
    pointers={"x": 0}, marks={str(k): "dim" for k in range(n)},
    sidebar={"title": "seen (set)", "rows": []},
    state=[["extra memory", "O(n)"]])
seen = set()
dups_set = []
for i, x in enumerate(nums):
    dup = x in seen
    if dup:
        dups_set.append(x)
    add(act=0, code="set", line=2,
        note=f"nums[{i}] = {x}. " + (f"Already seen → duplicate." if dup else "New — file it."),
        pointers={"x": i},
        marks={str(i): "good" if dup else "active", **{str(k): "dim" for k in range(i)}},
        sidebar={"title": "seen (set)", "rows": [[str(s), "✓"] for s in sorted(seen)]},
        state=[["x", x], ["duplicate?", "yes" if dup else "no"],
               ["dups so far", str(dups_set) if dups_set else "—"]])
    seen.add(x)
add(act=0, code="set", line=5,
    note=f"Duplicates: {dups_set}. Correct, but paid for a full extra set.",
    marks={str(k): "dim" for k in range(n)},
    state=[["answer", str(dups_set)], ["extra memory", "O(n)"]])

# ---- Act 1: the idea — sign records the first visit ----
add(act=1,
    intro="the FIRST time we reach value v, flip its home negative; a second time, it's a dup.",
    note="Values are 1..n, so value v maps to home index v-1. Use the SIGN of the "
         "number parked there: positive = never reached v; negative = reached before.",
    marks={str(k): "dim" for k in range(n)},
    state=[["value v", "home v-1"], ["first visit", "flip negative"],
           ["home already <0", "v is a duplicate"]])
add(act=1,
    note="Read abs(x) since a slot may already be flipped. One pass, no extra memory: "
         "the array carries the bookkeeping.",
    marks={str(k): "dim" for k in range(n)},
    state=[["read", "abs(x)"], ["extra memory", "O(1)"]])

# ---- Act 2: the sign-flip pass ----
arr = list(nums)


def sign_marks(cur=None, home=None, hit=False):
    m = {}
    for k in range(n):
        m[str(k)] = "good" if arr[k] < 0 else "dim"
    if cur is not None:
        m[str(cur)] = "active"
    if home is not None:
        m[str(home)] = "bad" if hit else "active"
    return m


add(act=2, cells=arr, code="fast", line=0,
    intro="a home found already-negative is the tell: that value is a repeat.",
    invariant="a negative home means its value was visited once before.",
    note="Pass: for each value, look at its home. Positive → flip it (first visit). "
         "Negative → we've been here, so it's a duplicate.",
    pointers={"x": 0}, marks=sign_marks(),
    state=[["step", 0], ["n", n]])

dups = []
for idx in range(n):
    x = arr[idx]
    v = abs(x)
    home = v - 1
    hit = arr[home] < 0
    if hit:
        dups.append(v)
        add(act=2, code="fast", line=4,
            note=f"Read nums[{idx}] = {x}. Value {v} → home {home}, already negative "
                 f"({arr[home]}). {v} is a DUPLICATE.",
            pointers={"x": idx}, arc=[idx, home] if idx != home else None,
            marks=sign_marks(cur=idx, home=home, hit=True),
            state=[["value", v], ["home", home], ["nums[home]", arr[home]],
                   ["dups so far", str(dups)]])
    else:
        arr[home] = -arr[home]
        add(act=2, code="fast", line=6,
            note=f"Read nums[{idx}] = {x}. Value {v} → home {home}, was positive — flip "
                 f"it to {arr[home]}. First visit to {v}.",
            pointers={"x": idx}, arc=[idx, home] if idx != home else None,
            marks=sign_marks(cur=idx, home=home),
            state=[["value", v], ["home", home], ["nums[home]", arr[home]],
                   ["dups so far", str(dups) if dups else "—"]])

add(act=2, code="fast", line=0,
    note=f"Pass done. Duplicates = {dups}. Same answer as the set, zero extra memory.",
    marks={str(k): "good" for k in range(n) if arr[k] < 0},
    state=[["answer", str(sorted(dups))], ["extra memory", "O(1)"], ["vs set", str(dups_set)]],
    banner=f"Duplicates = {sorted(dups)}   (set said {sorted(dups_set)}) — O(1) space")

# ---- Act 3: edge case — all unique ----
edge = [1, 2, 3, 4]
add(act=3, cells=edge, code="fast", line=0,
    intro="with no repeats, every home is found positive and flipped once — no dups.",
    invariant="each value visits a distinct home exactly once.",
    note="Edge case: [1, 2, 3, 4], all unique. Every home is flipped exactly once, so "
         "nothing is ever found already negative.",
    pointers={"x": 0}, marks={str(k): "dim" for k in range(len(edge))},
    state=[["n", len(edge)]])
en = len(edge)
ea = list(edge)
for idx in range(en):
    home = abs(ea[idx]) - 1
    ea[home] = -ea[home]
    add(act=3, code="fast", line=6,
        note=f"Value {abs(edge[idx])} → home {home}, positive — flip. No duplicate.",
        pointers={"x": idx}, arc=[idx, home] if idx != home else None,
        marks={str(k): "good" if ea[k] < 0 else "dim" for k in range(en)} | {str(idx): "active"},
        state=[["value", abs(edge[idx])], ["home", home], ["dups so far", "—"]])
add(act=3, code="fast", line=0,
    note="Every home was positive when reached, so no value repeated. Answer is empty.",
    marks={str(k): "good" for k in range(en)},
    state=[["answer", "[]"], ["extra memory", "O(1)"]],
    banner="All unique → duplicates = []")

trace = {
    "player": "linear",
    "title": "Find All Duplicates — signs catch the second visit",
    "acts": ["Seen-set baseline (O(n) space)", "The idea: sign = visited",
             "Sign-flip pass in place", "Edge case: all unique"],
    "code": {"set": SET, "fast": FAST},
    "legend": [["active", "value / home being touched"], ["good", "flipped (visited once)"],
               ["bad", "already negative = duplicate"], ["dim", "not yet visited"]],
    "cells": nums, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
