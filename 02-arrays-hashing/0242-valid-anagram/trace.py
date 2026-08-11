"""Full-arc trace for Valid Anagram, mirroring solution.py: the sort-both-and-
compare baseline and the O(n) count-map (+1 for s, -1 for t, all must cancel to
zero). Linear renderer: a row of characters, a moving pointer, a `counts`
sidebar. Writes trace.json.
"""
import json
import os

s = "anagram"
t = "nagaram"
frames = []

SORT = [
    "return sorted(s) == sorted(t)",
]
FAST = [
    "if len(s) != len(t): return False",
    "counts = {}",
    "for ch in s: counts[ch] += 1",
    "for ch in t:",
    "    counts[ch] -= 1",
    "    if counts[ch] < 0: return False",
    "return all(v == 0 for v in counts.values())",
]


def add(**f):
    frames.append(f)


# ---- Act 0: the sort baseline ----
add(act=0, cells=list(s), code="sort", line=0,
    intro="sorting forces both words into one order — anagrams become the same string.",
    invariant="two words are anagrams exactly when their sorted letters match.",
    note=f"Baseline: sort '{s}' and '{t}', then compare. Simple, but sorting pays an "
         "n log n factor to fully order letters.",
    marks={str(i): "dim" for i in range(len(s))},
    state=[["s", s], ["t", t]])
add(act=0, cells=list("".join(sorted(s))), code="sort", line=0,
    note=f"sorted(s) = '{''.join(sorted(s))}'   sorted(t) = '{''.join(sorted(t))}'. Equal -> anagram.",
    marks={str(i): "good" for i in range(len(s))},
    banner="True (sort) — but we only ever needed the letter counts, not their order",
    state=[["sorted(s)", "".join(sorted(s))], ["sorted(t)", "".join(sorted(t))], ["equal?", "True"]])

# ---- Act 1: the insight ----
add(act=1,
    intro="what sorting computes that we don't need — a full ordering, when a tally is enough.",
    note="Anagrams share one thing: every letter's count matches. So tally s (+1) and t (-1) "
         "in one map. If they cancel to all zeros, it's an anagram.",
    state=[["idea", "count, don't sort"], ["cost", "O(n) vs O(n log n)"]])

# ---- Act 2: fast count map over s (+1) ----
counts = {}


def sidebar():
    return {"title": "counts (letter -> tally)", "rows": [[k, str(v)] for k, v in counts.items()]}


add(act=2, cells=list(s), code="fast", line=1,
    intro="s adds, t subtracts — an anagram makes every tally return to zero.",
    invariant="counts holds (s-letters seen so far) minus (t-letters seen so far).",
    note=f"Lengths match ({len(s)} == {len(t)}), so keep going. First pass: +1 for each letter of s.",
    pointers={"ch": 0}, marks={"0": "active"}, sidebar=sidebar(),
    state=[["pass", "s: +1"]])
for i, ch in enumerate(s):
    counts[ch] = counts.get(ch, 0) + 1
    add(act=2, code="fast", line=2,
        note=f"s[{i}] = '{ch}'. counts['{ch}'] -> {counts[ch]}.",
        pointers={"ch": i}, marks={str(i): "active"}, sidebar=sidebar(),
        state=[["ch", ch], ["counts[ch]", counts[ch]]])

# ---- second pass over t (-1) ----
add(act=2, cells=list(t), code="fast", line=3,
    note="Second pass over t: -1 for each letter. Watch every tally drain toward zero.",
    pointers={"ch": 0}, marks={"0": "active"}, sidebar=sidebar(),
    state=[["pass", "t: -1"]])
neg = False
for i, ch in enumerate(t):
    counts[ch] = counts.get(ch, 0) - 1
    below = counts[ch] < 0
    add(act=2, code="fast", line=5 if below else 4,
        note=f"t[{i}] = '{ch}'. counts['{ch}'] -> {counts[ch]}."
             + (" Below zero — t has a letter s lacked." if below else ""),
        pointers={"ch": i},
        marks={str(i): "bad" if below else "active"}, sidebar=sidebar(),
        state=[["ch", ch], ["counts[ch]", counts[ch]]])
    if below:
        neg = True
        break
if not neg:
    add(act=2, code="fast", line=6,
        note="Every tally cancelled back to zero. The two words use the same letters the same number of times.",
        sidebar=sidebar(),
        banner="True — all counts are zero, so 't' is an anagram of 's'",
        state=[["all zero?", "True"], ["answer", "True"]])

# ---- Act 3: edge case, not an anagram ----
es, et = "rat", "car"
counts = {}
add(act=3, cells=list(es), code="fast", line=1,
    intro="the moment a tally goes below zero we can stop — t brought a letter s never had.",
    invariant="a negative tally means t over-used a letter, so it cannot be an anagram.",
    note="Edge case: 'rat' vs 'car'. Same length, but different letters.",
    pointers={"ch": 0}, marks={"0": "active"}, sidebar=sidebar(),
    state=[["s", es], ["t", et]])
for i, ch in enumerate(es):
    counts[ch] = counts.get(ch, 0) + 1
    add(act=3, code="fast", line=2,
        note=f"s[{i}] = '{ch}'. counts['{ch}'] -> {counts[ch]}.",
        pointers={"ch": i}, marks={str(i): "active"}, sidebar=sidebar(),
        state=[["ch", ch], ["counts[ch]", counts[ch]]])
add(act=3, cells=list(et), code="fast", line=3,
    note="Now subtract for 'car'.",
    pointers={"ch": 0}, marks={"0": "active"}, sidebar=sidebar(),
    state=[["pass", "t: -1"]])
for i, ch in enumerate(et):
    counts[ch] = counts.get(ch, 0) - 1
    below = counts[ch] < 0
    add(act=3, code="fast", line=5 if below else 4,
        note=f"t[{i}] = '{ch}'. counts['{ch}'] -> {counts[ch]}."
             + (" Below zero — 'car' has a 'c' that 'rat' never had. Stop." if below else ""),
        pointers={"ch": i}, marks={str(i): "bad" if below else "active"}, sidebar=sidebar(),
        state=[["ch", ch], ["counts[ch]", counts[ch]]])
    if below:
        add(act=3, code="fast", line=5,
            banner="False — 'car' uses a letter 'rat' does not",
            note="A count dropped below zero, so return False immediately.",
            marks={str(i): "bad"}, sidebar=sidebar(),
            state=[["answer", "False"]])
        break

trace = {
    "player": "linear",
    "title": "Valid Anagram — count the letters, don't sort them",
    "acts": ["Baseline: sort both", "The insight", "Fast: count map", "Edge case: 'rat' vs 'car'"],
    "code": {"sort": SORT, "fast": FAST},
    "legend": [["active", "letter being tallied"], ["good", "match / all zero"], ["bad", "count went negative"], ["dim", "input word"]],
    "cells": list(s), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
