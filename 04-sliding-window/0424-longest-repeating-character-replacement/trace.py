"""Full-arc trace for Longest Repeating Character Replacement: brute re-count every
substring -> the waste -> sliding window (fixable iff window_len - max_freq <= k;
shrink by one when not) -> edge case (k = 0). Mirrors solution.py. Writes trace.json.
"""
import json
import os

s = "AABABBA"
k = 1  # answer 4
cells = list(s)
frames = []

BRUTE = [
    "for i in range(n):",
    "  counts = {}; max_freq = 0",
    "  for j in range(i, n):",
    "    counts[s[j]] += 1; max_freq = max(...)",
    "    if (j-i+1) - max_freq <= k:",
    "      best = max(best, j-i+1)",
]
FAST = [
    "for right, ch in enumerate(s):",
    "    counts[ch] += 1",
    "    max_freq = max(max_freq, counts[ch])",
    "    if (right-left+1) - max_freq > k:",
    "        counts[s[left]] -= 1; left += 1",
    "    best = max(best, right-left+1)",
]


def add(**f):
    frames.append(f)


def cbar(counts):
    items = [f"{c}:{n}" for c, n in sorted(counts.items()) if n]
    return {"title": "counts in window", "rows": [[x.split(":")[0], x.split(":")[1]] for x in items]}


# ---- Act 0: brute — re-count every substring for fixability ----
work = 0
best = 0
best_span = (0, 0)
add(act=0, cells=cells, labels=list(range(len(s))), code="brute", line=0,
    intro="every start re-counts letters from scratch across an overlapping tail.",
    invariant="best is the longest fixable substring among those starting before i.",
    note=f"Brute force: a window is fixable if (length - most common letter) <= {k} changes. "
         "Re-count from each start.",
    pointers={"i": 0, "j": 0}, window=[0, 0], marks={"0": "active"},
    state=[["i", 0], ["best", 0], ["k", k], ["recounts", 0]])
for i in range(len(s)):
    counts = {}
    max_freq = 0
    for j in range(i, len(s)):
        work += 1
        counts[s[j]] = counts.get(s[j], 0) + 1
        max_freq = max(max_freq, counts[s[j]])
        wlen = j - i + 1
        fixable = wlen - max_freq <= k
        if fixable and wlen > best:
            best = wlen
            best_span = (i, j)
        # surface first start fully, plus any new best
        if i == 0 or (fixable and wlen == best):
            add(act=0, code="brute", line=4,
                note=f"s[{i}..{j}] = \"{s[i:j+1]}\": length {wlen}, most common appears "
                     f"{max_freq}x → {wlen-max_freq} changes. "
                     + (f"<= {k}: fixable, best {best}." if fixable else f"> {k}: not fixable."),
                pointers={"i": i, "j": j}, window=[i, j],
                marks={str(m): ("good" if fixable else "active") for m in range(i, j + 1)},
                sidebar=cbar(counts),
                state=[["i", i], ["j", j], ["max_freq", max_freq],
                       ["changes", wlen - max_freq], ["best", best], ["recounts", work]])
a, b = best_span
add(act=0, code="brute", line=5,
    note=f"Longest fixable: \"{s[a:b+1]}\" length {best} — but it re-counted {work} times.",
    pointers={"i": a, "j": b}, window=[a, b],
    marks={str(m): "good" for m in range(a, b + 1)},
    state=[["best", best], ["recounts", work]])

# ---- Act 1: the waste ----
add(act=1,
    intro="the recount counter — each new start rebuilds tallies an earlier start had.",
    note=f"{work} recounts. Every start rebuilds the letter tally from zero over "
    "overlapping text. That repeated counting is the waste.",
    marks={str(m): "dim" for m in range(len(s))},
    state=[["recounts (brute)", work], ["pattern", "~ n*n"]])
add(act=1,
    note="Keep ONE window. A window is fixable iff (length - max_freq) <= k. Grow right "
    "always; when it stops being fixable, nudge left forward by one. left never rewinds.",
    marks={str(m): "dim" for m in range(len(s))},
    state=[["pattern", "~ n"], ["left moves", "forward only"]])

# ---- Act 2: fast — sliding window ----
counts = {}
left = 0
max_freq = 0
best = 0
best_span = (0, 0)
add(act=2, cells=cells, labels=list(range(len(s))), code="fast", line=0,
    intro="counts carry as the window moves; left only slides when the window is unfixable.",
    invariant="the window [left, right] is always fixable within k changes.",
    note=f"One window, budget k={k}. Grow right; if changes needed exceed {k}, slide left one.",
    pointers={"L": 0, "R": 0}, window=[0, 0], marks={"0": "active"},
    sidebar=cbar({}),
    state=[["left", 0], ["max_freq", 0], ["best", 0]])
