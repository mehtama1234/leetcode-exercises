"""Rich full-arc trace for Number of 1 Bits (linear renderer, cells = bits).
Arc: brute scan every bit position -> name the waste (it always runs 32 steps) ->
Brian Kernighan clears one set bit per step -> edge case (all bits set). Cells are
the individual bits; a pointer marks the bit being examined or cleared; state
tracks the running count. Mirrors both functions in solution.py. Writes trace.json.
"""
import json
import os

WIDTH = 8               # 8-bit example for a readable row; real code is 32-bit
N = 0b10010100          # 148 -> three set bits
frames = []

SCAN = [
    "count = 0",
    "while n:",
    "    count += n & 1",
    "    n >>= 1",
    "return count",
]
KERNIGHAN = [
    "count = 0",
    "while n:",
    "    n &= n - 1   # clear lowest set bit",
    "    count += 1",
    "return count",
]


def add(**f):
    frames.append(f)


def bits(x, width=WIDTH):
    return [(x >> (width - 1 - i)) & 1 for i in range(width)]


POS = [WIDTH - 1 - i for i in range(WIDTH)]  # bit positions [7..0]
SETBITS = bin(N).count("1")

# ---- Act 0: brute scan every position ----
add(act=0, cells=bits(N), labels=POS, code="scan", line=0,
    intro="every bit position gets looked at, set or not — the loop length is fixed.",
    invariant="count = number of 1s seen among the positions we have passed.",
    note=f"Count the 1-bits of {''.join(map(str, bits(N)))}. Brute scan: look at the "
    "lowest bit, add it, shift right, repeat.",
    pointers={"look": WIDTH - 1}, marks={str(WIDTH - 1): "active"},
    state=[["n", "".join(map(str, bits(N)))], ["count", 0]])

n = N
count = 0
steps = 0
# scan while n != 0, but for the animation walk the full 8 positions to show the
# fixed-length cost; count only real bits examined until n becomes 0.
for pos in range(WIDTH):
    low = n & 1
    steps += 1
    read_idx = WIDTH - 1
    count += low
    add(act=0, cells=bits(n), labels=POS, code="scan", line=2,
        note=f"Lowest bit is {low}. count -> {count}. Shift n right so the next bit "
        "drops into place.",
        pointers={"look": read_idx},
        marks={str(read_idx): "good" if low else "bad"},
        state=[["n", "".join(map(str, bits(n)))], ["n & 1", low],
               ["count", count], ["steps", steps]])
    n >>= 1
    if n == 0:
        add(act=0, cells=bits(0), labels=POS, code="scan", line=1,
            note=f"n is 0 now, so the loop can stop. It took {steps} shifts to find "
            f"{count} ones. In the 32-bit version it is 32 shifts no matter what.",
            marks={str(i): "dim" for i in range(WIDTH)},
            state=[["count", count], ["steps", steps]])
        break

# ---- Act 1: name the waste ----
add(act=1, cells=bits(N), labels=POS, code=None,
    intro="the scan touches leading zeros it will never count — pure overhead.",
    invariant="only the 1-bits actually matter to the answer.",
    note=f"The scan does one step per bit position. For a 32-bit number that is 32 "
    f"steps even though only {SETBITS} of them are 1s.",
    marks={str(i): ("good" if bits(N)[i] else "bad") for i in range(WIDTH)},
    state=[["set bits", SETBITS], ["scan steps (32-bit)", 32]])
add(act=1, cells=bits(N), labels=POS, code=None,
    note="For a sparse number like 1000...0001 the scan still walks all 32 bits to "
    "count 2 ones. We want steps = number of set bits, not number of positions.",
    marks={str(i): "bad" for i in range(WIDTH) if bits(N)[i] == 0},
    state=[["want steps", SETBITS], ["scan steps", 32]])

# ---- Act 2: Brian Kernighan, one step per set bit ----
n = N
count = 0
steps = 0
add(act=2, cells=bits(N), labels=POS, code="kern", line=0,
    intro="n & (n-1) erases exactly the lowest 1-bit, so each step removes one 1.",
    invariant="count = 1-bits already cleared; n holds the ones still to remove.",
    note="Brian Kernighan: n & (n - 1) clears the lowest set bit. Loop until n is 0; "
    "each turn of the loop kills exactly one 1.",
    pointers={"lowest 1": max(i for i in range(WIDTH) if bits(N)[i] == 1)},
    marks={str(max(i for i in range(WIDTH) if bits(N)[i] == 1)): "active"},
    state=[["n", "".join(map(str, bits(N)))], ["count", 0]])

while n:
    lowset = max(i for i in range(WIDTH) if bits(n)[i] == 1)  # rightmost 1
    steps += 1
    add(act=2, cells=bits(n), labels=POS, code="kern", line=2,
        note=f"Lowest set bit is at position {WIDTH - 1 - lowset}. n & (n-1) wipes it "
        "in one move — no walking past zeros.",
        pointers={"clear": lowset}, marks={str(lowset): "active"},
        state=[["n", "".join(map(str, bits(n)))], ["step", steps]])
    n &= n - 1
    count += 1
    add(act=2, cells=bits(n), labels=POS, code="kern", line=3,
        note=f"That 1 is gone; count -> {count}. n is now "
        f"{''.join(map(str, bits(n)))}.",
        marks={str(lowset): "good"},
        state=[["n", "".join(map(str, bits(n)))], ["count", count],
               ["steps", steps]])

add(act=2, cells=bits(0), labels=POS, code="kern", line=4,
    note=f"n reached 0 after {steps} steps — exactly the number of set bits, not the "
    f"number of positions. Answer: {count}.",
    marks={str(i): "dim" for i in range(WIDTH)},
    state=[["count", count], ["steps", steps], ["vs scan", 32]],
    banner=f"{SETBITS} set bits in {steps} steps  (scan would take 32)")

# ---- Act 3: edge case — all bits set ----
E = 0b11111111
en = E
ecount = 0
add(act=3, cells=bits(E), labels=POS, code="kern", line=0,
    intro="every bit is a 1, so this is the one case where both methods do equal work.",
    invariant="each step still clears exactly one bit from the bottom.",
    note=f"Edge case: all bits set ({''.join(map(str, bits(E)))}). Kernighan runs once "
    "per bit here, since every bit is a 1 to clear.",
    pointers={"clear": WIDTH - 1}, marks={str(WIDTH - 1): "active"},
    state=[["n", "".join(map(str, bits(E)))], ["count", 0]])
while en:
    en &= en - 1
    ecount += 1
add(act=3, cells=bits(0), labels=POS, code="kern", line=4,
    note=f"All {ecount} bits cleared, one per step. For all-ones the answer equals the "
    "width. (For n = 0 the loop never runs and the answer is 0.)",
    marks={str(i): "good" for i in range(WIDTH)},
    state=[["count", ecount]],
    banner=f"All bits set -> count = {ecount}")

trace = {
    "player": "linear",
    "title": "Number of 1 Bits - from scan-every-position to clear-one-bit-per-step",
    "acts": ["Brute: scan every position", "The waste", "Kernighan: clear a bit each step", "Edge: all bits set"],
    "code": {"scan": SCAN, "kern": KERNIGHAN},
    "legend": [["active", "bit being examined / cleared"], ["good", "a 1 counted / cleared"],
               ["bad", "a 0 (wasted look)"], ["dim", "finished"]],
    "cells": bits(N), "labels": POS, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
