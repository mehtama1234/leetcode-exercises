"""Rich full-arc trace for Longest Increasing Path in a Matrix (grid renderer).
Arc: brute (DFS from every cell, downstream recomputed) -> memoized DP on the DAG
of 'points to a larger neighbour', filling best(r,c) in increasing-value order so
each cell's larger neighbours are already solved -> answer + edge. Mirrors the
memo in solution.py. Writes trace.json.
"""
import json
import os

MATRIX = [[9, 9, 4], [6, 6, 8], [2, 1, 1]]
R = len(MATRIX)
C = len(MATRIX[0])
DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))
frames = []

CODE = [
    "@lru_cache(None)",
    "def best(r, c):",
    "    longest = 1",
    "    for nr, nc in neighbours(r, c):",
    "        if matrix[nr][nc] > matrix[r][c]:",
    "            longest = max(longest, 1 + best(nr, nc))",
    "    return longest",
    "return max(best(r, c) for all cells)",
]

ROWLABELS = [str(r) for r in range(R)]
COLLABELS = [str(c) for c in range(C)]


def add(**f):
    frames.append(f)


def matrix_rows():
    return [row[:] for row in MATRIX]


# ---- Act 0: brute ----
add(act=0, rows=matrix_rows(), rowLabels=ROWLABELS, colLabels=COLLABELS, code=None,
    intro="how the same cell's downstream path gets recomputed from every start.",
    invariant="best(r,c) = length of the longest strictly-increasing path starting there.",
    note="Brute force: from each cell walk to any larger neighbour and take 1 + the best "
    "of those. Cells values shown; every start launches its own full DFS.",
    marks={"2,1": "active"}, state=[["from", "(2,1) value 1"], ["step", "to a larger neighbour"]])
add(act=0, note="A cell reachable from many places — like (1,0) value 6 — has its whole "
    "downstream re-explored each time. That repeated tail is the exponential waste.",
    marks={"1,0": "bad", "2,1": "active"},
    state=[["recomputed", "best(1,0) …"], ["cost", "exponential"]])

# ---- Act 1: memoize, fill by increasing value ----
# compute best via memo, but also record fill order (increasing value) and the
# larger-neighbour dependencies actually used.
# best(cell) depends on best(strictly-larger neighbours), so process LARGEST first.
best = {}
order = sorted(((MATRIX[r][c], r, c) for r in range(R) for c in range(C)), reverse=True)


def compute(r, c):
    longest = 1
    deps = []
    for dr, dc in DIRS:
        nr, nc = r + dr, c + dc
        if 0 <= nr < R and 0 <= nc < C and MATRIX[nr][nc] > MATRIX[r][c]:
            longest = max(longest, 1 + best[(nr, nc)])
            deps.append((nr, nc))
    return longest, deps


add(act=1, rows=matrix_rows(), code="tab", line=1,
    intro="fill best(r,c) from the largest values down, so every larger neighbour is already done.",
    invariant="best(r,c) = 1 + max best over strictly-larger neighbours (or 1 if none).",
    note="Because each step goes strictly uphill in value, there are no cycles — the "
    "grid is a DAG. Solve the biggest values first (they are the path ends) and cache each once.",
    marks={}, state=[["order", "largest value first"]])

for v, r, c in order:
    longest, deps = compute(r, c)
    best[(r, c)] = longest
    marks = {f"{r},{c}": "good"}
    for (nr, nc) in deps:
        marks[f"{nr},{nc}"] = "active"
    if deps:
        parts = ", ".join(f"best({nr},{nc})={best[(nr,nc)]}" for nr, nc in deps)
        note = (f"cell ({r},{c}) value {v}: 1 + max of larger neighbours [{parts}] "
                f"= {longest}.")
        state = [["value", v], ["larger neighbours", len(deps)], [f"best({r},{c})", longest]]
    else:
        note = f"cell ({r},{c}) value {v}: no larger neighbour, best = 1 (a peak)."
        state = [["value", v], ["larger neighbours", 0], [f"best({r},{c})", longest]]
    add(act=1, code="tab", line=5 if deps else 6, note=note,
        set={f"{r},{c}": longest}, marks=marks, state=state)

# ---- Act 2: answer + edge ----
answer = max(best.values())
# find a cell achieving the max
best_cell = max(best, key=lambda k: best[k])
add(act=2, code="tab", line=7,
    intro="the answer is the largest best(r,c) over all cells.",
    invariant="each cell solved exactly once; total work is linear in cells and edges.",
    note=f"The longest increasing path has length {answer}, starting at "
    f"({best_cell[0]},{best_cell[1]}): 1 -> 2 -> 6 -> 9.",
    marks={f"{best_cell[0]},{best_cell[1]}": "good"}, state=[["answer", answer]],
    banner=f"Longest increasing path = {answer}")

# edge: all equal -> no strict step -> every best is 1
E = [[7, 7, 7], [7, 7, 7]]
er, ec = len(E), len(E[0])
add(act=2, rows=[[1] * ec for _ in range(er)],
    rowLabels=[str(i) for i in range(er)], colLabels=[str(j) for j in range(ec)],
    code="tab", line=7,
    note="Edge case: every cell equals 7. No neighbour is strictly larger, so no step is "
    "allowed anywhere — each best is 1 and the answer is 1.",
    marks={"0,0": "good"}, state=[["answer", 1]],
    banner="All-equal grid → path length 1")

trace = {
    "player": "grid",
    "title": "Longest Increasing Path - memoize the DAG, fill by value",
    "acts": ["Brute: DFS from every cell", "Memoize (fill by value)", "Answer + edge"],
    "code": {"tab": CODE},
    "legend": [["active", "larger neighbours read"], ["good", "solved best(r,c) / answer"],
               ["bad", "recomputed downstream (waste)"]],
    "rows": matrix_rows(), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
