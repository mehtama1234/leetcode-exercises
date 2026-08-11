"""Rich full-arc trace for Plus One (linear renderer).
Adding one to a number stored as a digit array, carrying by hand from the right.
Arc: the rule (a +1 only ripples through trailing 9s) -> run it where the carry
stops partway -> the all-nines edge that grows a digit. Cells are the digits,
most-significant left; a pointer walks from the right.
Mirrors plus_one in solution.py. Writes trace.json.
"""
import json
import os

digits = [1, 9, 9]  # -> [2, 0, 0]
frames = []

CODE = [
    "for i in reversed(range(len(digits))):",
    "    if digits[i] < 9:",
    "        digits[i] += 1",
    "        return digits          # no carry escapes",
    "    digits[i] = 0               # 9 -> 0, carry left",
    "return [1] + digits            # all nines",
]


def add(**f):
    frames.append(f)


def run(dig, act, intro=None, invariant=None, note=None):
    dig = dig[:]
    labels = list(range(len(dig)))
    add(act=act, cells=[str(d) for d in dig], labels=labels, code="add", line=0,
        intro=intro, invariant=invariant, note=note,
        pointers={"i": len(dig) - 1}, marks={str(len(dig) - 1): "active"},
        state=[["number", "".join(map(str, dig))], ["carry", 1]])
    for i in range(len(dig) - 1, -1, -1):
        if dig[i] < 9:
            dig[i] += 1
            add(act=act, code="add", line=2,
                note=f"digit {i} is {dig[i] - 1} < 9: bump to {dig[i]}. No carry escapes, done.",
                pointers={"i": i}, marks={str(i): "good",
                                          **{str(k): "dim" for k in range(i)}},
                cells=[str(d) for d in dig],
                state=[["result", "".join(map(str, dig))], ["carry", 0]])
            return dig, False
        dig[i] = 0
        add(act=act, code="add", line=4,
            note=f"digit {i} is 9: 9+1 = 10 -> write 0, carry the 1 left.",
            pointers={"i": i}, marks={str(i): "bad"}, cells=[str(d) for d in dig],
            state=[["digit " + str(i), 0], ["carry", 1]])
    grown = [1] + dig
    add(act=act, code="add", line=5,
        note="Fell off the left end still carrying: prepend a 1. The number grew a digit.",
        cells=[str(d) for d in grown], labels=list(range(len(grown))),
        marks={"0": "good", **{str(k): "dim" for k in range(1, len(grown))}},
        state=[["result", "".join(map(str, grown))]])
    return grown, True


# ---- Act 0: the rule ----
add(act=0, cells=[str(d) for d in digits], labels=list(range(len(digits))), code="add", line=0,
    intro="a +1 only ripples through a run of trailing 9s, then stops.",
    invariant="once a digit < 9 is bumped, no carry can escape further left.",
    note="Add one to a number stored as digits (most-significant left). Start at the "
    "rightmost digit and carry left, exactly like adding on paper.",
    pointers={"i": len(digits) - 1}, marks={str(len(digits) - 1): "active"},
    state=[["number", "199"], ["add", 1]])

# ---- Act 1: run it, carry stops partway ----
run(digits, 1,
    intro="the two trailing 9s roll to 0, then the 1 catches the +1 and stops.",
    invariant="the carry dies at the first non-9 digit.",
    note="Run 199 + 1: rightmost 9 -> 0 (carry), next 9 -> 0 (carry), the 1 becomes 2 and "
    "the carry stops -> 200.")
add(act=1, note="199 + 1 = 200. The carry only had to walk the two trailing nines.",
    cells=["2", "0", "0"], labels=[0, 1, 2], code="add", line=3,
    marks={"0": "good", "1": "good", "2": "good"},
    state=[["answer", "200"]], banner="199 + 1 = 200")

# ---- Act 2: all-nines edge ----
add(act=2, cells=["9", "9", "9"], labels=[0, 1, 2], code="add", line=0,
    intro="every digit is 9, so the carry never dies — it falls off the left.",
    invariant="all nines is the only case where the number grows a digit.",
    note="Edge case: 999 + 1. Each 9 becomes 0 and passes the carry on; the carry escapes "
    "the left end.",
    pointers={"i": 2}, marks={"2": "active"},
    state=[["number", "999"], ["carry", 1]])
run([9, 9, 9], 2)
add(act=2, note="999 + 1 = 1000 — a fresh leading 1 and all zeros. One digit longer.",
    cells=["1", "0", "0", "0"], labels=[0, 1, 2, 3], code="add", line=5,
    marks={"0": "good", "1": "dim", "2": "dim", "3": "dim"},
    state=[["answer", "1000"]], banner="999 + 1 = 1000 (grows a digit)")

trace = {
    "player": "linear",
    "title": "Plus One - carry a +1 through the digits, by hand",
    "acts": ["The rule", "Run: carry stops partway", "Edge: all nines"],
    "code": {"add": CODE},
    "legend": [["active", "digit we're adding to"], ["bad", "9 -> 0, carry left"],
               ["good", "final digit / answer"], ["dim", "unchanged / new zeros"]],
    "cells": [str(d) for d in digits], "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
