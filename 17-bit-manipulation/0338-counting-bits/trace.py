"""Rich full-arc trace for Counting Bits (linear renderer, cells = bits of i).
Arc: brute — count each number's bits from scratch (the waste) -> name the repeated
work -> DP: ans[i] = ans[i & (i-1)] + 1 reuses an already-solved smaller number ->
edge case (i = 0). Cells are the bits of the current number i; a pointer marks the
lowest set bit being dropped; a sidebar holds the growing ans[] table. Mirrors both
functions in solution.py. Writes trace.json.
"""
import json
import os

N = 7                   # build ans[0..7]
WIDTH = 3               # 3 bits hold 0..7
frames = []

BRUTE = [
    "for i in range(n + 1):",
    "    count = 0; x = i",
    "    while x:",
    "        x &= x - 1   # drop lowest set bit",
    "        count += 1",
    "    ans.append(count)",
]
DP = [
    "ans = [0] * (n + 1)",
    "for i in range(1, n + 1):",
    "    ans[i] = ans[i & (i - 1)] + 1",
    "return ans",
]


def add(**f):
    frames.append(f)


def bits(x, width=WIDTH):
    return [(x >> (width - 1 - i)) & 1 for i in range(width)]


POS = [WIDTH - 1 - i for i in range(WIDTH)]


def table(ans, upto):
    rows = [[str(k), str(ans[k]) if k <= upto and ans[k] is not None else "?"]
            for k in range(N + 1)]
    return {"title": "ans[i] = # of 1s", "rows": rows}


def popcount(x):
    return bin(x).count("1")


# ---- Act 0: brute — count each number from scratch ----
brute_ans = [None] * (N + 1)
total_ops = 0
add(act=0, cells=bits(0), labels=POS, code="brute", line=0,
    intro="each number is taken apart bit by bit, ignoring the ones we already solved.",
    invariant="count = set bits removed from x so far.",
    note=f"Brute force: for every i in 0..{N}, peel its set bits one at a time and "
    "count them. Correct, but every number starts from zero.",
    marks={str(i): "dim" for i in range(WIDTH)},
    sidebar=table(brute_ans, -1),
    state=[["i", 0], ["count", 0], ["ops", 0]])

for i in range(N + 1):
    x = i
    c = 0
    # show a couple representative numbers in full; summarize the rest
    show = i in (3, 5, 6, 7)
    if show:
        add(act=0, cells=bits(i), labels=POS, code="brute", line=1,
            note=f"i = {i} ({''.join(map(str, bits(i)))}). Start count at 0 and strip "
            "its set bits.",
            marks={str(j): ("good" if bits(i)[j] else "dim") for j in range(WIDTH)},
            sidebar=table(brute_ans, i - 1),
            state=[["i", i], ["count", 0]])
    while x:
        lowset = max(j for j in range(WIDTH) if bits(x)[j] == 1)
        x &= x - 1
        c += 1
        total_ops += 1
        if show:
            add(act=0, cells=bits(x), labels=POS, code="brute", line=3,
                note=f"Drop a set bit; count -> {c}. x is now "
                f"{''.join(map(str, bits(x)))}.",
                pointers={"dropped": lowset}, marks={str(lowset): "active"},
                sidebar=table(brute_ans, i - 1),
                state=[["i", i], ["count", c], ["ops", total_ops]])
    brute_ans[i] = c
add(act=0, cells=bits(N), labels=POS, code="brute", line=5,
    note=f"All {N + 1} numbers counted independently in {total_ops} bit-drops. Notice 7 "
    "recomputed the very same bits 3 and 6 already went through.",
    marks={str(i): "bad" for i in range(WIDTH)},
    sidebar=table(brute_ans, N),
    state=[["ans", str(brute_ans)], ["total bit-drops", total_ops]])

