"""Rich full-arc trace for Range Sum Query 2D - Immutable, mirroring NumMatrix in
solution.py. Uses the grid renderer. Shows the brute force re-adding a rectangle
per query, builds the (rows+1)x(cols+1) prefix table once by inclusion-exclusion,
then answers a rectangle with the four-corner formula. Writes trace.json.
"""
import json
import os

matrix = [
    [3, 0, 1, 4],
    [5, 6, 3, 2],
    [1, 2, 0, 1],
]
frames = []

BRUTE = [
    "def sumRegion(r1, c1, r2, c2):",
    "    total = 0",
    "    for r in range(r1, r2+1):",
    "        for c in range(c1, c2+1):",
    "            total += matrix[r][c]",
    "    return total",
]
BUILD = [
    "P = (rows+1) x (cols+1) of 0",
    "P[r+1][c+1] = matrix[r][c]",
    "           + P[r][c+1] + P[r+1][c]",
    "           - P[r][c]",
]
FAST = [
    "def sumRegion(r1, c1, r2, c2):",
    "    return (P[r2+1][c2+1]",
    "          - P[r1][c2+1]",
    "          - P[r2+1][c1]",
    "          + P[r1][c1])",
]


def add(**f):
    frames.append(f)


R, C = len(matrix), len(matrix[0])
rlab = [str(r) for r in range(R)]
clab = [str(c) for c in range(C)]

# reference brute for verification
def brute(r1, c1, r2, c2):
    return sum(matrix[r][c] for r in range(r1, r2 + 1) for c in range(c1, c2 + 1))

# query used throughout: rows 1..2, cols 1..3 -> 6+3+2 + 2+0+1 = 14
q = (1, 1, 2, 3)
Q_ANS = brute(*q)  # 14

# ---- Act 0: brute force — re-add the rectangle ----
work = 0
total = 0
add(act=0, rows=[row[:] for row in matrix], rowLabels=rlab, colLabels=clab, code="brute",
    line=0,
    intro="every query adds every cell in its rectangle — overlapping queries re-add the same cells.",
    invariant="sumRegion literally adds each cell inside the rectangle.",
    note=f"Brute force: to sum the rectangle rows {q[0]}..{q[2]}, cols {q[1]}..{q[3]}, add "
         "every cell inside.",
    marks={f"{q[0]},{q[1]}": "active"},
    state=[["rectangle", f"({q[0]},{q[1]})..({q[2]},{q[3]})"], ["total", 0], ["adds", 0]])
for r in range(q[0], q[2] + 1):
    for c in range(q[1], q[3] + 1):
        total += matrix[r][c]
        work += 1
        add(act=0, code="brute", line=4,
            note=f"add matrix[{r}][{c}] = {matrix[r][c]} -> total {total}.",
            marks={**{f"{rr},{cc}": "good"
                      for rr in range(q[0], r + 1) for cc in range(q[1], q[3] + 1)
                      if (rr < r or cc <= c)},
                   f"{r},{c}": "active"},
            state=[["cell", f"({r},{c})"], ["total", total], ["adds", work]])
add(act=0, code="brute", line=5,
    note=f"This one rectangle took {work} adds. Ask thousands of overlapping rectangles "
         "and the same cells get re-added endlessly — that is the waste.",
    marks={f"{r},{c}": "dim" for r in range(R) for c in range(C)},
    state=[["sum", total], ["adds", work]])

# ---- Act 1: the waste ----
add(act=1,
    intro="a rectangle sum is four corner lookups on a table of top-left block sums — build that table once.",
    note="Let P[r][c] = sum of the whole top-left block from (0,0) to (r-1,c-1). Any "
         "rectangle is one big block minus the strip above minus the strip left, plus "
         "the double-removed corner.",
    marks={f"{r},{c}": "dim" for r in range(R) for c in range(C)},
    state=[["insight", "big - top - left + corner"], ["build cost", "one sweep"]])
add(act=1,
    note="After the table is built, every rectangle is exactly four lookups and three "
         "+/- operations — no matter how wide.",
    marks={f"{r},{c}": "dim" for r in range(R) for c in range(C)},
    state=[["per query", "4 lookups"], ["was", "O(area)"]])

# ---- Act 2: build the (R+1)x(C+1) prefix table ----
P = [[0] * (C + 1) for _ in range(R + 1)]
Plab_r = [str(r) for r in range(R + 1)]
Plab_c = [str(c) for c in range(C + 1)]


def pblank():
    # show current P with zero border, None-free (all ints so far as filled)
    return [[P[r][c] for c in range(C + 1)] for r in range(R + 1)]


