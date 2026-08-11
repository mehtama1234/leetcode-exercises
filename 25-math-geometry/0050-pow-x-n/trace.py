"""Rich full-arc trace for Pow(x, n) (linear renderer).
Arc: naive (multiply n times) -> the waste -> exponentiation by squaring, reading
the exponent's bits low-to-high -> a negative-exponent edge case. The cells are the
binary digits of the exponent; the sidebar tracks current = x^(2^bit) and result.
Mirrors my_pow_naive / my_pow in solution.py. Writes trace.json.
"""
import json
import os

X, N = 2.0, 10  # 2^10 = 1024
frames = []

NAIVE = [
    "result = 1.0",
    "for _ in range(n):",
    "    result *= x",
    "return result",
]
FAST = [
    "result, current = 1.0, x",
    "while n > 0:",
    "    if n & 1:",
    "        result *= current",
    "    current *= current   # x^2, x^4, x^8...",
    "    n >>= 1",
    "return result",
]


def add(**f):
    frames.append(f)


bits = [int(b) for b in bin(N)[2:]][::-1]  # low bit first: 10 -> [0,1,0,1]
bit_cells = [str(b) for b in bits]
bit_labels = [f"2^{i}" for i in range(len(bits))]


# ---- Act 0: naive multiply n times ----
add(act=0, cells=[str(N)], labels=["n"], code="naive", line=0,
    intro="one multiply per unit of n — count them climb.",
    invariant="result = x multiplied by itself (count) times.",
    note=f"Naive power: multiply x by itself n times. For 2^{N} that is {N} multiplies; "
    "for n = 2 billion it is 2 billion.",
    pointers={}, marks={}, state=[["x", X], ["n", N], ["multiplies", 0]])
result = 1.0
for k in range(N):
    result *= X
    add(act=0, code="naive", line=2,
        note=f"multiply {k + 1}: result = {result:g}.",
        pointers={}, marks={},
        state=[["step", k + 1], ["result", f"{result:g}"], ["multiplies", k + 1]])
add(act=0, code="naive", line=3,
    note=f"2^{N} = {result:g}, but it took {N} multiplies — and this grows linearly with n.",
    marks={}, state=[["answer", f"{result:g}"], ["multiplies", N]])

# ---- Act 1: the waste ----
add(act=1,
    intro="x^10 = (x^5)^2, and x^5 = (x^2)^2 * x — the same squares reused.",
    note=f"Multiplying one at a time redoes work: once you know x^5 you get x^10 by one "
    "squaring, not five more multiplies. The repeated single steps are the waste.",
    marks={}, state=[["multiplies (naive)", N], ["pattern", "~ n"]])
add(act=1,
    note=f"Read n in binary: {N} = {bin(N)[2:]}. Each 1-bit says 'this power of two is "
    "present.' Square to climb powers of two, multiply in only where a bit is 1.",
    marks={}, state=[["n in binary", bin(N)[2:]], ["what we want", "~ log n"]])

# ---- Act 2: exponentiation by squaring ----
add(act=2, cells=bit_cells, labels=bit_labels, code="fast", line=0,
    intro="cells are n's bits (low first); current doubles its exponent each step.",
    invariant="current = x^(2^bit); result folds in current only where the bit is 1.",
    note=f"n = {N} = binary {bin(N)[2:]} (read low bit first: {''.join(bit_cells)}). Keep "
    "current = x, x^2, x^4, x^8 and fold it into result at each 1-bit.",
    pointers={"bit": 0}, marks={},
    sidebar={"title": "running", "rows": [["current", f"{X:g}"], ["result", "1"]]},
    state=[["result", 1], ["current", f"{X:g}"], ["multiplies", 0]])
