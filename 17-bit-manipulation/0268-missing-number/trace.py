"""Rich full-arc trace for Missing Number (linear renderer, cells = bits of acc).
Arc: the XOR facts (x^x=0, x^0=x) -> fold every index and value into one
accumulator so pairs cancel -> the survivor is the missing value -> edge case.
Cells are the individual bits of the running accumulator; the pointer marks the
bit being flipped this step; a sidebar tracks i, value, and the operand XORed in.
Mirrors missing_number (the XOR version) in solution.py. Writes trace.json.
"""
import json
import os

NUMS = [3, 0, 1]        # n = 3, missing 2
WIDTH = 4               # 4 bits hold values 0..3 comfortably
frames = []

CODE = [
    "acc = len(nums)      # = n, folds in top of range",
    "for i, x in enumerate(nums):",
    "    acc ^= i ^ x",
    "return acc",
]


def add(**f):
    frames.append(f)


def bits(x, width=WIDTH):
    return [(x >> (width - 1 - i)) & 1 for i in range(width)]


POS = [WIDTH - 1 - i for i in range(WIDTH)]
n = len(NUMS)


def diff_marks(before, after):
    # mark the bits that flipped between two accumulator values
    b, a = bits(before), bits(after)
    return {str(i): ("active" if b[i] != a[i] else "dim") for i in range(WIDTH)}


# ---- Act 0: the XOR facts ----
add(act=0, cells=bits(0), labels=POS, code=None,
    intro="a value XORed with itself vanishes; that is what makes the pairs cancel.",
    invariant="XOR is order-free, so we can fold indices and values in any order.",
    note="Two facts: x ^ x = 0 (a value cancels itself) and x ^ 0 = x. Every number "
    "in 0..n appears as an index; every array value appears once. Fold them all and "
    "the matched pairs cancel to 0.",
    marks={str(i): "dim" for i in range(WIDTH)},
    state=[["nums", str(NUMS)], ["range", f"0..{n}"], ["missing", "one value"]])
add(act=0, cells=bits(0), labels=POS, code=None,
    note="The missing value shows up as an index (0..n) but never as a value, so it "
    "has no partner to cancel with — it is the lone survivor.",
    marks={str(i): "dim" for i in range(WIDTH)},
    state=[["indices", f"0..{n}"], ["values", "n of them"], ["unpaired", "1"]])

# ---- Act 1: fold everything into acc ----
acc = n
add(act=1, cells=bits(acc), labels=POS, code="xor", line=0,
    intro="acc starts at n because indices only reach n-1 but values reach n.",
    invariant="acc = XOR of everything folded so far; cancelled pairs leave no trace.",
    note=f"Seed acc = n = {n} ({''.join(map(str, bits(n)))}). This folds in the top of "
    "the value range, which no index provides.",
    marks={str(i): ("good" if bits(acc)[i] else "dim") for i in range(WIDTH)},
    state=[["acc", "".join(map(str, bits(acc)))], ["seed", n]])

for i, x in enumerate(NUMS):
    before = acc
    operand = i ^ x
    add(act=1, cells=bits(before), labels=POS, code="xor", line=2,
        note=f"i={i}, value={x}. Fold in i ^ x = {i} ^ {x} = {operand}. XOR flips acc's "
        f"bits wherever {operand} has a 1.",
        marks={str(j): ("active" if bits(operand)[j] else "dim") for j in range(WIDTH)},
        state=[["i", i], ["x", x], ["i ^ x", operand],
               ["acc", "".join(map(str, bits(before)))]])
    acc ^= operand
    add(act=1, cells=bits(acc), labels=POS, code="xor", line=2,
        note=f"acc is now {''.join(map(str, bits(acc)))} = {acc}. "
        + (f"Value {x} at index {x} will cancel later." if acc != 2 or i < len(NUMS) - 1
           else "Only the missing value's bits are left standing."),
        marks=diff_marks(before, acc),
        state=[["acc", "".join(map(str, bits(acc)))], ["acc value", acc]])

add(act=1, cells=bits(acc), labels=POS, code="xor", line=3,
    note=f"Every paired index/value cancelled to 0. What remains is {acc} — the missing "
    "number.",
    marks={str(i): ("good" if bits(acc)[i] else "dim") for i in range(WIDTH)},
    state=[["missing", acc]],
    banner=f"Missing number = {acc}   (nums = {NUMS}, range 0..{n})")

# ---- Act 2: edge case — missing the bottom of the range ----
E = [1]                 # n = 1, missing 0
en = len(E)
eacc = en
add(act=2, cells=bits(eacc), labels=POS, code="xor", line=0,
    intro="the missing value can be 0 — then acc must end at all-zero bits.",
    invariant="the same fold runs; the survivor just happens to be 0.",
    note="Edge case: nums = [1], range 0..1, missing 0. Seed acc = n = 1, then fold in "
    "i=0, value=1.",
    marks={str(i): ("good" if bits(eacc)[i] else "dim") for i in range(WIDTH)},
    state=[["nums", str(E)], ["acc seed", en]])
for i, x in enumerate(E):
    before = eacc
    eacc ^= i ^ x
    add(act=2, cells=bits(eacc), labels=POS, code="xor", line=2,
        note=f"i={i}, value={x}: fold i ^ x = {i ^ x}. acc -> "
        f"{''.join(map(str, bits(eacc)))}. The 1 from the seed cancels the value 1.",
        marks=diff_marks(before, eacc),
        state=[["i ^ x", i ^ x], ["acc", "".join(map(str, bits(eacc)))]])
add(act=2, cells=bits(eacc), labels=POS, code="xor", line=3,
    note=f"acc ended at 0 — and 0 is exactly the missing value. XOR handles a missing "
    "bottom-of-range just as cleanly as any other.",
    marks={str(i): "good" for i in range(WIDTH)},
    state=[["missing", eacc]],
    banner=f"Missing number = {eacc}")

trace = {
    "player": "linear",
    "title": "Missing Number - XOR every index and value; the survivor is the gap",
    "acts": ["The XOR facts", "Fold everything into acc", "Edge: missing 0"],
    "code": {"xor": CODE},
    "legend": [["active", "bit flipped this step"], ["good", "a 1 in the current value"],
               ["dim", "a 0 / settled bit"]],
    "cells": bits(0), "labels": POS, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
