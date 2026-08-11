"""Rich full-arc trace for Rotate Image (grid renderer).
Arc: brute (copy into a fresh grid, extra space wasted) -> transpose in place ->
reverse each row -> edge (2x2). Mirrors solution.py. Writes trace.json.
"""
import json
import os

frames = []

CODE_COPY = [
    "result = [[0]*n for _ in range(n)]",
    "for r in range(n):",
    "    for c in range(n):",
    "        result[c][n-1-r] = matrix[r][c]",
    "matrix[:] = result   # extra grid = the waste",
]
CODE_FAST = [
    "for r in range(n):",
    "    for c in range(r+1, n):",
    "        matrix[r][c], matrix[c][r] = matrix[c][r], matrix[r][c]",
    "for row in matrix:",
    "    row.reverse()",
]


def add(**f):
    frames.append(f)


def grid_of(m):
    return [row[:] for row in m]


def labels(n):
    return [str(i) for i in range(n)]


# ---- Act 0: brute — write each cell into a fresh grid ----
start = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
N = 3
add(act=0, rows=grid_of(start), rowLabels=labels(N), colLabels=labels(N),
    intro="where each cell lands under a 90-degree clockwise turn.",
    invariant="clockwise sends (r,c) to (c, n-1-r).",
    note="Brute force: allocate a second n x n grid and copy every cell to its "
    "rotated home. Watch (0,0), the top-left, travel to the top-right.",
    marks={"0,0": "active"}, state=[["extra grid", "n x n"], ["writes", 0]])

# show a few source->dest writes into a separate result grid (rendered by rebuilding)
writes = 0
mapping = [(0, 0), (0, 2), (2, 2), (2, 0)]  # corners: source -> (c, n-1-r)
for (r, c) in mapping:
    dr, dc = c, N - 1 - r
    writes += 1
    add(act=0, note=f"result[{dr}][{dc}] = matrix[{r}][{c}] = {start[r][c]} "
        f"(source (r,c) lands at (c, n-1-r)).",
        code="copy", line=3,
        marks={f"{r},{c}": "active", f"{dr},{dc}": "good"},
        state=[["from", f"({r},{c})"], ["to", f"({dr},{dc})"], ["writes", writes]])
add(act=0, note="It works, but the second grid is banned by the problem. That extra "
    "n x n storage is the waste. In place we look for swaps that stay inside the grid.",
    marks={"0,0": "bad", "0,2": "bad", "2,2": "bad", "2,0": "bad"},
    state=[["extra grid", "n x n"], ["cost", "O(n^2) space"]])

# ---- Act 1: transpose in place (swap across main diagonal) ----
m = grid_of(start)
add(act=1, rows=grid_of(m), rowLabels=labels(N), colLabels=labels(N),
    code="fast", line=0,
    intro="a clockwise turn = transpose, then reverse each row. First the transpose.",
    invariant="transpose swaps matrix[r][c] with matrix[c][r], only for c > r.",
    note="Transpose flips the grid over its main diagonal: rows become columns. Swap "
    "each pair once, taking only cells above the diagonal (c > r).",
    marks={"0,0": "dim", "1,1": "dim", "2,2": "dim"}, state=[["swaps", 0]])
swaps = 0
for r in range(N):
    for c in range(r + 1, N):
        a, b = m[r][c], m[c][r]
        m[r][c], m[c][r] = b, a
        swaps += 1
        add(act=1, code="fast", line=2,
            note=f"swap ({r},{c})={a} with ({c},{r})={b}.",
            set={f"{r},{c}": m[r][c], f"{c},{r}": m[c][r]},
            marks={f"{r},{c}": "active", f"{c},{r}": "active"},
            state=[["swap", f"({r},{c}) <-> ({c},{r})"], ["swaps", swaps]])
# after transpose m == [[1,4,7],[2,5,8],[3,6,9]]
add(act=1, code="fast", line=2,
    note="Transposed. Rows and columns have traded places, entirely in place.",
    marks={f"{r},{r}": "dim" for r in range(N)}, state=[["swaps", swaps]])

# ---- Act 2: reverse each row -> answer ----
add(act=2, rows=grid_of(m), rowLabels=labels(N), colLabels=labels(N),
    code="fast", line=3,
    intro="now reverse each row left-to-right to finish the clockwise turn.",
    invariant="reversing a row mirrors it; combined with the transpose that is the rotation.",
    note="Reverse each row in place. No scratch space needed.",
    marks={}, state=[["rows reversed", 0]])
done = 0
for r in range(N):
    before = m[r][:]
    m[r].reverse()
    done += 1
    sets = {f"{r},{c}": m[r][c] for c in range(N)}
    add(act=2, code="fast", line=4,
        note=f"reverse row {r}: {before} -> {m[r]}.",
        set=sets, marks={f"{r},{c}": "active" for c in range(N)},
        state=[["row", r], ["rows reversed", done]])
# m now == [[7,4,1],[8,5,2],[9,6,3]]
assert m == [[7, 4, 1], [8, 5, 2], [9, 6, 3]]
add(act=2, code="fast", line=4,
    note="Done. The grid is rotated 90 degrees clockwise using only in-grid swaps "
    "and reverses.",
    marks={f"{r},{c}": "good" for r in range(N) for c in range(N)},
    state=[["extra space", "O(1)"]],
    banner="Rotated 90 clockwise in place")

# ---- Act 3: edge — 2x2 grid ----
e = [[1, 2], [3, 4]]
NE = 2
add(act=3, rows=grid_of(e), rowLabels=labels(NE), colLabels=labels(NE),
    code="fast", line=0,
    intro="the smallest non-trivial grid: one transpose swap, then two reverses.",
    invariant="same two passes, any n.",
    note="Edge case: 2x2. Only pair above the diagonal is (0,1) <-> (1,0).",
    marks={"0,1": "active", "1,0": "active"}, state=[["swaps", 0]])
e[0][1], e[1][0] = e[1][0], e[0][1]  # -> [[1,3],[2,4]]
add(act=3, code="fast", line=2, note="swap (0,1)=2 with (1,0)=3.",
    set={"0,1": e[0][1], "1,0": e[1][0]},
    marks={"0,1": "active", "1,0": "active"}, state=[["swaps", 1]])
e[0].reverse()  # [3,1]
add(act=3, code="fast", line=4, note="reverse row 0: [1, 3] -> [3, 1].",
    set={"0,0": e[0][0], "0,1": e[0][1]},
    marks={"0,0": "active", "0,1": "active"}, state=[["rows reversed", 1]])
e[1].reverse()  # [4,2]
add(act=3, code="fast", line=4, note="reverse row 1: [2, 4] -> [4, 2].",
    set={"1,0": e[1][0], "1,1": e[1][1]},
    marks={"1,0": "active", "1,1": "active"}, state=[["rows reversed", 2]])
assert e == [[3, 1], [4, 2]]
add(act=3, code="fast", line=4, note="2x2 rotated: [[1,2],[3,4]] -> [[3,1],[4,2]].",
    marks={f"{r},{c}": "good" for r in range(NE) for c in range(NE)},
    banner="2x2 rotated in place")

trace = {
    "player": "grid",
    "title": "Rotate Image - transpose then reverse rows, no extra grid",
    "acts": ["Brute: copy to a new grid", "Transpose in place", "Reverse each row",
             "Edge: 2x2"],
    "code": {"copy": CODE_COPY, "fast": CODE_FAST},
    "legend": [["active", "cells being swapped / read"], ["good", "placed / answer"],
               ["bad", "the extra grid (waste)"], ["dim", "on the diagonal / settled"]],
    "rows": grid_of(start), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