result = 1.0
current = X
n = N
mults = 0
idx = 0
while n > 0:
    take = n & 1
    if take:
        result *= current
        mults += 1
        add(act=2, code="fast", line=3,
            note=f"bit {idx} (2^{idx}) is 1: fold current {current:g} into result -> "
                 f"{result:g}.",
            pointers={"bit": idx}, marks={str(idx): "good"},
            sidebar={"title": "running", "rows": [["current", f"{current:g}"], ["result", f"{result:g}"]]},
            state=[["bit", idx], ["current", f"{current:g}"], ["result", f"{result:g}"],
                   ["multiplies", mults]])
    else:
        add(act=2, code="fast", line=2,
            note=f"bit {idx} (2^{idx}) is 0: skip, this power of x is not in the exponent.",
            pointers={"bit": idx}, marks={str(idx): "dim"},
            sidebar={"title": "running", "rows": [["current", f"{current:g}"], ["result", f"{result:g}"]]},
            state=[["bit", idx], ["current", f"{current:g}"], ["result", f"{result:g}"]])
    current *= current
    mults += 1
    n >>= 1
    idx += 1
    if n > 0:
        add(act=2, code="fast", line=4,
            note=f"Square current to reach x^(2^{idx}) = {current:g}; drop the used bit.",
            pointers={"bit": idx}, marks={str(idx): "active"},
            sidebar={"title": "running", "rows": [["current", f"{current:g}"], ["result", f"{result:g}"]]},
            state=[["current", f"{current:g}"], ["multiplies", mults]])
add(act=2, code="fast", line=6,
    note=f"2^{N} = {result:g} in {mults} multiplies instead of {N} — log n, not n.",
    marks={str(i): "good" for i, b in enumerate(bits) if b},
    sidebar={"title": "running", "rows": [["result", f"{result:g}"]]},
    state=[["answer", f"{result:g}"], ["multiplies", mults], ["vs naive", N]],
    banner=f"2^{N} = {result:g}   ({mults} multiplies vs {N} naive)")

# ---- Act 3: negative exponent edge ----
ex_x, ex_n = 2.0, -2
bits_e = [int(b) for b in bin(2)[2:]][::-1]  # |n|=2 -> [0,1]
add(act=3, cells=[str(b) for b in bits_e], labels=[f"2^{i}" for i in range(len(bits_e))],
    code="fast", line=0,
    intro="negative n: flip x to 1/x, make n positive, then the same squaring runs.",
    invariant="x^(-n) = (1/x)^n; the bit loop is unchanged.",
    note="Edge case: 2^-2. Replace x with 1/x = 0.5 and n with 2, then run the same "
    "squaring loop.",
    pointers={"bit": 0}, marks={},
    sidebar={"title": "running", "rows": [["x -> 1/x", "0.5"], ["result", "1"]]},
    state=[["x", 0.5], ["n", 2]])
result = 1.0
current = 1 / ex_x
n = 2
idx = 0
while n > 0:
    if n & 1:
        result *= current
        add(act=3, code="fast", line=3,
            note=f"bit {idx} is 1: result *= current {current:g} -> {result:g}.",
            pointers={"bit": idx}, marks={str(idx): "good"},
            sidebar={"title": "running", "rows": [["current", f"{current:g}"], ["result", f"{result:g}"]]},
            state=[["result", f"{result:g}"]])
    else:
        add(act=3, code="fast", line=4,
            note=f"bit {idx} is 0: skip; square current {current:g} -> {current * current:g}.",
            pointers={"bit": idx}, marks={str(idx): "dim"},
            sidebar={"title": "running", "rows": [["current", f"{current:g}"], ["result", f"{result:g}"]]},
            state=[["current", f"{current * current:g}"]])
    current *= current
    n >>= 1
    idx += 1
add(act=3, code="fast", line=6, note=f"2^-2 = {result:g} = 1/4.",
    marks={"1": "good"}, sidebar={"title": "running", "rows": [["result", f"{result:g}"]]},
    state=[["answer", f"{result:g}"]], banner="2^-2 = 0.25")

trace = {
    "player": "linear",
    "title": "Pow(x, n) - square through the exponent's bits, not n multiplies",
    "acts": ["Naive: multiply n times", "The waste", "Squaring by bits", "Edge: negative n"],
    "code": {"naive": NAIVE, "fast": FAST},
    "legend": [["good", "bit is 1: folded into result"], ["active", "next power of two"],
               ["dim", "bit is 0: skipped"]],
    "cells": bit_cells, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
