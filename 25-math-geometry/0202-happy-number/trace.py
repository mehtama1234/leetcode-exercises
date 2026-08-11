"""Rich full-arc trace for Happy Number (linear renderer).
The step is f(n) = sum of squares of digits; the sequence either reaches 1 (happy)
or loops forever. Arc: the rule (compute f(n) digit by digit) -> the seen-set walk
for a happy number -> the seen-set catching a repeat for an unhappy number -> Floyd's
two-pointer version that needs no set. Cells are the sequence of numbers produced;
the sidebar holds the running square-digit-sum breakdown or the seen set.
Mirrors _square_digit_sum / is_happy_set / is_happy in solution.py. Writes trace.json.
"""
import json
import os

frames = []

CODE = [
    "def f(n):                      # sum of squared digits",
    "    return sum(d*d for d in digits(n))",
    "seen = set()",
    "while n != 1 and n not in seen:",
    "    seen.add(n); n = f(n)",
    "return n == 1",
]
FLOYD = [
    "slow = n",
    "fast = f(n)",
    "while fast != 1 and slow != fast:",
    "    slow = f(slow)             # one step",
    "    fast = f(f(fast))          # two steps",
    "return fast == 1",
]


def add(**f):
    frames.append(f)


def sds(n):
    t = 0
    while n > 0:
        n, d = divmod(n, 10)
        t += d * d
    return t


def breakdown(n):
    parts = [f"{d}^2" for d in str(n)]
    return f"{'+'.join(parts)} = {sds(n)}"


def seq_of(start, limit=8):
    s = [start]
    n = start
    for _ in range(limit):
        n = sds(n)
        s.append(n)
        if n == 1:
            break
    return s


# ---- Act 0: the rule ----
add(act=0, cells=["19"], labels=["n"], code="hap", line=0,
    intro="the step replaces n by the sum of the squares of its digits.",
    invariant="the sequence either hits 1 or repeats a value — it can't run forever new.",
    note="Happy test: replace n by the sum of its digits squared, repeat. Reach 1 = happy; "
    "loop without 1 = not.",
    pointers={}, marks={}, sidebar={"title": "step", "rows": [["1^2 + 9^2", "1 + 81 = 82"]]},
    state=[["n", 19], ["f(19)", 82]])

# ---- Act 1: seen-set on a happy number 19 ----
seq = seq_of(19)  # [19, 82, 68, 100, 1]
add(act=1, cells=[str(v) for v in seq], labels=list(range(len(seq))), code="hap", line=3,
    intro="each new number is remembered; we stop the moment we see 1 or a repeat.",
    invariant="seen holds every earlier number in the chain.",
    note=f"Run 19 with a seen-set. The chain: {' -> '.join(map(str, seq))}.",
    pointers={"n": 0}, marks={"0": "active"},
    sidebar={"title": "seen", "rows": []}, state=[["n", 19]])
seen = []
for i in range(len(seq) - 1):
    n = seq[i]
    nxt = seq[i + 1]
    seen.append(n)
    add(act=1, code="hap", line=4,
        note=f"f({n}) = {breakdown(n)} -> {nxt}." + ("  Reached 1!" if nxt == 1 else ""),
        pointers={"n": i + 1},
        marks={**{str(k): "dim" for k in range(i + 1)}, str(i + 1): "good" if nxt == 1 else "active"},
        sidebar={"title": "seen", "rows": [[str(v), "seen"] for v in seen]},
        state=[["n", n], ["f(n)", nxt], ["seen size", len(seen)]])
add(act=1, code="hap", line=5, note="Reached 1 -> 19 is happy.",
    marks={str(len(seq) - 1): "good"},
    sidebar={"title": "seen", "rows": [[str(v), "seen"] for v in seen]},
    state=[["happy", True]], banner="19 is happy (19 -> 82 -> 68 -> 100 -> 1)")

