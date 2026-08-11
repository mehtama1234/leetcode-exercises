"""Rich full-arc trace for Multiply Strings (linear renderer).
Grade-school long multiplication by hand. Arc: the rule (digit i * digit j lands
in place i+j from the right) -> accumulate every partial product into a result
array -> settle carries left to right -> read off, dropping leading zeros ->
a zero edge case. Cells are the result-array places (units on the right); the
sidebar lists the partial products feeding the current place.
Mirrors multiply in solution.py. Writes trace.json.
"""
import json
import os

num1, num2 = "123", "456"  # 56088
frames = []

CODE = [
    "result = [0] * (m + n)",
    "for i in reversed(range(m)):",
    "    for j in reversed(range(n)):",
    "        low = (m-1-i) + (n-1-j)",
    "        result[low] += d1 * d2",
    "for k in range(m+n):        # settle carries",
    "    result[k], carry = (result[k]+carry) % 10, ...",
    "return trimmed big-endian string",
]


def add(**f):
    frames.append(f)


m, n = len(num1), len(num2)
SIZE = m + n
place_labels = [f"10^{k}" for k in range(SIZE)]  # cells are little-endian: units on left cell 0


def cells_from(result):
    # show places with units at index 0 (left). Keep them as strings.
    return [str(v) for v in result]


# ---- Act 0: the rule ----
add(act=0, cells=[str(0)] * SIZE, labels=place_labels, code="mul", line=0,
    intro="digit i of num1 times digit j of num2 always lands in place (i+j) from the right.",
    invariant="an m-digit by n-digit product has at most m+n places.",
    note=f"Multiply {num1} x {num2} on paper. Allocate {SIZE} places (units on the "
    "left cell). Each single-digit product drops into one place by its position.",
    pointers={}, marks={}, state=[["num1", num1], ["num2", num2], ["places", SIZE]])
add(act=0, cells=[str(0)] * SIZE, labels=place_labels, code="mul", line=3,
    note="Counting from the right: units*units -> place 0, tens*units -> place 1, and so "
    "on. That place-shift is exactly stacking numbers on paper.",
    marks={"0": "active"}, state=[["units*units", "place 0"], ["tens*units", "place 1"]])

# ---- Act 1: accumulate partial products ----
result = [0] * SIZE
partials = {}  # place -> list of "d1*d2=p" strings
add(act=1, cells=cells_from(result), labels=place_labels, code="mul", line=4,
    intro="every digit pair adds its product into one place; carries wait till the end.",
    invariant="result[place] holds the running (un-normalized) total for that place.",
    note="Accumulate: for each digit pair, add d1*d2 into place (i+j)-from-right. Places "
    "may exceed 9 for now — we fix carries after.",
    pointers={}, marks={}, sidebar={"title": "partial products", "rows": []},
    state=[["result", str(result)]])
for i in range(m - 1, -1, -1):
    d1 = int(num1[i])
    for j in range(n - 1, -1, -1):
        d2 = int(num2[j])
        low = (m - 1 - i) + (n - 1 - j)
        prod = d1 * d2
        result[low] += prod
        partials.setdefault(low, []).append(f"{d1}x{d2}={prod}")
        add(act=1, code="mul", line=4,
            note=f"{num1[i]}(place {m - 1 - i}) x {num2[j]}(place {n - 1 - j}) = {prod} -> "
                 f"add to place {low}; place {low} now {result[low]}.",
            pointers={"place": low}, marks={str(low): "active"},
            sidebar={"title": f"feeding place {low}", "rows": [[s, ""] for s in partials[low]]},
            cells=cells_from(result),
            state=[["d1*d2", prod], [f"place {low}", result[low]]])
add(act=1, code="mul", line=4,
    note=f"All 9 digit-pairs accumulated. Un-normalized places (units first): {result}.",
    cells=cells_from(result), marks={str(k): "dim" for k in range(SIZE)},
    sidebar={"title": "partial products", "rows": []},
    state=[["pre-carry", str(result)]])

# ---- Act 2: settle carries ----
add(act=2, cells=cells_from(result), labels=place_labels, code="mul", line=5,
    intro="each place keeps its ones digit; the rest carries into the next place left.",
    invariant="after place k, places 0..k are final single digits.",
    note="Walk the places from units up. Keep total%10 here, carry total//10 to the next.",
    pointers={"place": 0}, marks={"0": "active"},
    sidebar={"title": "carry", "rows": [["carry", "0"]]},
    state=[["carry", 0]])
carry = 0
for k in range(SIZE):
    total = result[k] + carry
    keep = total % 10
    newcarry = total // 10
    result[k] = keep
    add(act=2, code="mul", line=6,
        note=f"place {k}: {total} -> keep {keep}, carry {newcarry} left.",
        pointers={"place": k}, marks={str(k): "good",
                                      **({str(k + 1): "active"} if k + 1 < SIZE else {})},
        cells=cells_from(result),
        sidebar={"title": "carry", "rows": [["into place", k + 1], ["carry", newcarry]]},
        state=[["place", k], ["kept", keep], ["carry out", newcarry]])
    carry = newcarry

# ---- Act 3: read off + zero edge ----
digits = result[::-1]
start = 0
while start < len(digits) - 1 and digits[start] == 0:
    start += 1
answer = "".join(str(d) for d in digits[start:])
add(act=3, cells=[str(d) for d in digits], labels=[f"10^{k}" for k in range(SIZE - 1, -1, -1)],
    code="mul", line=7,
    intro="reverse to big-endian and drop the leading zero place.",
    invariant="the top place can be 0 when the product is shorter than m+n.",
    note=f"Reversed to normal order: {digits}. The top place is 0, so drop it -> {answer}.",
    pointers={}, marks={**{str(k): "dim" for k in range(start)},
                        **{str(k): "good" for k in range(start, SIZE)}},
    state=[["answer", answer]],
    banner=f"{num1} x {num2} = {answer}")
add(act=3, cells=["0"], labels=["10^0"], code="mul", line=0,
    note="Edge case: any factor is \"0\" -> the product is \"0\", returned before the loop.",
    marks={"0": "good"}, state=[["0 x 52", "0"]], banner='"0" x anything -> "0"')

trace = {
    "player": "linear",
    "title": "Multiply Strings - grade-school long multiplication, place by place",
    "acts": ["The place rule", "Accumulate partials", "Settle carries", "Read off + edge"],
    "code": {"mul": CODE},
    "legend": [["active", "place being written"], ["good", "final digit / answer"],
               ["dim", "settled / dropped zero"]],
    "cells": [str(0)] * SIZE, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
