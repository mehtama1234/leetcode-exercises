"""Rich full-arc trace for Find All Numbers Disappeared in an Array, mirroring the
two functions in solution.py. Shows the O(n)-extra-space set baseline, then the
sign-flip trick: mark value v by negating the number at home index v-1; whatever
stays positive was never marked. Writes trace.json.
"""
import json
import os

nums = [4, 3, 2, 7, 8, 2, 3, 1]  # answer: [5, 6]
frames = []

SET = [
    "present = set(nums)",
    "return [v for v in range(1, n+1)",
    "        if v not in present]",
]
FAST = [
    "for x in nums:",
    "    home = abs(x) - 1",
    "    if nums[home] > 0:",
    "        nums[home] = -nums[home]",
    "return [i+1 for i in range(n)",
    "        if nums[i] > 0]",
]


def add(**f):
    frames.append(f)


# ---- Act 0: the set baseline (O(n) extra memory) ----
n = len(nums)
present = set(nums)
add(act=0, cells=nums, code="set", line=0,
    intro="the set is exactly the extra memory the problem asks us to drop.",
    invariant="present holds every value read so far from nums.",
    note="Baseline: build a set of what's present, then report every v in 1..n that "
         "isn't in it. Correct, but the set is O(n) extra memory.",
    marks={str(k): "dim" for k in range(n)},
    sidebar={"title": "present (set)", "rows": [[str(v), "✓"] for v in sorted(present)]},
    state=[["set size", len(present)], ["extra memory", "O(n)"]])
missing_set = []
for v in range(1, n + 1):
    inset = v in present
    if not inset:
        missing_set.append(v)
    add(act=0, code="set", line=1,
        note=f"Is {v} in the set? " + ("Yes." if inset else "No — it disappeared."),
        marks={str(k): "dim" for k in range(n)},
        sidebar={"title": "present (set)", "rows": [[str(x), "✓"] for x in sorted(present)]},
        state=[["checking", v], ["in set?", "yes" if inset else "no"],
               ["missing so far", str(missing_set) if missing_set else "—"]])
add(act=0, code="set", line=1,
    note=f"Missing: {missing_set}. Right answer, but it cost a whole extra set.",
    marks={str(k): "dim" for k in range(n)},
    state=[["answer", str(missing_set)], ["extra memory", "O(n)"]])

# ---- Act 1: the idea — sign as a visited flag ----
add(act=1,
    intro="each value's home index v-1 gets a minus sign to record 'v showed up'.",
    note="Values are 1..n, so value v has a home index v-1. We don't need a set — we "
         "flip the SIGN of the number parked at that home to mark 'seen v'.",
    marks={str(k): "dim" for k in range(n)},
    state=[["value v", "home index v-1"], ["mark", "negate nums[v-1]"],
           ["stays positive", "= never seen"]])
add(act=1,
    note="Read magnitudes with abs() because a slot may already be flipped. After one "
         "pass, any index still POSITIVE was never marked → that value is missing.",
    marks={str(k): "dim" for k in range(n)},
    state=[["read", "abs(x)"], ["extra memory", "O(1)"]])

# ---- Act 2: the sign-flip pass ----
arr = list(nums)


def sign_marks(cur=None, home=None):
    m = {}
    for k in range(n):
        m[str(k)] = "good" if arr[k] < 0 else "dim"  # good = marked (seen)
    if cur is not None:
        m[str(cur)] = "active"
    if home is not None:
        m[str(home)] = "active"
    return m


add(act=2, cells=arr, code="fast", line=0,
    intro="watch homes go negative; the two that stay positive are the answer.",
    invariant="a negative slot means its value's index+1 has already appeared.",
    note="Pass 1: for each value x, go to home index abs(x)-1 and flip it negative "
         "(if still positive). That records 'this value appeared'.",
    pointers={"x": 0}, marks=sign_marks(),
    state=[["step", 0], ["n", n]])