for right, ch in enumerate(s):
    counts[ch] = counts.get(ch, 0) + 1
    max_freq = max(max_freq, counts[ch])
    wlen = right - left + 1
    if wlen - max_freq > k:
        dropped = s[left]
        counts[dropped] -= 1
        left += 1
        wlen -= 1
        add(act=2, code="fast", line=4,
            note=f"add '{ch}': window \"{s[left-1:right+1]}\" needs > {k} changes — "
                 f"slide left, drop '{dropped}'. Window now \"{s[left:right+1]}\".",
            pointers={"L": left, "R": right}, window=[left, right],
            marks={**{str(left - 1): "bad"},
                   **{str(m): "active" for m in range(left, right + 1)}},
            sidebar=cbar(counts),
            state=[["left", left], ["max_freq", max_freq], ["window", wlen], ["best", best]])
    else:
        add(act=2, code="fast", line=5,
            note=f"add '{ch}': window \"{s[left:right+1]}\" needs {wlen-max_freq} change(s) "
                 f"(<= {k}) — valid, length {wlen}.",
            pointers={"L": left, "R": right}, window=[left, right],
            marks={str(m): "active" for m in range(left, right + 1)},
            sidebar=cbar(counts),
            state=[["left", left], ["max_freq", max_freq], ["window", wlen], ["best", max(best, wlen)]])
    if wlen > best:
        best = wlen
        best_span = (left, right)
a, b = best_span
add(act=2, code="fast", line=5,
    note=f"Longest run makeable with {k} change(s): length {best} (e.g. \"{s[a:b+1]}\").",
    pointers={"L": a, "R": b}, window=[a, b],
    marks={str(m): "good" for m in range(a, b + 1)},
    sidebar=cbar(counts),
    state=[["best", best], ["passes", 1], ["vs brute recounts", work]],
    banner=f"Longest run = {best}   window \"{s[a:b+1]}\" with {k} change(s) — one pass vs {work} recounts")

# ---- Act 3: edge case, k = 0 ----
e = "ABCDE"
ek = 0  # answer 2? no: k=0 means no changes -> longest existing same-letter run = 1
cells_e = list(e)
counts = {}
left = 0
max_freq = 0
best = 0
best_span = (0, 0)
add(act=3, cells=cells_e, labels=list(range(len(e))), code="fast", line=0,
    intro="with k=0 no letter may change, so the window can never hold two different letters.",
    invariant="the window [left, right] is fixable with 0 changes — all one letter.",
    note="Edge case: k = 0, all-distinct letters. left chases right; the run never exceeds 1.",
    pointers={"L": 0, "R": 0}, window=[0, 0], marks={"0": "active"},
    sidebar=cbar({}),
    state=[["k", 0], ["best", 0]])
for right, ch in enumerate(e):
    counts[ch] = counts.get(ch, 0) + 1
    max_freq = max(max_freq, counts[ch])
    wlen = right - left + 1
    if wlen - max_freq > ek:
        dropped = e[left]
        counts[dropped] -= 1
        left += 1
        wlen -= 1
        add(act=3, code="fast", line=4,
            note=f"add '{ch}': window would need a change but k=0 — slide left, drop '{dropped}'.",
            pointers={"L": left, "R": right}, window=[left, right],
            marks={str(left - 1): "bad", str(right): "active"},
            sidebar=cbar(counts),
            state=[["left", left], ["window", wlen], ["best", best]])
    if wlen > best:
        best = wlen
        best_span = (left, right)
add(act=3, code="fast", line=5,
    note="No two letters are the same, so with 0 changes the best run stays length 1.",
    pointers={"L": best_span[0], "R": best_span[1]}, window=list(best_span),
    marks={str(best_span[0]): "good"},
    state=[["best", best]],
    banner="Longest run = 1   (k=0, all letters distinct)")

trace = {
    "player": "linear",
    "title": "Longest Repeating Character Replacement — from re-counting to one window",
    "acts": ["Brute force: re-count each start", "The waste",
             "Fast: fixable window", "Edge case: k = 0"],
    "code": {"brute": BRUTE, "fast": FAST},
    "legend": [["active", "current window"], ["good", "best fixable window"],
               ["bad", "letter leaving on the left"], ["dim", "inactive"]],
    "cells": cells, "labels": list(range(len(s))), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
