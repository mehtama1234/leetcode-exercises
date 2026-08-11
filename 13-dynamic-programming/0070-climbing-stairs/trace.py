"""Full-arc trace for Climbing Stairs (grid renderer, dp shown as one row).
Arc: naive recursion re-solves the same ways(k) -> fill each once -> rolling
loop -> edge case. Mirrors solution.py. Writes trace.json.
"""
import json
import os

N = 6  # ways(6) = 13
frames = []

NAIVE = [
    "def climb(n):",
    "    if n <= 2: return n",
    "    return climb(n-1) + climb(n-2)",
]
FAST = [
    "prev, curr = 1, 2",
    "for _ in range(3, n+1):",
    "    prev, curr = curr, prev + curr",
    "return curr",
]


def add(**f):
    frames.append(f)


# dp[k] = ways(k). Base: ways(1)=1, ways(2)=2. Verified 1 2 3 5 8 13
dp = [0, 1, 2]
for k in range(3, N + 1):
    dp.append(dp[k - 1] + dp[k - 2])
assert dp[1:] == [1, 2, 3, 5, 8, 13]

labels = [str(k) for k in range(1, N + 1)]  # steps 1..N


def blank():
    return [[None] * N]


# ---- Act 0: naive recursion, same subproblem re-solved ----
add(act=0, rows=blank(), rowLabels=["ways"], colLabels=labels, code="naive", line=0,
    intro="how often the SAME ways(k) is recomputed as the branches split.",
    invariant="ways(n) = ways(n-1) + ways(n-2): last move was a 1-step or a 2-step.",
    note=f"Naive: to reach step {N} the last move came from step {N-1} (a 1-step) or "
    f"step {N-2} (a 2-step). Each of those branches again.",
    marks={f"0,{N-1}": "active"}, state=[["want", f"ways({N})"], ["cost", "exponential"]])
add(act=0, code="naive", line=2,
    note="But ways(3) is asked while solving ways(5) and again while solving ways(4). "
    "The same subproblem is re-solved along many branches. That overlap is the waste.",
    marks={"0,2": "bad", "0,1": "bad", "0,0": "bad", f"0,{N-1}": "active"},
    state=[["ways(3)", "recomputed"], ["cost", "exponential"]])

# ---- Act 1: waste named ----
add(act=1,
    note=f"There are only {N} distinct subproblems, ways(1)..ways({N}). Cache each "
    "once and the branching tree collapses into a straight line.",
    marks={f"0,{c}": "dim" for c in range(N)},
    state=[["distinct", N], ["naive calls", "exponential"]])

# ---- Act 2: fill each step once ----
add(act=2, rows=blank(), rowLabels=["ways"], colLabels=labels, code="fast", line=0,
    intro="each step filled ONCE from the two below it.",
    invariant="dp[k] = distinct ways to reach step k, final when written.",
    note="Base cases: 1 way to reach step 1, and 2 ways to reach step 2 (1+1 or 2).",
    set={"0,0": 1, "0,1": 2}, marks={"0,0": "good", "0,1": "good"},
    state=[["ways(1)", 1], ["ways(2)", 2]])
for k in range(3, N + 1):
    c = k - 1
    add(act=2, code="fast", line=2,
        note=f"ways({k}) = ways({k-1}) + ways({k-2}) = {dp[k-1]} + {dp[k-2]} = {dp[k]}.",
        set={f"0,{c}": dp[k]},
        marks={f"0,{c-1}": "active", f"0,{c-2}": "active", f"0,{c}": "good"},
        state=[["prev", dp[k - 2]], ["curr", dp[k - 1]], [f"ways({k})", dp[k]]])

# ---- Act 3: answer + edge ----
add(act=2, code="fast", line=3,
    note=f"Only the last two counts are ever needed at once, so the loop keeps just "
    f"prev and curr. ways({N}) = {dp[N]}.",
    marks={f"0,{N-1}": "good"}, state=[["answer", dp[N]]],
    banner=f"ways({N}) = {dp[N]}  each step counted once")
add(act=3, rows=[[2]], rowLabels=["ways"], colLabels=["2"], code="fast", line=0,
    intro="n <= 2 is a base case that returns immediately.",
    note="Edge case: n = 2. Two ways to the top (1+1 or a single 2), returned "
    "directly with no loop.",
    marks={"0,0": "good"}, state=[["n", 2], ["answer", 2]],
    banner="n <= 2 -> return n")

trace = {
    "player": "grid",
    "title": "Climbing Stairs - count each step once instead of re-branching",
    "acts": ["Naive: re-branch", "The waste", "Fill each once", "Edge case: n=2"],
    "code": {"naive": NAIVE, "fast": FAST},
    "legend": [["active", "the two we add"], ["good", "filled / answer"], ["bad", "recomputed (waste)"]],
    "rows": blank(), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
