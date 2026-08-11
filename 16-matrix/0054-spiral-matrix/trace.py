"""Rich full-arc trace for Spiral Matrix (grid renderer).
No wasteful baseline: this is "the rule -> run it -> edge". Four shrinking walls
peel the grid ring by ring. Mirrors solution.py. Writes trace.json.
"""
import json
import os

frames = []

CODE = [
    "while top <= bottom and left <= right:",
    "    for c in range(left, right+1): out += matrix[top][c]",
    "    top += 1",
    "    for r in range(top, bottom+1): out += matrix[r][right]",
    "    right -= 1",
    "    if top <= bottom:",
    "        for c in range(right, left-1, -1): out += matrix[bottom][c]",
    "        bottom -= 1",
    "    if left <= right:",
    "        for r in range(bottom, top-1, -1): out += matrix[r][left]",
    "        left += 1",
]


def add(**f):
    frames.append(f)


def grid_of(m):
    return [row[:] for row in m]


def rlabels(m):
    return [str(i) for i in range(len(m))]


def clabels(m):
    return [str(i) for i in range(len(m[0]))]


def walk(matrix, act, intro=None, invariant=None, first_note=None):
    """Emit frames for one full spiral, collecting result; mirror solution.py exactly."""
    M, Nn = len(matrix), len(matrix[0])
    out = []
    top, bottom, left, right = 0, M - 1, 0, Nn - 1
    collected = {}  # "r,c" -> order marks stay "good"

    add(act=act, rows=grid_of(matrix), rowLabels=rlabels(matrix),
        colLabels=clabels(matrix), code="peel", line=0,
        intro=intro, invariant=invariant,
        note=first_note or "Four walls bound the unvisited part: top, bottom, left, "
        "right. Each direction walks one wall, then that wall steps inward.",
        marks={}, state=[["top", top], ["bottom", bottom], ["left", left],
                         ["right", right], ["collected", 0]])

    def snap(rr, cc, note, line):
        collected[f"{rr},{cc}"] = True
        marks = {k: "good" for k in collected}
        marks[f"{rr},{cc}"] = "active"
        add(act=act, code="peel", line=line, note=note, marks=marks,
            state=[["top", top], ["bottom", bottom], ["left", left],
                   ["right", right], ["collected", len(out)]])

    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            out.append(matrix[top][c])
            snap(top, c, f"top row {top}, going right: read {matrix[top][c]}.", 1)
        top += 1
        for r in range(top, bottom + 1):
            out.append(matrix[r][right])
            snap(r, right, f"right column {right}, going down: read {matrix[r][right]}.", 3)
        right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                out.append(matrix[bottom][c])
                snap(bottom, c, f"bottom row {bottom}, going left: read {matrix[bottom][c]}.", 6)
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                out.append(matrix[r][left])
                snap(r, left, f"left column {left}, going up: read {matrix[r][left]}.", 9)
            left += 1
    return out


# ---- Act 0: the rule on a 3x3 ----
g1 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
res1 = walk(g1, 0,
            intro="how the four walls close in until they cross.",
            invariant="everything outside the walls is already collected.",
            first_note="The rule: walk the outer ring clockwise, shrink the walls, "
            "repeat on what's left. Start with top=0, bottom=2, left=0, right=2.")
assert res1 == [1, 2, 3, 6, 9, 8, 7, 4, 5]
add(act=0, code="peel", line=0,
    note=f"Walls have crossed. Spiral order = {res1}.",
    marks={f"{r},{c}": "good" for r in range(3) for c in range(3)},
    banner=f"3x3 spiral = {res1}")

# ---- Act 1: non-square 3x4 (shows why the guards matter) ----
g2 = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
res2 = walk(g2, 1,
            intro="a non-square grid, where the mid-loop guards do real work.",
            invariant="a lone leftover row/column must not be walked twice.",
            first_note="3x4 grid. After the top row and right column, only one middle "
            "row remains; the guards keep us from re-walking it backward.")
assert res2 == [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]
add(act=1, code="peel", line=0,
    note=f"Spiral order = {res2}. The `if top <= bottom` / `if left <= right` guards "
    "stopped the single inner row being read twice.",
    marks={f"{r},{c}": "good" for r in range(3) for c in range(4)},
    banner=f"3x4 spiral = {res2}")

# ---- Act 2: edge — single row ----
g3 = [[1, 2, 3, 4]]
res3 = walk(g3, 2,
            intro="the degenerate case: one row.",
            invariant="after the top row, top passes bottom and the loop ends.",
            first_note="Single row. The top-row pass reads everything; then top > "
            "bottom and both guards fail, so nothing is re-read.")
assert res3 == [1, 2, 3, 4]
add(act=2, code="peel", line=0, note=f"Single row spiral = {res3}.",
    marks={f"0,{c}": "good" for c in range(4)}, banner=f"Single row = {res3}")

trace = {
    "player": "grid",
    "title": "Spiral Matrix - four shrinking walls peel the grid ring by ring",
    "acts": ["The rule (3x3)", "Non-square 3x4 (guards)", "Edge: single row"],
    "code": {"peel": CODE},
    "legend": [["active", "cell being read now"], ["good", "already collected"]],
    "rows": grid_of(g1), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
