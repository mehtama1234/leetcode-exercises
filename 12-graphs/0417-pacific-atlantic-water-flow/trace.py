"""Rich full-arc trace for Pacific Atlantic Water Flow (grid renderer).
Arc: the naive waste (search downhill per cell) -> reverse-flood from each ocean
-> intersect for the answer. Mirrors the reverse BFS/DFS in solution.py. The grid
values are the heights; marks show which cells each ocean's flood reaches.
Writes trace.json.
"""
import json
import os

frames = []

HEIGHTS = [
    [1, 2, 2, 3, 5],
    [3, 2, 3, 4, 4],
    [2, 4, 5, 3, 1],
    [6, 7, 1, 4, 5],
    [5, 1, 1, 2, 4],
]
ROWS, COLS = len(HEIGHTS), len(HEIGHTS[0])
RL = [str(r) for r in range(ROWS)]
CL = [str(c) for c in range(COLS)]

CODE = [
    "def flood(starts):        # walk UPHILL from an ocean edge",
    "    reach = set()",
    "    stack = list(starts)",
    "    while stack:",
    "        r, c = stack.pop()",
    "        reach.add((r, c))",
    "        for nr, nc in neighbors(r, c):",
    "            if heights[nr][nc] >= heights[r][c]:",
    "                stack.append((nr, nc))   # uphill in reverse",
    "    return reach",
    "return pacific & atlantic",
]


def add(**f):
    frames.append(f)


def flood(starts):
    """Reverse flood-fill; returns the set of reachable cells (order-free)."""
    reach = set()
    stack = list(starts)
    while stack:
        r, c = stack.pop()
        if (r, c) in reach:
            continue
        reach.add((r, c))
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and (nr, nc) not in reach \
                    and HEIGHTS[nr][nc] >= HEIGHTS[r][c]:
                stack.append((nr, nc))
    return reach


PAC_STARTS = [(0, c) for c in range(COLS)] + [(r, 0) for r in range(ROWS)]
ATL_STARTS = [(ROWS - 1, c) for c in range(COLS)] + [(r, COLS - 1) for r in range(ROWS)]
pac = flood(PAC_STARTS)
atl = flood(ATL_STARTS)
both = pac & atl


def marks_for(cells, cls):
    return {f"{r},{c}": cls for (r, c) in cells}


# ---- Act 0: the naive waste ----
add(act=0, rows=HEIGHTS, rowLabels=RL, colLabels=CL, code=None,
    intro="how many times a mountain cell is re-walked by everything downstream.",
    invariant="water flows to a neighbor only if it is not higher.",
    note="Naive idea: for EACH cell, search downhill and see if it hits an ocean. "
    "A tall cell in the middle gets re-explored by every path that drains through it.",
    marks={"2,2": "active"}, state=[["approach", "search per cell"], ["cost", "repeated"]])
add(act=0,
    note="Cell (2,2) height 5 sits on many drainage routes, so it's visited again "
    "and again. That overlapping downhill search is the waste we delete.",
    marks={"2,2": "bad", "1,3": "dim", "3,3": "dim", "2,3": "dim"},
    state=[["re-explored", "(2,2) ..."], ["fix", "reverse the flow"]])

# ---- Act 1: flood inward from the Pacific ----
add(act=1, rows=HEIGHTS, rowLabels=RL, colLabels=CL, code="flood", line=0,
    intro="start AT the ocean edge and climb uphill — every cell reached can drain here.",
    invariant="we step to a neighbor only when it's >= our height (uphill in reverse).",
    note="Reverse it. The Pacific touches the top row and left column. Flood inward "
    "from that border, moving only to cells at least as high.",
    marks=marks_for(PAC_STARTS, "active"),
    state=[["ocean", "Pacific"], ["seeds", len(set(PAC_STARTS))]])
add(act=1, code="flood", line=7,
    note=f"Climbing uphill from the Pacific border reaches {len(pac)} cells. Each one "
    f"can drain to the Pacific (forward, water runs downhill back to the edge).",
    marks=marks_for(pac, "good"),
    state=[["Pacific reaches", len(pac)]])

# ---- Act 2: flood inward from the Atlantic ----
add(act=2, rows=HEIGHTS, rowLabels=RL, colLabels=CL, code="flood", line=0,
    intro="same climb, from the opposite corner's ocean.",
    invariant="a cell counts only if BOTH floods reach it.",
    note="Now the Atlantic: it touches the bottom row and right column. Flood inward "
    "from that border the same way.",
    marks=marks_for(ATL_STARTS, "active"),
    state=[["ocean", "Atlantic"], ["seeds", len(set(ATL_STARTS))]])
add(act=2, code="flood", line=7,
    note=f"The Atlantic flood reaches {len(atl)} cells.",
    marks=marks_for(atl, "good"),
    state=[["Atlantic reaches", len(atl)]])

# ---- Act 3: intersect + edge ----
add(act=3, rows=HEIGHTS, rowLabels=RL, colLabels=CL, code="flood", line=10,
    intro="the answer is the overlap — cells both floods marked.",
    invariant="a cell in both sets drains to both oceans.",
    note=f"Intersect the two reachable sets. The {len(both)} cells reached by BOTH "
    f"floods are exactly the ones that drain to both oceans.",
    marks=marks_for(both, "good"),
    state=[["Pacific", len(pac)], ["Atlantic", len(atl)], ["both", len(both)]],
    banner=f"{len(both)} cells reach both oceans")

flat = [[1, 1], [1, 1]]


def flood_flat(starts):
    reach = set()
    stack = list(starts)
    while stack:
        r, c = stack.pop()
        if (r, c) in reach:
            continue
        reach.add((r, c))
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < 2 and 0 <= nc < 2 and (nr, nc) not in reach \
                    and flat[nr][nc] >= flat[r][c]:
                stack.append((nr, nc))
    return reach


fp = flood_flat([(0, 0), (0, 1), (1, 0)])
fa = flood_flat([(1, 1), (0, 1), (1, 0)])
fboth = fp & fa
add(act=3, rows=flat, rowLabels=["0", "1"], colLabels=["0", "1"], code="flood", line=7,
    note="Edge case: a flat grid, all heights equal. 'Uphill' is satisfied everywhere, "
    "so both floods cover every cell — all of them drain to both oceans.",
    marks=marks_for(fboth, "good"), state=[["both", len(fboth)]],
    banner="Flat grid -> every cell qualifies")

trace = {
    "player": "grid",
    "title": "Pacific Atlantic - flood uphill from each ocean, then intersect",
    "acts": ["Naive: search per cell", "Flood from Pacific", "Flood from Atlantic",
             "Intersect + edge"],
    "code": {"flood": CODE},
    "legend": [["active", "ocean border / seeds"], ["good", "reachable / answer"],
               ["bad", "re-explored (waste)"], ["dim", "downstream routes"]],
    "rows": HEIGHTS, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
