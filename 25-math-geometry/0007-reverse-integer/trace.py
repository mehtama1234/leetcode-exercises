"""Rich full-arc trace for Reverse Integer (linear renderer).
Peel digits off the end of x and push them onto result, with an overflow check
BEFORE each multiply. Arc: the rule (pop with divmod, push onto result) -> run a
clean case -> the overflow edge where the reversed value would pass INT_MAX and we
bail with 0. Cells are the digits of x being consumed; the sidebar tracks result
and the 32-bit limit.
Mirrors reverse in solution.py. Writes trace.json.
"""
import json
import os

INT_MAX = 2**31 - 1  # 2147483647
frames = []

CODE = [
    "sign, x = sign_of(x), abs(x)",
    "result = 0",
    "while x != 0:",
    "    x, digit = divmod(x, 10)   # peel last digit",
    "    if result would exceed limit: return 0",
    "    result = result * 10 + digit",
    "return sign * result",
]


def add(**f):
    frames.append(f)


def digit_cells(x):
    return [c for c in str(abs(x))]


# ---- Act 0: the rule ----
X = 123
add(act=0, cells=digit_cells(X), labels=list(range(len(str(X)))), code="rev", line=0,
    intro="pull the last digit off x, push it onto result — the number turns around.",
    invariant="result holds the digits seen so far, already reversed.",
    note=f"Reverse {X}: repeatedly peel the last digit with divmod by 10 and push it onto "
    "result as result*10 + digit.",
    pointers={}, marks={},
    sidebar={"title": "state", "rows": [["result", "0"], ["INT_MAX", str(INT_MAX)]]},
    state=[["x", X], ["result", 0]])

# ---- Act 1: run a clean case ----
x = X
result = 0
sign = 1
add(act=1, cells=digit_cells(X), labels=list(range(len(str(X)))), code="rev", line=2,
    intro="each step consumes one digit from the right and grows result on the left.",
    invariant="result * 10 + digit stays within the 32-bit range here.",
    note="Run it. Watch result build 3 -> 32 -> 321 as digits peel off x.",
    pointers={}, marks={}, sidebar={"title": "state", "rows": [["result", "0"]]},
    state=[["x", x], ["result", 0]])
step = 0
consumed = len(str(X))
while x != 0:
    x, digit = divmod(x, 10)
    result = result * 10 + digit
    step += 1
    add(act=1, code="rev", line=5,
        note=f"peel digit {digit}: result = {result // 10 if step > 1 else 0}*10 + {digit} "
             f"= {result}. x is now {x}.",
        pointers={"d": consumed - step},
        marks={str(consumed - step): "good",
               **{str(k): "dim" for k in range(consumed - step)}},
        cells=digit_cells(X),
        sidebar={"title": "state", "rows": [["result", str(result)], ["x left", str(x)]]},
        state=[["digit", digit], ["result", result], ["x", x]])
add(act=1, code="rev", line=6, note=f"x hit 0. Reversed {X} = {result}.",
    marks={str(k): "good" for k in range(consumed)},
    sidebar={"title": "state", "rows": [["result", str(result)]]},
    state=[["answer", result]], banner=f"reverse({X}) = {result}")

# ---- Act 2: overflow edge ----
XO = 1534236469  # reversed 9646324351 > INT_MAX -> 0
add(act=2, cells=digit_cells(XO), labels=list(range(len(str(XO)))), code="rev", line=0,
    intro="the reversed value can pass INT_MAX even when x fits — we check BEFORE multiplying.",
    invariant="if result > INT_MAX//10, or ties it with a digit > 7, the next step overflows.",
    note=f"Edge case: {XO}. Its reversal 9646324351 is larger than INT_MAX "
    f"({INT_MAX}). A fixed-width machine would overflow, so we must catch it.",
    pointers={}, marks={},
    sidebar={"title": "guard", "rows": [["INT_MAX//10", str(INT_MAX // 10)], ["result", "0"]]},
    state=[["x", XO], ["result", 0]])
x = XO
result = 0
consumed = len(str(XO))
step = 0
limit = INT_MAX
while x != 0:
    x, digit = divmod(x, 10)
    over = result > limit // 10 or (result == limit // 10 and digit > limit % 10)
    step += 1
    if over:
        add(act=2, code="rev", line=4,
            note=f"About to do {result}*10 + {digit}, but result {result} already exceeds "
                 f"INT_MAX//10 = {limit // 10}. That would overflow -> return 0.",
            pointers={"d": consumed - step}, marks={str(consumed - step): "bad"},
            sidebar={"title": "guard", "rows": [["result", str(result)], ["limit//10", str(limit // 10)], ["digit", str(digit)]]},
            state=[["result", result], ["overflow", "yes"], ["answer", 0]],
            banner=f"reverse({XO}) overflows 32-bit -> 0")
        break
    result = result * 10 + digit
    add(act=2, code="rev", line=5,
        note=f"peel {digit}: result = {result}. Still within range.",
        pointers={"d": consumed - step},
        marks={str(consumed - step): "good", **{str(k): "dim" for k in range(consumed - step)}},
        sidebar={"title": "guard", "rows": [["result", str(result)], ["INT_MAX//10", str(limit // 10)]]},
        state=[["digit", digit], ["result", result]])

trace = {
    "player": "linear",
    "title": "Reverse Integer - peel digits, push onto result, guard the 32-bit limit",
    "acts": ["The rule", "Run a clean case", "Edge: overflow -> 0"],
    "code": {"rev": CODE},
    "legend": [["good", "digit consumed into result"], ["bad", "would overflow -> 0"],
               ["dim", "already peeled"]],
    "cells": digit_cells(X), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
