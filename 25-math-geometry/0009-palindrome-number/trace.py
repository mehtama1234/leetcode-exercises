"""Rich full-arc trace for Palindrome Number (linear renderer).
Test a palindrome without strings by reversing only the BACK half while the front
half shrinks, stopping when they meet in the middle. Arc: the idea (build the
reversed back half, stop at the midpoint) -> run an even-length case -> run an
odd-length case (drop the lone middle digit) -> a trailing-zero edge rejected up
front. Cells are the digits; the sidebar tracks front x and reversed back half.
Mirrors is_palindrome in solution.py. Writes trace.json.
"""
import json
import os

frames = []

CODE = [
    "if x < 0 or (x % 10 == 0 and x != 0): return False",
    "reversed_half = 0",
    "while x > reversed_half:",
    "    x, digit = divmod(x, 10)",
    "    reversed_half = reversed_half * 10 + digit",
    "return x == reversed_half or x == reversed_half // 10",
]


def add(**f):
    frames.append(f)


def cells_of(x):
    return [c for c in str(x)]


def sb(front, back):
    return {"title": "meet in the middle",
            "rows": [["front x", str(front)], ["reversed back", str(back)]]}


# ---- Act 0: the idea ----
V0 = 1221
add(act=0, cells=cells_of(V0), labels=list(range(len(str(V0)))), code="pal", line=0,
    intro="we never build the whole reverse — just enough back half to meet the front.",
    invariant="a palindrome reads the same both ways; halves must match at the middle.",
    note=f"Test {V0} without strings: peel digits off the RIGHT into reversed_half while "
    "the left front shrinks. Stop when front <= reversed back — they've met.",
    pointers={}, marks={},
    sidebar=sb(V0, 0), state=[["x", V0], ["reversed_half", 0]])

# ---- Act 1: even length 1221 ----
def run_even(x, act):
    orig = x
    ncells = len(str(x))
    rev = 0
    add(act=act, cells=cells_of(orig), labels=list(range(ncells)), code="pal", line=2,
        intro="even count: front and reversed back land exactly equal.",
        invariant="each step moves one digit from front's end to the back half.",
        note=f"Run {orig} (even length). Peel from the right until front x <= reversed back.",
        pointers={}, marks={}, sidebar=sb(x, rev),
        state=[["x", x], ["reversed_half", rev]])
    while x > rev:
        x, d = divmod(x, 10)
        rev = rev * 10 + d
        add(act=act, code="pal", line=4,
            note=f"peel {d}: front x -> {x}, reversed back -> {rev}."
                 + ("  Now x <= reversed: stop." if x <= rev else ""),
            pointers={}, marks={}, sidebar=sb(x, rev), cells=cells_of(orig),
            state=[["front x", x], ["reversed back", rev]])
    ok = x == rev or x == rev // 10
    add(act=act, code="pal", line=5,
        note=f"front {x} == reversed back {rev}: equal, so {orig} is a palindrome.",
        marks={str(k): "good" for k in range(ncells)},
        sidebar=sb(x, rev), state=[["front", x], ["back", rev], ["palindrome", ok]],
        banner=f"{orig} is a palindrome")
    return ok


run_even(V0, 1)

# ---- Act 2: odd length 12321 ----
V2 = 12321
x = V2
rev = 0
add(act=2, cells=cells_of(V2), labels=list(range(len(str(V2)))), code="pal", line=2,
    intro="odd count: a lone middle digit is left sitting in the front — drop it with //10.",
    invariant="the middle digit never needs to match anything.",
    note=f"Run {V2} (odd length). The center 3 will sit alone; we compare front to "
    "reversed_half // 10.",
    pointers={}, marks={}, sidebar=sb(x, rev), state=[["x", x], ["reversed_half", rev]])
while x > rev:
    x, d = divmod(x, 10)
    rev = rev * 10 + d
    add(act=2, code="pal", line=4,
        note=f"peel {d}: front x -> {x}, reversed back -> {rev}."
             + ("  x <= reversed: stop." if x <= rev else ""),
        pointers={}, marks={}, sidebar=sb(x, rev), cells=cells_of(V2),
        state=[["front x", x], ["reversed back", rev]])
ok2 = x == rev or x == rev // 10
add(act=2, code="pal", line=5,
    note=f"front {x} == reversed back // 10 = {rev // 10} (drop the middle 3): match, so "
         f"{V2} is a palindrome.",
    marks={str(k): "good" for k in range(len(str(V2)))},
    sidebar=sb(x, rev // 10), state=[["front", x], ["back//10", rev // 10], ["palindrome", ok2]],
    banner=f"{V2} is a palindrome (odd length)")

# ---- Act 3: trailing-zero edge ----
add(act=3, cells=cells_of(10), labels=[0, 1], code="pal", line=0,
    intro="a number ending in 0 (but not 0) can't be a palindrome — no leading 0 to match.",
    invariant="the first-line guard rejects negatives and trailing zeros up front.",
    note="Edge case: 10. It ends in 0 but isn't 0, so its reverse would start with 0 — "
    "impossible. The guard returns False before the loop.",
    marks={"0": "bad", "1": "bad"}, sidebar={"title": "guard", "rows": [["x % 10", "0"], ["x != 0", "true"]]},
    state=[["x", 10], ["palindrome", False]], banner="10 is NOT a palindrome")

trace = {
    "player": "linear",
    "title": "Palindrome Number - reverse only the back half, meet in the middle",
    "acts": ["The idea", "Even length: 1221", "Odd length: 12321", "Edge: trailing zero"],
    "code": {"pal": CODE},
    "legend": [["good", "halves match -> palindrome"], ["bad", "rejected"]],
    "cells": cells_of(V0), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
