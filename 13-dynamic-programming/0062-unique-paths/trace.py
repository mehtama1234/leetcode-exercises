"""Rich full-arc trace for Unique Paths (grid renderer reference).
Arc: brute (every path, overlapping work) -> fill the table -> answer + edge.
Mirrors the tabulation in solution.py. Writes trace.json.
"""
import json
import os

M, N = 3, 3
frames = []

CODE = [
    "dp = [[1] * n for _ in range(m)]",
    "for r in range(1, m):",
    "    for c in range(1, n):",
    "        dp[r][c] = dp[r-1][c] + dp[r][c-1]",
    "return dp[m-1][n-1]",
]


def add(**f):
    frames.append(f)


def blank():
    return [[None] * N for _ in range(M)]


# ---- Act 0: brute force — every path, same cells recomputed ----
add(act=0, rows=blank(), rowLabels=[str(r) for r in range(M)],
    colLabels=[str(c) for c in range(N)], code=None,
    intro="how many times the SAME cell gets asked 'how many paths from here?'",
    invariant="paths(cell) = paths(right) + paths(down).",
    note="Brute force: from the start, branch right or down until the corner. Count "
    "the paths that reach the end.",
    marks={"0,0": "active"}, state=[["start", "(0,0)"], ["moves", "right / down"]])
add(act=0, note="But paths through (1,1) get recounted by many different routes — the "
    "same subproblem, solved again and again. That overlap is the waste.",
    marks={"1,1": "bad", "0,0": "active", "2,2": "active"},
    state=[["recomputed", "(1,1) …"], ["cost", "exponential"]])

# ---- Act 1: fill the table ----
dp = [[1] * N for _ in range(M)]
add(act=1, rows=blank(), code="tab", line=0,
    intro="each cell is filled ONCE, from the two neighbors it depends on.",
    invariant="dp[r][c] = ways to reach that cell, computed once.",
    note="Seed the first row and column with 1: there is exactly one straight-line "
    "way to reach any edge cell.",
    marks={}, state=[["fill", "edges = 1"]])
# show seeding of row 0 and col 0
for c in range(N):
    add(act=1, code="tab", line=0, note=f"dp[0][{c}] = 1 (only rightward).",
        set={f"0,{c}": 1}, marks={f"0,{c}": "good"}, state=[["dp[0][%d]" % c, 1]])
for r in range(1, M):
    add(act=1, code="tab", line=0, note=f"dp[{r}][0] = 1 (only downward).",
        set={f"{r},0": 1}, marks={f"{r},0": "good"}, state=[["dp[%d][0]" % r, 1]])
# fill interior
for r in range(1, M):
    for c in range(1, N):
        up = dp[r - 1][c]
        left = dp[r][c - 1]
        dp[r][c] = up + left
        add(act=1, code="tab", line=3,
            note=f"dp[{r}][{c}] = up {up} + left {left} = {dp[r][c]}.",
            set={f"{r},{c}": dp[r][c]},
            marks={f"{r-1},{c}": "active", f"{r},{c-1}": "active", f"{r},{c}": "good"},
            state=[["up", up], ["left", left], [f"dp[{r}][{c}]", dp[r][c]]])

# ---- Act 2: answer + edge ----
add(act=2, code="tab", line=4,
    intro="the bottom-right cell is the whole answer.",
    invariant="the corner already combined every path into one number.",
    note=f"The corner dp[{M-1}][{N-1}] = {dp[M-1][N-1]} is the answer — filled once, no path re-walked.",
    marks={f"{M-1},{N-1}": "good"}, state=[["answer", dp[M - 1][N - 1]]],
    banner=f"Unique paths on a {M}x{N} grid = {dp[M-1][N-1]}")
add(act=2, rows=[[1, 1, 1, 1]], rowLabels=["0"], colLabels=[str(c) for c in range(4)],
    code="tab", line=4,
    note="Edge case: a single-row grid. There is only one path — keep going right — "
    "so every cell is 1 and the answer is 1.",
    marks={"0,3": "good"}, state=[["answer", 1]], banner="Single row -> 1 path")

trace = {
    "player": "grid",
    "title": "Unique Paths - fill each cell once instead of re-walking every path",
    "acts": ["Brute: every path", "Fill the table", "Answer + edge"],
    "code": {"tab": CODE},
    "legend": [["active", "the two cells we add"], ["good", "filled / answer"], ["bad", "recomputed (waste)"]],
    "rows": blank(), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
