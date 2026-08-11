"""Rich full-arc trace for Sum of Two Integers (linear renderer, cells = bits).
Bit-addition has no wasteful baseline, so the arc is: the rule (XOR = add without
carry, AND<<1 = the carry) -> loop until no carry is left -> edge case (adding 0).
Cells are the bits of `a` (the running carry-free sum); a pointer marks where a new
carry is produced; a sidebar tracks a, b, and the carry each pass. Uses small
positive inputs for a readable row; mirrors get_sum in solution.py (the sign/mask
handling only matters for negatives). Writes trace.json.
"""
import json
import os

A0, B0 = 3, 5           # 3 + 5 = 8
WIDTH = 5               # 5 bits hold the result 8 = 01000
frames = []

CODE = [
    "while b != 0:",
    "    carry = (a & b) << 1",
    "    a = (a ^ b) & MASK",
    "    b = carry & MASK",
    "return a",
]


def add(**f):
    frames.append(f)


def bits(x, width=WIDTH):
    return [(x >> (width - 1 - i)) & 1 for i in range(width)]


POS = [WIDTH - 1 - i for i in range(WIDTH)]


def sidebar(a, b, carry):
    return {"title": "registers", "rows": [
        ["a  (sum)", "".join(map(str, bits(a)))],
        ["b  (carry in)", "".join(map(str, bits(b)))],
        ["carry out", "".join(map(str, bits(carry)))],
    ]}


def carry_marks(a, b):
    # positions where a AND b are both 1 -> a carry is generated here
    both = a & b
    return {str(i): "active" for i in range(WIDTH) if bits(both)[i] == 1}


# ---- Act 0: the rule ----
add(act=0, cells=bits(A0), labels=POS, code="add", line=0,
    intro="XOR adds each column ignoring carry; AND finds where a carry is born.",
    invariant="a always holds the sum-so-far without the pending carry.",
    note=f"Add {A0} + {B0} without + or -. Split each column: a ^ b is the sum "
    "ignoring carry, and (a & b) << 1 is the carry, shifted one column left.",
    marks={str(i): ("good" if bits(A0)[i] else "dim") for i in range(WIDTH)},
    sidebar=sidebar(A0, B0, 0),
    state=[["a", "".join(map(str, bits(A0)))], ["b", "".join(map(str, bits(B0)))]])

# ---- Act 1: loop until no carry ----
a, b = A0, B0
add(act=1, cells=bits(a), labels=POS, code="add", line=0,
    intro="the carry keeps sliding left; when it runs out, a is the answer.",
    invariant="a ^ b plus (a & b) << 1 always equals the true total.",
    note="Repeat: fold the carry-free sum into a and the new carry into b, until b "
    "(the carry) becomes 0.",
    marks=carry_marks(a, b),
    sidebar=sidebar(a, b, 0),
    state=[["pass", 0], ["a", "".join(map(str, bits(a)))],
           ["b", "".join(map(str, bits(b)))]])

MASK = 0xFFFFFFFF
p = 0
while b != 0:
    p += 1
    carry = (a & b) << 1
    add(act=1, cells=bits(a), labels=POS, code="add", line=1,
        note=f"Pass {p}: columns where a & b are both 1 make a carry. carry = "
        f"(a & b) << 1 = {''.join(map(str, bits(carry)))} (shifted one column left).",
        marks=carry_marks(a, b),
        sidebar=sidebar(a, b, carry),
        state=[["pass", p], ["a & b", "".join(map(str, bits(a & b)))],
               ["carry", "".join(map(str, bits(carry)))]])
    new_a = (a ^ b) & MASK
    add(act=1, cells=bits(new_a), labels=POS, code="add", line=2,
        note=f"a = a ^ b = {''.join(map(str, bits(new_a)))} — every column added "
        "without its carry.",
        marks={str(i): ("good" if bits(new_a)[i] else "dim") for i in range(WIDTH)},
        sidebar=sidebar(new_a, b, carry),
        state=[["pass", p], ["a (new)", "".join(map(str, bits(new_a)))]])
    a = new_a
    b = carry & MASK
    add(act=1, cells=bits(a), labels=POS, code="add", line=3,
        note=f"b takes the carry: {''.join(map(str, bits(b)))}. "
        + ("Carry is 0 now — done." if b == 0 else "Still a carry, so loop again."),
        marks=carry_marks(a, b) if b else {},
        sidebar=sidebar(a, b, 0),
        state=[["pass", p], ["b", "".join(map(str, bits(b)))],
               ["a", "".join(map(str, bits(a)))]])

add(act=1, cells=bits(a), labels=POS, code="add", line=4,
    note=f"No carry left. a = {''.join(map(str, bits(a)))} = {a}. That is {A0} + {B0} "
    "with no + used.",
    marks={str(i): "good" for i in range(WIDTH)},
    sidebar=sidebar(a, 0, 0),
    state=[["answer", a], ["passes", p]],
    banner=f"{A0} + {B0} = {a}   (in {p} carry passes, no + operator)")

# ---- Act 2: edge case — adding 0 ----
ea, eb = 6, 0
add(act=2, cells=bits(ea), labels=POS, code="add", line=0,
    intro="if b is 0 there is no carry to fold — the loop body never runs.",
    invariant="a starts as the answer and stays it.",
    note=f"Edge case: {ea} + 0. b is already 0, so the while loop never executes and a "
    "is returned unchanged.",
    marks={str(i): ("good" if bits(ea)[i] else "dim") for i in range(WIDTH)},
    sidebar=sidebar(ea, eb, 0),
    state=[["a", "".join(map(str, bits(ea)))], ["b", "".join(map(str, bits(eb)))]])
add(act=2, cells=bits(ea), labels=POS, code="add", line=4,
    note=f"Loop skipped, return a = {ea}. (Negatives use the same loop, with a 32-bit "
    "mask so the carry can't shift off forever, then a sign-bit fix at the end.)",
    marks={str(i): "good" for i in range(WIDTH)},
    sidebar=sidebar(ea, 0, 0),
    state=[["answer", ea]],
    banner=f"{ea} + 0 = {ea}  (loop runs zero times)")

trace = {
    "player": "linear",
    "title": "Sum of Two Integers - XOR is the sum, AND<<1 is the carry, loop till it clears",
    "acts": ["The rule", "Loop until no carry", "Edge: adding 0"],
    "code": {"add": CODE},
    "legend": [["active", "column making a carry"], ["good", "a 1 in the running sum"],
               ["dim", "a 0"]],
    "cells": bits(A0), "labels": POS, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
