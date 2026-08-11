"""Full-arc trace for Minimum Window Substring: brute check every substring for
coverage -> the waste (re-counting overlapping substrings) -> sliding window (grow
to cover via a `formed` counter, then shrink while still covered) -> edge case
(need more of a char than exists). Mirrors solution.py. Writes trace.json.
"""
import json
import os

s = "ADOBECODEBANC"
t = "ABC"  # answer "BANC" at s[9:13]
cells = list(s)
frames = []

BRUTE = [
    "for i in range(n):",
    "    for j in range(i+1, n+1):",
    "        if covers(s[i:j], need):",
    "            best = shortest so far",
    "            break",
]
FAST = [
    "for right, ch in enumerate(s):",
    "    window[ch] += 1",
    "    if window[ch] == need[ch]: formed += 1",
    "    while formed == required:",
    "        record if shorter",
    "        drop s[left]; left += 1",
    "        if a need broke: formed -= 1",
]


def add(**f):
    frames.append(f)


need = {"A": 1, "B": 1, "C": 1}
required = len(need)


def wbar(window):
    rows = [[c, str(window.get(c, 0))] for c in "ABC"]
    return {"title": "window has (need 1 each)", "rows": rows}


# ---- Act 0: brute — check every substring for coverage ----
work = 0
best = ""
best_span = None


def covers(sub):
    have = {}
    for ch in sub:
        have[ch] = have.get(ch, 0) + 1
    return all(have.get(c, 0) >= n for c, n in need.items())


add(act=0, cells=cells, labels=list(range(len(s))), code="brute", line=0,
    intro="every start grows a substring and re-counts its letters from scratch.",
    invariant="best is the shortest covering substring starting before i.",
    note="Brute force: for each start, extend until it covers A, B and C. Re-count each time.",
    pointers={"i": 0, "j": 0}, window=[0, 0], marks={"0": "active"},
    state=[["i", 0], ["best", "\"\""], ["checks", 0]])
for i in range(len(s)):
    for j in range(i + 1, len(s) + 1):
        work += 1
        if covers(s[i:j]):
            if best == "" or (j - i) < len(best):
                best = s[i:j]
                best_span = (i, j - 1)
                add(act=0, code="brute", line=3,
                    note=f"start {i}: \"{s[i:j]}\" first covers A,B,C at length {j-i}. "
                         f"Best so far \"{best}\".",
                    pointers={"i": i, "j": j - 1}, window=[i, j - 1],
                    marks={str(m): "good" for m in range(i, j)},
                    state=[["i", i], ["window", f"\"{s[i:j]}\""], ["best", f"\"{best}\""],
                           ["checks", work]])
            break
a, b = best_span
add(act=0, code="brute", line=4,
    note=f"Shortest covering window \"{best}\" (s[{a}:{b+1}]) — but it counted {work} "
         "substrings, re-tallying overlaps.",
    pointers={"i": a, "j": b}, window=[a, b],
    marks={str(m): "good" for m in range(a, b + 1)},
    state=[["best", f"\"{best}\""], ["checks", work]])

# ---- Act 1: the waste ----
add(act=1,
    intro="the check counter — each start re-counts letters overlapping windows already saw.",
    note=f"{work} substring checks, each re-counting letters. Neighbouring substrings share "
    "almost all their text — that re-tallying is the waste.",
    marks={str(m): "dim" for m in range(len(s))},
    state=[["checks (brute)", work], ["pattern", "~ n*n"]])
add(act=1,
    note="Keep one window and a single counter `formed` = how many of A,B,C are satisfied. "
    "Grow right to reach coverage, then shrink left while still covered. Both move forward only.",
    marks={str(m): "dim" for m in range(len(s))},
    state=[["pattern", "~ n"], ["coverage test", "O(1) via formed"]])

# ---- Act 2: fast — grow to cover, shrink while covered ----
window = {}
formed = 0
left = 0
best_len = float("inf")
best_start = 0
add(act=2, cells=cells, labels=list(range(len(s))), code="fast", line=0,
    intro="`formed` counts satisfied letters, so 'fully covered?' is one comparison.",
    invariant="formed = how many of A,B,C currently meet their required count.",
    note="One window. Grow right, tracking formed. When formed == 3, shrink left as far as valid.",
    pointers={"L": 0, "R": 0}, window=[0, 0], marks={"0": "active"},
    sidebar=wbar({}),
    state=[["left", 0], ["formed", 0], ["required", required], ["best", "inf"]])
