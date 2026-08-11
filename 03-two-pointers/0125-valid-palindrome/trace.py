"""Full-arc trace for Valid Palindrome: filter-and-reverse (allocates two strings)
-> the waste -> two pointers walking inward, skipping junk in place -> edge case.
Mirrors solution.py. Writes trace.json.
"""
import json
import os

s = "A man, a plan, a canal: Panama"
cells = list(s)
frames = []

CLEAN = [
    "kept = [c.lower() for c in s if c.isalnum()]",
    "return kept == kept[::-1]",
]
FAST = [
    "left, right = 0, len(s)-1",
    "while left < right:",
    "    while not s[left].isalnum(): left += 1",
    "    while not s[right].isalnum(): right -= 1",
    "    if s[left].lower() != s[right].lower(): return False",
    "    left += 1; right -= 1",
]


def add(**f):
    frames.append(f)


def setrows(title, items):
    return {"title": title, "rows": [[c, ""] for c in items]}


# ---- Act 0: filter and reverse — the honest first thought ----
kept = [c.lower() for c in s if c.isalnum()]
add(act=0, cells=cells, labels=list(range(len(cells))), code="clean", line=0,
    intro="a whole new filtered string gets built, then a second reversed copy of it.",
    invariant="kept holds every letter/digit seen so far, lowercased, in order.",
    note="First thought: strip out non-letters, lowercase, then compare to the reverse.",
    marks={str(k): ("active" if s[k].isalnum() else "dim") for k in range(len(s))},
    sidebar=setrows("kept (allocated)", kept[:12] + (["..."] if len(kept) > 12 else [])),
    state=[["kept length", len(kept)], ["allocations", 0]])
add(act=0, code="clean", line=0,
    note=f"Filtered string \"{''.join(kept)}\" — that's one new string of {len(kept)} chars.",
    marks={str(k): ("active" if s[k].isalnum() else "dim") for k in range(len(s))},
    sidebar=setrows("kept (allocated)", list("".join(kept))),
    state=[["kept", "".join(kept)], ["allocations", 1]])
rev = kept[::-1]
is_pal = kept == rev
add(act=0, code="clean", line=1,
    note=f"Reverse it — a SECOND string \"{''.join(rev)}\" — and compare. Equal? "
         f"{is_pal}. Correct, but two throwaway strings for a yes/no.",
    marks={str(k): "good" for k in range(len(s)) if s[k].isalnum()},
    sidebar=setrows("reversed (allocated)", list("".join(rev))),
    state=[["equal?", is_pal], ["allocations", 2], ["extra space", f"~{2*len(kept)} chars"]])

# ---- Act 1: the waste ----
add(act=1,
    intro="two full strings built just to answer true/false — pure overhead.",
    note=f"The waste is memory: we allocated ~{2*len(kept)} characters of new string to "
    "decide one boolean. The mirror check needs no copies at all.",
    marks={str(k): "dim" for k in range(len(s))},
    state=[["extra space", f"~{2*len(kept)} chars"], ["what we want", "O(1) extra"]])
add(act=1,
    note="A palindrome is a mirror: first kept char equals last, second equals "
    "second-last. Compare the two ends directly and step inward — nothing to build.",
    marks={str(k): "dim" for k in range(len(s))},
    state=[["extra space", "0"], ["passes", "1"]])

# ---- Act 2: fast, two pointers inward, skip junk in place ----
left, right = 0, len(s) - 1
add(act=2, cells=cells, labels=list(range(len(cells))), code="fast", line=0,
    intro="the pointers skip punctuation in place and compare where they land — no copy.",
    invariant="everything outside [left, right] has already matched as a mirror pair.",
    note="Two pointers at the ends. Skip non-alphanumerics, compare, step inward.",
    pointers={"L": left, "R": right}, window=[left, right],
    marks={str(left): "active", str(right): "active"},
    state=[["left", left], ["right", right], ["comparisons", 0]])
comps = 0
ok = True
while left < right:
    if not s[left].isalnum():
        add(act=2, code="fast", line=2,
            note=f"s[{left}] = '{s[left]}' isn't a letter/digit — skip it, move left in.",
            pointers={"L": left, "R": right}, window=[left, right],
            marks={str(left): "dim", str(right): "active"},
            state=[["left", left], ["right", right], ["comparisons", comps]])
        left += 1
        continue
    if not s[right].isalnum():
        add(act=2, code="fast", line=3,
            note=f"s[{right}] = '{s[right]}' isn't a letter/digit — skip it, move right in.",
            pointers={"L": left, "R": right}, window=[left, right],
            marks={str(left): "active", str(right): "dim"},
            state=[["left", left], ["right", right], ["comparisons", comps]])
        right -= 1
        continue
    comps += 1
    match = s[left].lower() == s[right].lower()
    add(act=2, code="fast", line=4,
        note=f"'{s[left]}' vs '{s[right]}' (lowercased): "
             + ("match — step both inward." if match else "mismatch — not a palindrome."),
        pointers={"L": left, "R": right}, window=[left, right], arc=[left, right],
        marks={str(left): "good" if match else "bad", str(right): "good" if match else "bad"},
        state=[["left", left], ["right", right], ["comparisons", comps]])
    if not match:
        ok = False
        break
    left += 1
    right -= 1
if ok:
    add(act=2, code="fast", line=1,
        note="Pointers met in the middle with every pair matched. It's a palindrome.",
        pointers={"L": right, "R": left}, window=[min(left, right), max(left, right)],
        marks={str(k): "good" for k in range(len(s)) if s[k].isalnum()},
        state=[["result", "True"], ["extra space", "0"], ["comparisons", comps]],
        banner=f"Palindrome: True   (0 extra memory, {comps} comparisons)")

# ---- Act 3: edge case, the case-fold trap "0P" ----
e = "0P"
left, right = 0, len(e) - 1
add(act=3, cells=list(e), labels=list(range(len(e))), code="fast", line=0,
    intro="'0' and 'P' are both alphanumeric — a digit will not equal a letter.",
    invariant="lowercasing only touches letters; a digit stays a digit.",
    note="Edge case: \"0P\". Both are alphanumeric, so neither is skipped — they compare.",
    pointers={"L": left, "R": right}, window=[left, right],
    marks={str(left): "active", str(right): "active"},
    state=[["left", left], ["right", right]])
match = e[left].lower() == e[right].lower()
add(act=3, code="fast", line=4,
    note=f"'{e[left]}' vs '{e[right]}' lowercased = '{e[left].lower()}' vs '{e[right].lower()}'. "
         f"A digit is not a letter — mismatch.",
    pointers={"L": left, "R": right}, window=[left, right], arc=[left, right],
    marks={str(left): "bad", str(right): "bad"},
    state=[["result", "False"]],
    banner="Palindrome: False   ('0' != 'p')")

trace = {
    "player": "linear",
    "title": "Valid Palindrome — from two throwaway strings to one mirror walk",
    "acts": ["Filter and reverse", "The waste",
             "Fast: two pointers inward", "Edge case: \"0P\""],
    "code": {"clean": CLEAN, "fast": FAST},
    "legend": [["active", "current pointer"], ["good", "matched mirror pair"],
               ["bad", "mismatch"], ["dim", "skipped / filed"]],
    "cells": cells, "labels": list(range(len(cells))), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