for idx in range(n):
    x = arr[idx]
    v = abs(x)
    home = v - 1
    already = arr[home] < 0
    add(act=2, code="fast", line=1,
        note=f"Read nums[{idx}] = {x}. Value {v} → home index {home}. "
             + (f"nums[{home}] already negative, skip." if already
                else f"nums[{home}] = {arr[home]} is positive — flip it."),
        pointers={"x": idx}, arc=[idx, home] if idx != home else None,
        marks=sign_marks(cur=idx, home=home),
        state=[["reading idx", idx], ["value", v], ["home", home],
               ["nums[home]", arr[home]]])
    if arr[home] > 0:
        arr[home] = -arr[home]
        add(act=2, code="fast", line=3,
            note=f"Marked: nums[{home}] is now {arr[home]}. Value {v} is recorded as seen.",
            pointers={"x": idx},
            marks=sign_marks(cur=idx, home=home),
            state=[["marked value", v], ["nums[home]", arr[home]]])

add(act=2, code="fast", line=4,
    note="Pass 1 done. Now scan: every index still positive was never marked, so its "
         "value (index+1) never appeared.",
    marks=sign_marks(),
    state=[["array", " ".join(str(a) for a in arr)]])

missing = []
for i in range(n):
    pos = arr[i] > 0
    if pos:
        missing.append(i + 1)
    add(act=2, code="fast", line=5,
        note=f"nums[{i}] = {arr[i]}. "
             + (f"Positive → {i+1} is missing." if pos else f"Negative → {i+1} appeared."),
        pointers={"x": i},
        marks={**sign_marks(), str(i): "bad" if pos else "good"},
        state=[["i", i], ["nums[i]", arr[i]], ["missing so far", str(missing) if missing else "—"]])
add(act=2, code="fast", line=5,
    note=f"Missing = {missing}. Same answer as the set, with no extra memory.",
    marks={str(i): ("bad" if arr[i] > 0 else "good") for i in range(n)},
    state=[["answer", str(missing)], ["extra memory", "O(1)"]],
    banner=f"Disappeared = {missing}   (set said {missing_set}) — O(1) space")

# ---- Act 3: edge case — nothing missing ----
edge = [2, 1]
add(act=3, cells=edge, code="fast", line=0,
    intro="when every value shows up, both homes flip negative — the answer is empty.",
    invariant="each value in 1..n negates exactly one distinct home.",
    note="Edge case: [2, 1] contains both 1 and 2, so no number is missing.",
    pointers={"x": 0}, marks={"0": "dim", "1": "dim"},
    state=[["n", 2]])
en = len(edge)
ea = list(edge)
for idx in range(en):
    home = abs(ea[idx]) - 1
    if ea[home] > 0:
        ea[home] = -ea[home]
    add(act=3, code="fast", line=3,
        note=f"Value {abs(edge[idx])} → home {home}; flip it. nums[{home}] = {ea[home]}.",
        pointers={"x": idx}, arc=[idx, home] if idx != home else None,
        marks={str(k): "good" if ea[k] < 0 else "dim" for k in range(en)} | {str(idx): "active"},
        state=[["reading idx", idx], ["value", abs(edge[idx])], ["home", home]])
add(act=3, code="fast", line=5,
    note="Every slot is negative — all of 1..2 appeared, so nothing disappeared.",
    marks={str(k): "good" for k in range(en)},
    state=[["answer", "[]"], ["extra memory", "O(1)"]],
    banner="Both 1 and 2 present → disappeared = []")

trace = {
    "player": "linear",
    "title": "Find Disappeared Numbers — signs as a visited flag",
    "acts": ["Set baseline (O(n) space)", "The idea: sign = seen",
             "Sign-flip pass in place", "Edge case: nothing missing"],
    "code": {"set": SET, "fast": FAST},
    "legend": [["active", "value / home being touched"], ["good", "marked seen / negative"],
               ["bad", "stayed positive = missing"], ["dim", "not yet marked"]],
    "cells": nums, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