add(act=2, rows=pblank(), rowLabels=Plab_r, colLabels=Plab_c, code="build", line=0,
    intro="P has a zero top row and left column so the formula needs no edge cases. Each cell filled once.",
    invariant="P[r+1][c+1] = sum of every matrix cell in the top-left block up to (r,c).",
    note="Build a (rows+1)x(cols+1) table with a zero border. Row 0 and column 0 stay 0.",
    marks={**{f"0,{c}": "good" for c in range(C + 1)},
           **{f"{r},0": "good" for r in range(R + 1)}},
    state=[["table", f"{R+1} x {C+1}"], ["border", "all 0"]])
for r in range(R):
    for c in range(C):
        P[r + 1][c + 1] = (matrix[r][c] + P[r][c + 1] + P[r + 1][c] - P[r][c])
        add(act=2, rows=pblank(), rowLabels=Plab_r, colLabels=Plab_c, code="build", line=1,
            note=f"P[{r+1}][{c+1}] = m[{r}][{c}] {matrix[r][c]} + above {P[r][c+1]} + left "
                 f"{P[r+1][c]} - corner {P[r][c]} = {P[r+1][c+1]}.",
            set={f"{r+1},{c+1}": P[r + 1][c + 1]},
            marks={f"{r},{c+1}": "active", f"{r+1},{c}": "active", f"{r},{c}": "bad",
                   f"{r+1},{c+1}": "good"},
            state=[["m[r][c]", matrix[r][c]], ["above", P[r][c + 1]], ["left", P[r + 1][c]],
                   ["corner", P[r][c]], [f"P[{r+1}][{c+1}]", P[r + 1][c + 1]]])
add(act=2, rows=pblank(), rowLabels=Plab_r, colLabels=Plab_c, code="build", line=1,
    note=f"Table built. P[{R}][{C}] = {P[R][C]} is the sum of the entire matrix — filled "
         "once, cell by cell.",
    marks={f"{R},{C}": "good"},
    state=[["whole-matrix sum", P[R][C]]])

# ---- Act 3: answer a rectangle with four corners ----
r1, c1, r2, c2 = q
big = P[r2 + 1][c2 + 1]
top = P[r1][c2 + 1]
lft = P[r2 + 1][c1]
cor = P[r1][c1]
ans = big - top - lft + cor
assert ans == Q_ANS, (ans, Q_ANS)
add(act=3, rows=pblank(), rowLabels=Plab_r, colLabels=Plab_c, code="fast", line=0,
    intro="four corners of the prefix table give the rectangle sum: big - top - left + corner.",
    invariant="inclusion-exclusion: the corner block, removed twice, is added back once.",
    note=f"Rectangle rows {r1}..{r2}, cols {c1}..{c2}. Read four corners of P (shifted "
         "by +1 for the border).",
    marks={f"{r2+1},{c2+1}": "good", f"{r1},{c2+1}": "bad", f"{r2+1},{c1}": "bad",
           f"{r1},{c1}": "active"},
    state=[["big P[%d][%d]" % (r2 + 1, c2 + 1), big], ["top P[%d][%d]" % (r1, c2 + 1), top],
           ["left P[%d][%d]" % (r2 + 1, c1), lft], ["corner P[%d][%d]" % (r1, c1), cor]])
add(act=3, rows=pblank(), rowLabels=Plab_r, colLabels=Plab_c, code="fast", line=4,
    note=f"sum = big {big} - top {top} - left {lft} + corner {cor} = {ans}. Matches the "
         f"brute total ({Q_ANS}) — in four lookups, not {work} adds.",
    marks={f"{r2+1},{c2+1}": "good", f"{r1},{c2+1}": "bad", f"{r2+1},{c1}": "bad",
           f"{r1},{c1}": "good"},
    state=[["sum", ans], ["vs brute adds", work]],
    banner=f"Rectangle sum = {big} - {top} - {lft} + {cor} = {ans}   — four corners")
# tiny edge: single cell (0,0)..(0,0)
sc = P[1][1] - P[0][1] - P[1][0] + P[0][0]
assert sc == matrix[0][0]
add(act=3, rows=pblank(), rowLabels=Plab_r, colLabels=Plab_c, code="fast", line=4,
    note=f"Edge: a single cell (0,0). big {P[1][1]} - top {P[0][1]} - left {P[1][0]} + "
         f"corner {P[0][0]} = {sc} = matrix[0][0]. The zero border makes it just work.",
    marks={"1,1": "good", "0,1": "bad", "1,0": "bad", "0,0": "active"},
    state=[["single cell", sc]],
    banner=f"Single cell (0,0) -> {sc}")

trace = {
    "player": "grid",
    "title": "Range Sum Query 2D — a rectangle in four corner lookups",
    "acts": ["Brute force: re-add the rectangle", "The waste",
             "Build the 2D prefix table", "Answer: four corners + edge"],
    "code": {"brute": BRUTE, "build": BUILD, "fast": FAST},
    "legend": [["active", "cell / corner in play"], ["good", "kept (added)"],
               ["bad", "subtracted off"], ["dim", "filed away"]],
    "rows": [row[:] for row in matrix], "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