# ---- Act 1: name the waste ----
add(act=1, cells=bits(7), labels=POS, code=None,
    intro="7 = 111 is just 6 = 110 with one extra bit — 6's answer is already known.",
    invariant="dropping the lowest bit of i lands on a SMALLER number we solved.",
    note="6 = 110 has 2 ones. 7 = 111 is 6 with the low bit added, so it has 3 — we "
    "recounted 6's two bits instead of reusing ans[6].",
    marks={"0": "good", "1": "good", "2": "active"},
    state=[["ans[6]", brute_ans[6]], ["ans[7]", brute_ans[7]], ["reused?", "no"]])
add(act=1, cells=bits(7), labels=POS, code=None,
    note="For every i, i & (i-1) clears its lowest 1-bit and gives a smaller number "
    "whose answer we already have. That is the work we can skip.",
    marks={str(j): "bad" for j in range(WIDTH)},
    state=[["relation", "ans[i] = ans[i&(i-1)] + 1"]])

# ---- Act 2: DP — reuse the smaller answer ----
ans = [0] * (N + 1)
add(act=2, cells=bits(0), labels=POS, code="dp", line=0,
    intro="each ans[i] is one lookup plus one — no inner loop over bits at all.",
    invariant="ans[j] is already correct for every j < i.",
    note="DP: ans[0] = 0. For each i, look up ans[i & (i-1)] (the number with i's "
    "lowest bit removed) and add 1.",
    marks={str(j): "dim" for j in range(WIDTH)},
    sidebar=table(ans, 0),
    state=[["ans[0]", 0]])

for i in range(1, N + 1):
    prev = i & (i - 1)
    lowset = max(j for j in range(WIDTH) if bits(i)[j] == 1)
    add(act=2, cells=bits(i), labels=POS, code="dp", line=2,
        note=f"i = {i} ({''.join(map(str, bits(i)))}). Drop the lowest 1-bit: "
        f"i & (i-1) = {prev} ({''.join(map(str, bits(prev)))}), which we already solved.",
        pointers={"drop": lowset}, marks={str(lowset): "active"},
        sidebar=table(ans, i - 1),
        state=[["i", i], ["i & (i-1)", prev], ["ans[%d]" % prev, ans[prev]]])
    ans[i] = ans[prev] + 1
    add(act=2, cells=bits(i), labels=POS, code="dp", line=2,
        note=f"ans[{i}] = ans[{prev}] + 1 = {ans[prev]} + 1 = {ans[i]}. One lookup, no "
        "bit loop.",
        marks={str(j): ("good" if bits(i)[j] else "dim") for j in range(WIDTH)},
        sidebar=table(ans, i),
        state=[["ans[%d]" % i, ans[i]]])

add(act=2, cells=bits(N), labels=POS, code="dp", line=3,
    note=f"Whole table built in {N} single steps: {ans}. No number was taken apart "
    "twice.",
    marks={str(j): "good" for j in range(WIDTH)},
    sidebar=table(ans, N),
    state=[["ans", str(ans)], ["steps", N], ["vs brute drops", total_ops]],
    banner=f"ans = {ans}   ({N} lookups vs {total_ops} brute bit-drops)")

# ---- Act 3: edge case — i = 0 ----
add(act=3, cells=bits(0), labels=POS, code="dp", line=0,
    intro="the base case anchors the whole recurrence.",
    invariant="ans[0] = 0 is the one value not computed from a smaller one.",
    note="Edge case: i = 0 has no set bits, so ans[0] = 0. Every other answer chains "
    "back to this base through i & (i-1).",
    marks={str(j): "good" for j in range(WIDTH)},
    sidebar={"title": "ans[i] = # of 1s", "rows": [["0", "0"]]},
    state=[["ans[0]", 0]],
    banner="ans[0] = 0  (the base case)")

trace = {
    "player": "linear",
    "title": "Counting Bits - reuse the answer for i with its lowest bit dropped",
    "acts": ["Brute: count each from scratch", "The waste", "DP: ans[i] = ans[i&(i-1)]+1", "Edge: i = 0"],
    "code": {"brute": BRUTE, "dp": DP},
    "legend": [["active", "lowest set bit being dropped"], ["good", "a 1 in i / settled answer"],
               ["bad", "recounted work (waste)"], ["dim", "a 0"]],
    "cells": bits(0), "labels": POS, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
