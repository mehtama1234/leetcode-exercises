"""Full-arc trace for Is Subsequence: a single greedy two-pointer walk over t,
advancing into s on each match. There is no wasteful baseline here, so the arc
is: the rule -> run it -> an edge case. Linear renderer: the string t as a row of
cells, an `i` pointer into s and a `j` pointer into t, a sidebar showing s and
progress. Writes trace.json.
"""
import json
import os

s = "abc"
t = "ahbgdc"
frames = []

FAST = [
    "i = 0",
    "for ch in t:",
    "    if i < len(s) and ch == s[i]:",
    "        i += 1",
    "return i == len(s)",
]


def add(**f):
    frames.append(f)


def sidebar(i, s):
    need = s[i] if i < len(s) else "-"
    return {"title": "s (target) — waiting for", "rows": [
        ["s", s],
        ["matched", s[:i] or "(none)"],
        ["next needed", need],
    ]}


# ---- Act 0: the rule ----
add(act=0, cells=list(t), code="fast", line=0,
    intro="s never rewinds — one pointer into s only moves forward, and earliest-match greedy is safe.",
    invariant="s[:i] has been found in t, in order, up to the current position.",
    note=f"Is '{s}' a subsequence of '{t}'? Walk t once. Pointer i waits for the next letter of s.",
    pointers={"j": 0}, marks={"0": "active"}, sidebar=sidebar(0, s),
    state=[["s", s], ["t", t], ["i", 0], ["need", s[0]]])

# ---- Act 0 (cont.): run the walk ----
i = 0
matched_idx = []
for j, ch in enumerate(t):
    match = i < len(s) and ch == s[i]
    if match:
        matched_idx.append(j)
        add(act=0, code="fast", line=2,
            note=f"t[{j}] = '{ch}' == s[{i}] = '{s[i]}'. Match — advance i.",
            pointers={"j": j}, marks={str(j): "good"}, sidebar=sidebar(i, s),
            state=[["t[j]", ch], ["s[i]", s[i]], ["i", i], ["match", "yes"]])
        i += 1
        add(act=0, code="fast", line=3,
            note=f"i -> {i}. "
                 + (f"Now waiting for '{s[i]}'." if i < len(s) else "s is fully matched."),
            pointers={"j": j}, marks={str(j): "good"}, sidebar=sidebar(i, s),
            state=[["i", i], ["need", s[i] if i < len(s) else "(done)"]])
        if i == len(s):
            break
    else:
        add(act=0, code="fast", line=1,
            note=f"t[{j}] = '{ch}' != s[{i}] = '{s[i]}'. Skip this character of t; i stays.",
            pointers={"j": j}, marks={str(j): "dim"}, sidebar=sidebar(i, s),
            state=[["t[j]", ch], ["s[i]", s[i]], ["i", i], ["match", "no"]])

# ---- Act 1: full match ----
add(act=1, code="fast", line=4,
    intro="i reaching len(s) is the whole success test — s was consumed in order.",
    invariant="the matched positions of t are strictly increasing, preserving order.",
    note=f"i reached {i} = len(s). Every letter of '{s}' was found in order at "
         f"t{matched_idx}.",
    marks={str(k): "good" for k in matched_idx},
    banner=f"True — 'abc' is a subsequence of 'ahbgdc' (matched at t{matched_idx})",
    state=[["i", i], ["len(s)", len(s)], ["answer", "True"]])

# ---- Act 2: edge case, not a subsequence ----
es, et = "axc", "ahbgdc"
add(act=2, cells=list(et), code="fast", line=0,
    intro="t runs out before s is satisfied — that is the honest 'no'.",
    invariant="i still points at the first letter of s that t could not supply in order.",
    note="Edge case: 'axc' vs 'ahbgdc'. There is an 'a' and a 'c', but no 'x' after the 'a'.",
    pointers={"j": 0}, marks={"0": "active"}, sidebar=sidebar(0, es),
    state=[["s", es], ["t", et], ["i", 0], ["need", "a"]])
i = 0
for j, ch in enumerate(et):
    match = i < len(es) and ch == es[i]
    if match:
        add(act=2, code="fast", line=3,
            note=f"t[{j}] = '{ch}' == s[{i}] = '{es[i]}'. Advance i -> {i + 1}.",
            pointers={"j": j}, marks={str(j): "good"}, sidebar=sidebar(i + 1, es),
            state=[["i", i + 1], ["need", es[i + 1] if i + 1 < len(es) else "(done)"]])
        i += 1
    else:
        add(act=2, code="fast", line=1,
            note=f"t[{j}] = '{ch}' != s[{i}] = '{es[i]}'. Skip; still waiting for '{es[i]}'.",
            pointers={"j": j}, marks={str(j): "dim"}, sidebar=sidebar(i, es),
            state=[["t[j]", ch], ["need", es[i]], ["i", i]])
add(act=2, code="fast", line=4,
    note=f"t is exhausted but i is only {i} of {len(es)} — the 'x' was never found. Return False.",
    marks={str(len(et) - 1): "bad"}, sidebar=sidebar(i, es),
    banner="False — 'axc' is not a subsequence of 'ahbgdc' (no 'x')",
    state=[["i", i], ["len(s)", len(es)], ["answer", "False"]])

trace = {
    "player": "linear",
    "title": "Is Subsequence — one greedy walk, no rewinding",
    "acts": ["The rule: walk t once", "Full match", "Edge case: no 'x'"],
    "code": {"fast": FAST},
    "legend": [["active", "current position in t"], ["good", "a matched letter"], ["bad", "t ran out"], ["dim", "skipped in t"]],
    "cells": list(t), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