# ---- Act 2: seen-set catches a loop for 2 ----
seq2 = seq_of(2, limit=9)  # runs into the 4->16->37->58->89->145->42->20->4 loop
# find first repeat index
seen2 = []
repeat_at = None
chain = [2]
n = 2
while n not in seen2 and n != 1:
    seen2.append(n)
    n = sds(n)
    chain.append(n)
    if n in seen2:
        repeat_at = n
        break
add(act=2, cells=[str(v) for v in chain], labels=list(range(len(chain))), code="hap", line=3,
    intro="an unhappy number falls into a fixed loop; the set spots the first repeat.",
    invariant="if a value reappears, we are cycling and will never reach 1.",
    note=f"Run 2. Chain: {' -> '.join(map(str, chain))} — the last value repeats an "
    "earlier one, so it loops.",
    pointers={"n": 0}, marks={"0": "active"},
    sidebar={"title": "seen", "rows": []}, state=[["n", 2]])
acc = []
for i in range(len(chain) - 1):
    n = chain[i]
    nxt = chain[i + 1]
    is_repeat = nxt in acc
    acc.append(n)
    add(act=2, code="hap", line=4,
        note=f"f({n}) = {breakdown(n)} -> {nxt}."
             + (f"  {nxt} was already seen -> cycle!" if is_repeat else ""),
        pointers={"n": i + 1},
        marks={**{str(k): "dim" for k in range(i + 1)},
               str(i + 1): "bad" if is_repeat else "active"},
        sidebar={"title": "seen", "rows": [[str(v), "seen"] for v in acc]},
        state=[["n", n], ["f(n)", nxt], ["repeat?", is_repeat]])
add(act=2, code="hap", line=5, note=f"{repeat_at} repeated -> 2 is NOT happy.",
    marks={str(len(chain) - 1): "bad"},
    state=[["happy", False]], banner="2 is not happy (falls into a loop)")

# ---- Act 3: Floyd's two pointers, no set ----
add(act=3, cells=[str(v) for v in chain], labels=list(range(len(chain))), code="floyd", line=0,
    intro="drop the set: run a slow (1 step) and fast (2 steps) pointer; a cycle makes them meet.",
    invariant="in a cycle the fast pointer laps the slow one; on a happy chain fast reaches 1 first.",
    note="Floyd on 2: slow takes one step, fast takes two. If they meet, it's a loop; if "
    "fast hits 1, it's happy. No memory needed.",
    pointers={}, marks={},
    sidebar={"title": "pointers", "rows": [["slow", "2"], ["fast", str(sds(2))]]},
    state=[["slow", 2], ["fast", sds(2)]])
slow = 2
fast = sds(2)
steps = 0
while fast != 1 and slow != fast:
    slow = sds(slow)
    fast = sds(sds(fast))
    steps += 1
    met = slow == fast
    add(act=3, code="floyd", line=4,
        note=f"step {steps}: slow -> {slow}, fast -> {fast}."
             + ("  slow == fast: cycle found." if met else ""),
        pointers={}, marks={},
        sidebar={"title": "pointers", "rows": [["slow", str(slow)], ["fast", str(fast)]]},
        state=[["slow", slow], ["fast", fast], ["meet?", met]])
add(act=3, code="floyd", line=5,
    note=f"slow and fast met at {slow} without reaching 1 -> not happy. Same answer as the "
    "set, but O(1) memory.",
    marks={}, sidebar={"title": "pointers", "rows": [["slow", str(slow)], ["fast", str(fast)]]},
    state=[["happy", False]], banner="Floyd: they meet -> 2 is not happy (no set needed)")

trace = {
    "player": "linear",
    "title": "Happy Number - iterate digit-square-sums; detect the loop",
    "acts": ["The rule", "Seen-set: 19 is happy", "Seen-set: 2 loops", "Floyd's two pointers"],
    "code": {"hap": CODE, "floyd": FLOYD},
    "legend": [["active", "current number"], ["good", "reached 1"],
               ["bad", "repeat -> cycle"], ["dim", "already seen"]],
    "cells": ["19"], "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
