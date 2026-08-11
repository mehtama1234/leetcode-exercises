"""Rich full-arc trace for Reverse Bits (linear renderer, cells = individual bits).
Bit manipulation has no wasteful baseline, so the arc is: the rule -> peel and
push each bit in one pass -> an edge case (a palindrome that reverses to itself).
Uses an 8-bit example for a readable row (the real code loops 32 times, same
mechanic). Mirrors reverse_bits in solution.py. Writes trace.json.
"""
import json
import os

WIDTH = 8               # 8-bit example so the row fits; real code uses 32
N = 0b10110010          # 178 -> reversed reads 0100 1101 = 0x4D = 77
frames = []

CODE = [
    "result = 0",
    "for _ in range(32):",
    "    result = (result << 1) | (n & 1)",
    "    n >>= 1",
    "return result & 0xFFFFFFFF",
]


def add(**f):
    frames.append(f)


def bits(x, width=WIDTH):
    # MSB-first list of bit values, index 0 = leftmost (highest) bit
    return [(x >> (width - 1 - i)) & 1 for i in range(width)]


# labels: bit position under each cell (leftmost is the high bit)
POS = [WIDTH - 1 - i for i in range(WIDTH)]  # [7,6,5,4,3,2,1,0]

# ---- Act 0: the rule ----
add(act=0, cells=bits(N), labels=POS, code="rev", line=0,
    intro="the FIRST bit we read (position 0) gets shifted left the most — it lands "
    "at the top. That is reversal.",
    invariant="result grows from the bottom while n shrinks from the bottom.",
    note=f"Reverse the bits of {N} ({''.join(map(str, bits(N)))}). Read n from its "
    "lowest bit; push each bit onto the top of a growing result.",
    pointers={"bit 0": WIDTH - 1}, marks={str(WIDTH - 1): "active"},
    state=[["n", "".join(map(str, bits(N)))], ["result", "".join(map(str, bits(0)))]])

# ---- Act 1: peel and push, one pass ----
n = N
result = 0
add(act=1, cells=bits(N), labels=POS, code="rev", line=0,
    intro="each step: read n's lowest bit, then shift n right so the next bit "
    "becomes the lowest.",
    invariant="after k steps, result holds the first k bits of n, order flipped.",
    note="result starts at 0. We take 8 steps (32 in the real code), one per bit.",
    pointers={"read": WIDTH - 1}, marks={str(WIDTH - 1): "active"},
    state=[["result", "".join(map(str, bits(0)))], ["step", 0]])

for step in range(WIDTH):
    low = n & 1
    read_idx = WIDTH - 1            # n's lowest bit sits at the rightmost cell
    add(act=1, cells=bits(n), labels=POS, code="rev", line=2,
        note=f"Step {step + 1}: n's lowest bit is {low}. Shift result left one slot, "
        f"then drop {low} into the freshly opened bottom.",
        pointers={"read": read_idx}, marks={str(read_idx): "active"},
        state=[["n", "".join(map(str, bits(n)))], ["n & 1", low],
               ["result before", "".join(map(str, bits(result)))]])
    result = (result << 1) | low
    n >>= 1
    add(act=1, cells=bits(result), labels=POS, code="rev", line=3,
        note=f"result is now {''.join(map(str, bits(result)))}; that {low} sits at the "
        "bottom and will keep climbing as later bits push in.",
        pointers={"just pushed": WIDTH - 1}, marks={str(WIDTH - 1): "good"},
        state=[["result", "".join(map(str, bits(result)))],
               ["step", step + 1], ["bits left", WIDTH - step - 1]])

add(act=1, cells=bits(result), labels=POS, code="rev", line=4,
    note=f"All bits consumed. {''.join(map(str, bits(N)))} reversed is "
    f"{''.join(map(str, bits(result)))} = {result}. The bit once at position 0 now "
    "sits at the top.",
    marks={str(i): "good" for i in range(WIDTH)},
    state=[["input", N], ["reversed", result]],
    banner=f"{''.join(map(str, bits(N)))} -> {''.join(map(str, bits(result)))}   ({N} -> {result})")

# ---- Act 2: edge case — a palindrome reverses to itself ----
E = 0b10011001          # symmetric: reversing gives the same bits
en = E
eres = 0
add(act=2, cells=bits(E), labels=POS, code="rev", line=0,
    intro="if the bit pattern reads the same forwards and backwards, reversal is a "
    "no-op.",
    invariant="the same peel-and-push runs; the output just equals the input.",
    note=f"Edge case: {''.join(map(str, bits(E)))} is a mirror image of itself. "
    "Reversing it should return the same number.",
    pointers={"read": WIDTH - 1}, marks={str(WIDTH - 1): "active"},
    state=[["n", "".join(map(str, bits(E)))]])
for _ in range(WIDTH):
    eres = (eres << 1) | (en & 1)
    en >>= 1
add(act=2, cells=bits(eres), labels=POS, code="rev", line=4,
    note=f"After 8 steps result is {''.join(map(str, bits(eres)))} — identical to the "
    "input. A palindrome pattern is its own reverse. (All-zeros and all-ones behave "
    "the same way.)",
    marks={str(i): "good" for i in range(WIDTH)},
    state=[["input", E], ["reversed", eres]],
    banner=f"{''.join(map(str, bits(E)))} reverses to itself")

trace = {
    "player": "linear",
    "title": "Reverse Bits - peel each bit off the bottom, push it onto the top",
    "acts": ["The rule", "Peel and push, one pass", "Edge: a palindrome"],
    "code": {"rev": CODE},
    "legend": [["active", "bit being read"], ["good", "bit placed in result"]],
    "cells": bits(N), "labels": POS, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
