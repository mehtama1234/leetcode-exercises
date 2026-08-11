"""Full-arc trace for Fibonacci Number (linear renderer, dp shown as one grid row).
Arc: naive recursion re-solves the same F(k) -> memo/table fills each once ->
rolling two-variable loop -> edge case. Mirrors solution.py. Writes trace.json.
"""
import json
import os

N = 6  # compute F(6) = 8
frames = []

NAIVE = [
    "def fib(n):",
    "    if n < 2: return n",
    "    return fib(n-1) + fib(n-2)",
]
FAST = [
    "prev, curr = 0, 1",
    "for _ in range(2, n+1):",
    "    prev, curr = curr, prev + curr",
    "return curr",
]


def add(**f):
    frames.append(f)


# dp[k] = F(k), verified: 0 1 1 2 3 5 8
dp = [0, 1]
for k in range(2, N + 1):
    dp.append(dp[k - 1] + dp[k - 2])
assert dp == [0, 1, 1, 2, 3, 5, 8]

labels = [f"F{k}" for k in range(N + 1)]


def blank():
    return [[None] * (N + 1)]


# ---- Act 0: naive recursion, same values recomputed ----
add(act=0, rows=blank(), rowLabels=["F"], colLabels=labels, code="naive", line=0,
    intro="how many times the SAME F(k) gets asked as the call tree branches.",
    invariant="F(n) = F(n-1) + F(n-2).",
    note=f"Naive: to get F({N}) we ask F({N-1}) and F({N-2}), each of which asks two "
    "more. The tree branches at every step.",
    marks={f"0,{N}": "active"}, state=[["want", f"F({N})"], ["cost", "exponential"]])
add(act=0, code="naive", line=2,
    note="But F(4) is asked while computing F(6) and again while computing F(5). "
    "F(3) is recomputed 3 times, F(2) 5 times. That overlap is the waste.",
    marks={"0,4": "bad", "0,3": "bad", "0,2": "bad", f"0,{N}": "active"},
    state=[["F(4) computed", "twice"], ["F(2) computed", "5x"]])

# ---- Act 1: the waste named ----
add(act=1,
    note="The call tree for F(n) has about phi^n nodes, but only n+1 distinct "
    "answers live inside it. Remembering each once collapses the tree to a line.",
    marks={f"0,{k}": "dim" for k in range(N + 1)},
    state=[["distinct answers", N + 1], ["naive calls", "~phi^n"]])

# ---- Act 2: fill each F(k) once (bottom-up table) ----
add(act=2, rows=blank(), rowLabels=["F"], colLabels=labels, code="fast", line=0,
    intro="each cell filled ONCE, left to right, from the two before it.",
    invariant="dp[k] holds F(k), final the moment it is written.",
    note="Seed the base cases: F(0) = 0 and F(1) = 1.",
    set={"0,0": 0, "0,1": 1}, marks={"0,0": "good", "0,1": "good"},
    state=[["F(0)", 0], ["F(1)", 1]])
for k in range(2, N + 1):
    add(act=2, code="fast", line=2,
        note=f"F({k}) = F({k-1}) + F({k-2}) = {dp[k-1]} + {dp[k-2]} = {dp[k]}.",
        set={f"0,{k}": dp[k]},
        marks={f"0,{k-1}": "active", f"0,{k-2}": "active", f"0,{k}": "good"},
        state=[["prev", dp[k - 2]], ["curr", dp[k - 1]], [f"F({k})", dp[k]]])

# ---- Act 3: answer + edge ----
add(act=2, code="fast", line=3,
    note=f"Only the last two values were ever needed at once, so the real loop keeps "
    f"just prev and curr — O(1) space. F({N}) = {dp[N]}.",
    marks={f"0,{N}": "good"}, state=[["answer", dp[N]]],
    banner=f"F({N}) = {dp[N]}  filled once, no branch re-walked")
add(act=3, rows=[[0]], rowLabels=["F"], colLabels=["F0"], code="fast", line=1,
    intro="the base cases return immediately, no loop body runs.",
    note="Edge case: n = 0. The guard n < 2 returns n straight away, so F(0) = 0.",
    marks={"0,0": "good"}, state=[["n", 0], ["answer", 0]],
    banner="n < 2 -> return n directly")

trace = {
    "player": "grid",
    "title": "Fibonacci - remember each F(k) once instead of re-branching",
    "acts": ["Naive: re-branch", "The waste", "Fill each once", "Edge case: n=0"],
    "code": {"naive": NAIVE, "fast": FAST},
    "legend": [["active", "the two we add"], ["good", "filled / answer"], ["bad", "recomputed (waste)"]],
    "rows": blank(), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
