"""Rich full-arc trace for Number of Islands (grid renderer).
Arc: the idea (scan + flood-fill sinks a whole blob) -> run it counting islands
-> a diagonal-touch edge that splits into two. Mirrors the scan + iterative sink
in solution.py. Writes trace.json.
"""
import json
import os

frames = []

CODE = [
    "for r in range(rows):",
    "    for c in range(cols):",
    "        if grid[r][c] == '1':",
    "            count += 1",
    "            sink(r, c)   # DFS the whole blob",
    "return count",
]


def add(**f):
    frames.append(f)


def rows_from(grid):
    # '1' land shown as 1, '0' water shown as 0
    return [[int(v) for v in row] for row in grid]


def sink(grid, r, c, act, island_id):
    """Iterative DFS flood-fill, emitting a frame per cell sunk."""
    rows, cols = len(grid), len(grid[0])
    stack = [(r, c)]
    while stack:
        i, j = stack.pop()
        if i < 0 or i >= rows or j < 0 or j >= cols:
            continue
        if grid[i][j] != "1":
            continue
        grid[i][j] = "0"  # sink = mark visited
        add(act=act, rows=rows_from(grid), code="scan", line=4,
            note=f"Sink ({i},{j}) into water. Its land neighbors go on the stack "
            f"so the whole blob gets flooded as one island.",
            marks={f"{i},{j}": "good"},
            state=[["island", island_id], ["sinking", f"({i},{j})"],
                   ["stack", len(stack) + 4]])
        stack.extend([(i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)])


def run(grid0, act, intro=None, invariant=None, first_note=None):
    grid = [list(row) for row in grid0]
    rows, cols = len(grid), len(grid[0])
    first = {"act": act, "rows": rows_from(grid), "code": "scan", "line": 0,
             "marks": {}, "state": [["islands", 0]]}
    if intro:
        first["intro"] = intro
    if invariant:
        first["invariant"] = invariant
    first["note"] = first_note or "Scan the grid cell by cell. Every fresh piece " \
        "of land starts a new island."
    add(**first)
    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                count += 1
                add(act=act, rows=rows_from(grid), code="scan", line=3,
                    note=f"Fresh land at ({r},{c}) — it can't belong to an island "
                    f"we already counted (that one would have sunk it). Island #{count}.",
                    marks={f"{r},{c}": "active"},
                    state=[["islands", count], ["found land", f"({r},{c})"]])
                sink(grid, r, c, act, count)
    return count, grid


# ---- Act 0: the idea ----
G0 = [
    "110",
    "110",
    "001",
]
add(act=0, rows=rows_from(G0), rowLabels=["0", "1", "2"], colLabels=["0", "1", "2"],
    code="scan", line=2,
    intro="each blob of connected land gets sunk exactly once, and counted once.",
    invariant="counted land is already water — it can never be counted twice.",
    note="An island is a group of 1s joined up/down/left/right. Idea: scan for a "
    "1, count it, then flood-fill (sink) the entire blob so it's gone.",
    marks={"0,0": "active"}, state=[["islands", 0], ["rule", "scan + sink blob"]])

# ---- Act 1: run it ----
count, _ = run(G0, 1,
               intro="watch the counter tick only on FRESH land; sinking clears each blob.",
               invariant="every island bumps the counter exactly once.",
               first_note="Run it. Scan row by row; a 1 that's still land means a "
               "new island we haven't seen.")
add(act=1, code="scan", line=5,
    note=f"Grid fully scanned, everything sunk. Two separate blobs were found: "
    f"the top-left square and the lone cell at (2,2).",
    marks={}, state=[["islands", count]],
    banner=f"Number of islands = {count}")

# ---- Act 2: edge case (diagonal touch) ----
G2 = [
    "10",
    "01",
]
count2, _ = run(G2, 2,
                intro="diagonal neighbors are NOT connected — only 4-directional counts.",
                invariant="a flood-fill only steps up/down/left/right.",
                first_note="Edge case: two 1s touching only at a corner. Flood-fill "
                "moves in 4 directions, never diagonally.")
add(act=2, code="scan", line=5,
    note=f"The cell at (0,0) sinks without reaching (1,1) — corners don't connect. "
    f"So they count as {count2} separate islands.",
    marks={}, state=[["islands", count2]],
    banner=f"Diagonal touch -> {count2} islands (not 1)")

trace = {
    "player": "grid",
    "title": "Number of Islands - scan for fresh land, sink each blob once",
    "acts": ["The idea: scan + sink", "Run it: count blobs", "Edge: diagonal doesn't connect"],
    "code": {"scan": CODE},
    "legend": [["active", "fresh land found"], ["good", "sunk (this blob)"]],
    "rows": rows_from(G0), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