for right, ch in enumerate(s):
    window[ch] = window.get(ch, 0) + 1
    if ch in need and window[ch] == need[ch]:
        formed += 1
    covered = formed == required
    add(act=2, code="fast", line=1,
        note=f"right {right}: pull in '{ch}'. formed {formed}/{required}. "
             + ("Covered — now shrink." if covered else "Not covered yet — keep growing."),
        pointers={"L": left, "R": right}, window=[left, right],
        marks={str(m): ("active" if m == right else "dim") for m in range(left, right + 1)},
        sidebar=wbar(window),
        state=[["right", right], ["char", ch], ["formed", formed], ["window len", right - left + 1]])
    while formed == required:
        if right - left + 1 < best_len:
            best_len = right - left + 1
            best_start = left
        left_ch = s[left]
        window[left_ch] -= 1
        broke = left_ch in need and window[left_ch] < need[left_ch]
        add(act=2, code="fast", line=4,
            note=f"covered \"{s[left:right+1]}\" (len {right-left+1}). Best {best_len if best_len!=float('inf') else '-'}. "
                 f"Drop '{left_ch}' on the left" + (" — breaks coverage, stop." if broke else ", still covered."),
            pointers={"L": left, "R": right}, window=[left, right],
            marks={**{str(left): "bad"},
                   **{str(m): "good" for m in range(left + 1, right + 1)}},
            sidebar=wbar(window),
            state=[["left", left], ["window len", right - left + 1],
                   ["best len", best_len if best_len != float("inf") else "inf"],
                   ["formed", formed - (1 if broke else 0)]])
        if broke:
            formed -= 1
        left += 1
a = best_start
b = best_start + best_len - 1
add(act=2, code="fast", line=4,
    note=f"Shortest covering window \"{s[a:b+1]}\" (s[{a}:{b+1}]), length {best_len}. One pass.",
    pointers={"L": a, "R": b}, window=[a, b],
    marks={str(m): "good" for m in range(a, b + 1)},
    sidebar=wbar({c: need[c] for c in need}),
    state=[["answer", f"\"{s[a:b+1]}\""], ["best len", best_len], ["vs brute checks", work]],
    banner=f"Min window = \"{s[a:b+1]}\"   (len {best_len}) — one pass vs {work} brute checks")

# ---- Act 3: edge case, impossible (need more than exists) ----
es = "a"
et = "aa"  # need two a's, only one exists -> ""
add(act=3, cells=list(es), labels=list(range(len(es))), code="fast", line=0,
    intro="formed can never reach required, so no window is ever recorded.",
    invariant="formed = satisfied letters; it caps below required when t can't be covered.",
    note="Edge case: s=\"a\", t=\"aa\". We need two a's but only one exists — impossible.",
    pointers={"L": 0, "R": 0}, window=[0, 0], marks={"0": "active"},
    sidebar={"title": "window has (need a:2)", "rows": [["a", "0"]]},
    state=[["required", 1], ["formed", 0], ["best", "inf"]])
w = {}
formed = 0
for right, ch in enumerate(es):
    w[ch] = w.get(ch, 0) + 1
    add(act=3, code="fast", line=1,
        note=f"pull in '{ch}'. Have 1 'a', need 2 — requirement not met, formed stays 0.",
        pointers={"L": 0, "R": right}, window=[0, right],
        marks={str(right): "bad"},
        sidebar={"title": "window has (need a:2)", "rows": [["a", str(w["a"])]]},
        state=[["have a", w["a"]], ["need a", 2], ["formed", 0]])
add(act=3, code="fast", line=4,
    note="formed never reached required, so nothing was recorded. Answer is the empty string.",
    marks={"0": "dim"},
    state=[["answer", "\"\""]],
    banner="Min window = \"\"   (t can't be covered)")

trace = {
    "player": "linear",
    "title": "Minimum Window Substring — from checking every substring to one window",
    "acts": ["Brute force: check every substring", "The waste",
             "Fast: grow to cover, shrink while covered", "Edge case: impossible"],
    "code": {"brute": BRUTE, "fast": FAST},
    "legend": [["active", "char just pulled in"], ["good", "covering window"],
               ["bad", "char leaving / short"], ["dim", "inactive"]],
    "cells": cells, "labels": list(range(len(s))), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
