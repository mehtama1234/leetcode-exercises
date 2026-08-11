"""Rich full-arc trace for Distinct Subsequences (grid renderer).
Arc: brute (use/skip branching, subproblems overlap) -> fill a (m+1)x(n+1)
count table -> answer + edge. The rolled 1-D solution in solution.py is the same
recurrence; here we show the full 2-D table so the dependencies are visible.
Writes trace.json.
"""
import json
import os

S, T = "rabbbit", "rabbit"
M, N = len(S), len(T)
frames = []

CODE = [
    "dp = [[0]*(n+1) for _ in range(m+1)]",
    "for i in range(m+1): dp[i][n] = 1   # empty t: one way",
    "for i in range(m-1, -1, -1):",
    "    for j in range(n-1, -1, -1):",
    "        dp[i][j] = dp[i+1][j]              # skip s[i]",
    "        if s[i] == t[j]: dp[i][j] += dp[i+1][j+1]  # use s[i]",
    "return dp[0][0]",
]

# dp[i][j] = ways t[j:] appears in s[i:]. Rows i=0..m, cols j=0..n.
# Row m = empty s suffix; col n = empty t suffix.
ROWLABELS = list(S) + ["·"]       # row i shows s[i]; last row = empty s
COLLABELS = list(T) + ["·"]       # col j shows t[j]; last col = empty t


def add(**f):
    frames.append(f)


def blank():
    return [[None] * (N + 1) for _ in range(M + 1)]


# ---- Act 0: brute ----
add(act=0, rows=blank(), rowLabels=ROWLABELS, colLabels=COLLABELS, code=None,
    intro="how the same (s-suffix, t-suffix) pair gets counted again and again.",
    invariant="count(i,j) = ways t[j:] appears as a subsequence of s[i:].",
    note="Brute force: at each s-character, either skip it, or (if it matches the "
    "current t-character) use it. Every distinct alignment is a leaf of that tree.",
    marks={"0,0": "active"}, state=[["find", "\"rabbit\" in \"rabbbit\""], ["choice", "skip / use"]])
add(act=0, note="The three b's mean many branches reach the same subproblem "
    "count(4,3) \"bbit vs bit\" — re-solved on every route. That repeat is the waste.",
    marks={"4,3": "bad", "0,0": "active"},
    state=[["recomputed", "count(4,3) …"], ["cost", "exponential"]])

# ---- Act 1: fill the table (bottom-right back to top-left) ----
dp = [[0] * (N + 1) for _ in range(M + 1)]
add(act=1, rows=blank(), code="tab", line=0,
    intro="filled from the empty suffixes back to (0,0); each cell reads down + down-right.",
    invariant="dp[i][j] = dp[i+1][j] (+ dp[i+1][j+1] when s[i]==t[j]).",
    note="Seed the last column: matching the EMPTY target t[n:] inside any s-suffix "
    "is one way — delete everything.",
    marks={}, state=[["seed", "empty t = 1 way"]])
for i in range(M + 1):
    dp[i][N] = 1
    add(act=1, code="tab", line=1, note=f"dp[{i}][{N}] = 1 (empty target matches one way).",
        set={f"{i},{N}": 1}, marks={f"{i},{N}": "good"}, state=[[f"dp[{i}][{N}]", 1]])
# fill interior bottom-up, right-to-left
for i in range(M - 1, -1, -1):
    for j in range(N - 1, -1, -1):
        skip = dp[i + 1][j]
        dp[i][j] = skip
        a, b = S[i], T[j]
        if a == b:
            use = dp[i + 1][j + 1]
            dp[i][j] += use
            note = (f"s[{i}]='{a}' == t[{j}]='{b}': dp[{i}][{j}] = skip {skip} + use {use} "
                    f"= {dp[i][j]}.")
            marks = {f"{i+1},{j}": "active", f"{i+1},{j+1}": "active", f"{i},{j}": "good"}
            state = [["skip(down)", skip], ["use(down-right)", use], [f"dp[{i}][{j}]", dp[i][j]]]
        else:
            note = (f"s[{i}]='{a}' != t[{j}]='{b}': can't use it, dp[{i}][{j}] = skip {skip} "
                    f"= {dp[i][j]}.")
            marks = {f"{i+1},{j}": "active", f"{i},{j}": "good"}
            state = [["skip(down)", skip], [f"dp[{i}][{j}]", dp[i][j]]]
        add(act=1, code="tab", line=5 if a == b else 4, note=note,
            set={f"{i},{j}": dp[i][j]}, marks=marks, state=state)

# ---- Act 2: answer + edge ----
add(act=2, code="tab", line=6,
    intro="the top-left cell counts every full alignment.",
    invariant="dp[0][0] summed all use/skip paths without recounting a subproblem.",
    note=f"dp[0][0] = {dp[0][0]} — the number of distinct ways \"{T}\" appears in \"{S}\".",
    marks={"0,0": "good"}, state=[["answer", dp[0][0]]],
    banner=f"\"{T}\" appears in \"{S}\" {dp[0][0]} distinct way(s)")

# edge: t longer than s -> 0
E_S, E_T = "abc", "abcd"
em, en = len(E_S), len(E_T)
edp = [[0] * (en + 1) for _ in range(em + 1)]
for i in range(em + 1):
    edp[i][en] = 1
for i in range(em - 1, -1, -1):
    for j in range(en - 1, -1, -1):
        edp[i][j] = edp[i + 1][j]
        if E_S[i] == E_T[j]:
            edp[i][j] += edp[i + 1][j + 1]
add(act=2, rows=edp, rowLabels=list(E_S) + ["·"], colLabels=list(E_T) + ["·"],
    code="tab", line=6,
    note="Edge case: the target is longer than the source. There is no way to fit "
    "\"abcd\" inside \"abc\", so dp[0][0] = 0.",
    marks={"0,0": "good"}, state=[["answer", edp[0][0]]],
    banner="Target longer than source → 0")

trace = {
    "player": "grid",
    "title": "Distinct Subsequences - count each (suffix, suffix) alignment once",
    "acts": ["Brute: use / skip", "Fill the table", "Answer + edge"],
    "code": {"tab": CODE},
    "legend": [["active", "cells this one adds"], ["good", "filled / answer"],
               ["bad", "recomputed (waste)"]],
    "rows": blank(), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
