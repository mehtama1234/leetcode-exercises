"""Full-arc trace for Swim in Rising Water (tree renderer as a weighted graph).

Minimax-path Dijkstra: the cost of reaching a cell is the tallest elevation on
the best path to it. Arc: the rule (max, not sum) -> Dijkstra settling the cell
with the smallest worst-barrier -> a bigger 3x3 grid -> a 1x1 edge case. Each cell
is a node placed on a grid; edges join 4-adjacent cells. `active` = cell popped/
settled, `done` = the minimal max-elevation to reach it. Mirrors solution.py's
Dijkstra. Writes trace.json.
"""
import json
import os
import heapq

frames = []

CODE = [
    "heap = [(grid[0][0], 0, 0)]",
    "while heap:",
    "    t, r, c = heappop(heap)",
    "    if seen[r][c]: continue",
    "    seen[r][c] = True",
    "    if (r, c) == goal: return t",
    "    for nr, nc in neighbors(r, c):",
    "        push (max(t, grid[nr][nc]), nr, nc)",
]

XSTEP, YSTEP = 90, 90


def add(**f):
    frames.append(f)


def layout(grid):
    n = len(grid)
    nodes, edges = [], []
    nid = {}
    for r in range(n):
        for c in range(n):
            i = r * n + c
            nid[(r, c)] = i
            # label shows the cell's own elevation
            nodes.append({"id": i, "val": grid[r][c], "x": c * XSTEP, "y": r * YSTEP})
    for r in range(n):
        for c in range(n):
            if c + 1 < n:
                edges.append([nid[(r, c)], nid[(r, c + 1)]])
            if r + 1 < n:
                edges.append([nid[(r, c)], nid[(r + 1, c)]])
    return nodes, edges, nid


def run_dijkstra(grid, act, nodes, edges, nid, first_note, first_intro, first_inv):
    """Instrument the exact Dijkstra from solution.py, emitting frames."""
    n = len(grid)
    seen = [[False] * n for _ in range(n)]
    heap = [(grid[0][0], 0, 0)]
    done = {}
    add(act=act, nodes=nodes, edges=edges, code="dfs", line=0,
        intro=first_intro, invariant=first_inv, note=first_note,
        active=[nid[(0, 0)]], done={}, state=[["heap", f"[({grid[0][0]},0,0)]"], ["pops", 0]])
    pops = 0
    while heap:
        t, r, c = heapq.heappop(heap)
        if seen[r][c]:
            continue
        seen[r][c] = True
        pops += 1
        done[nid[(r, c)]] = t
        goal = (r == n - 1 and c == n - 1)
        add(act=act, code="dfs", line=5 if goal else 4,
            note=(f"Popped the goal ({r},{c}) with worst-barrier {t}. That is the "
                  f"earliest time the whole path is walkable — done."
                  if goal else
                  f"Pop the cell with the smallest worst-barrier: ({r},{c}), needs time {t}. Settle it."),
            active=[nid[(r, c)]], done=dict(done),
            state=[["settle", f"({r},{c}) = {t}"], ["pops", pops]])
        if goal:
            return t, done, pops
        pushed = []
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and not seen[nr][nc]:
                cost = max(t, grid[nr][nc])
                heapq.heappush(heap, (cost, nr, nc))
                pushed.append(f"({cost},{nr},{nc})")
        if pushed:
            add(act=act, code="dfs", line=7,
                note=f"Offer neighbors of ({r},{c}): cost to stand on each = "
                f"max(barrier {t}, that cell). Push {', '.join(pushed)}.",
                active=[nid[(r, c)]], done=dict(done),
                state=[["pops", pops], ["pushed", len(pushed)]])
    return None, done, pops


# ---- Act 0: the rule, on a 2x2 grid ----
GRID_A = [[0, 2], [1, 3]]
nodes_a, edges_a, nid_a = layout(GRID_A)
add(act=0, nodes=nodes_a, edges=edges_a, code="dfs", line=0,
    intro="a path's cost is its tallest cell, not the sum of steps.",
    invariant="you can only stand on a cell once water >= its elevation.",
    note="At time t the water level is t; you may stand on any cell with elevation "
    "<= t. The cost of a path is its highest cell — you wait for water to top the "
    "tallest barrier. We want the path whose maximum is smallest.",
    active=[nid_a[(0, 0)]], done={}, state=[["start", "(0,0)"], ["goal", "(1,1)"]])
add(act=0, code="dfs", line=7,
    note="So Dijkstra relaxes with max(cost so far, next cell) instead of a sum. "
    "The heap always expands the cell with the smallest worst-barrier reached so far.",
    active=[nid_a[(0, 0)]], done={nid_a[(0, 0)]: 0},
    state=[["relax", "max(t, cell)"]],
    banner="Minimax path: minimize the largest elevation you must cross.")

# ---- Act 1: run Dijkstra on the 2x2 grid ----
ans_a, done_a, pops_a = run_dijkstra(
    GRID_A, 1, nodes_a, edges_a, nid_a,
    "Run it: push the start's elevation, then always pop the smallest worst-barrier.",
    "the first time the goal pops, its value is the answer.",
    "a settled cell holds the minimal max-elevation to reach it.")
assert ans_a == 3, ans_a
add(act=1, code="dfs", line=5,
    note=f"Goal reached at time {ans_a}: any route to (1,1) must cross the elevation-3 "
    "corner, so 3 is the earliest arrival.",
    active=[], done=dict(done_a), state=[["answer", ans_a]],
    banner=f"Earliest swim time = {ans_a}")

# ---- Act 2: a 3x3 where the minimax choice really bites ----
GRID_B = [[0, 1, 2],
          [8, 9, 3],
          [7, 6, 5]]
nodes_b, edges_b, nid_b = layout(GRID_B)
ans_b, done_b, pops_b = run_dijkstra(
    GRID_B, 2, nodes_b, edges_b, nid_b,
    "A 3x3 with a tall 8/9 wall in the way. Same rule — watch it snake around the wall.",
    "cheaper (lower-max) cells settle before taller ones.",
    "the heap orders cells by worst-barrier, never by grid distance.")
assert ans_b == 5, ans_b
add(act=2, code="dfs", line=5,
    note=f"The best path hugs the low border 0->1->2->3->5, peaking at {ans_b}; going "
    "through the 8 or 9 would cost far more.",
    active=[], done=dict(done_b), state=[["answer", ans_b], ["cells settled", pops_b]],
    banner=f"Earliest swim time = {ans_b}")

# ---- Act 3: 1x1 edge case ----
GRID_C = [[0]]
nodes_c, edges_c, nid_c = layout(GRID_C)
add(act=3, nodes=nodes_c, edges=edges_c, code="dfs", line=0,
    intro="start and goal are the same cell.",
    invariant="you begin already standing on the goal.",
    note="Edge case: a 1x1 grid. Start is the goal, elevation 0 — no waiting needed.",
    active=[nid_c[(0, 0)]], done={}, state=[["grid", "1x1"]])
add(act=3, code="dfs", line=5,
    note="Pop (0,0) with barrier 0, which is the goal. Answer 0.",
    active=[nid_c[(0, 0)]], done={nid_c[(0, 0)]: 0}, state=[["answer", 0]],
    banner="Already at the goal -> time 0")

trace = {
    "player": "tree",
    "title": "Swim in Rising Water - the max rule, Dijkstra on the minimax path, big grid, then 1x1",
    "acts": ["The rule: cost is a max", "Run it (2x2)", "Bigger grid", "Edge case: 1x1"],
    "code": {"dfs": CODE},
    "legend": [["active", "cell settling now"], ["good", "min worst-barrier to reach"]],
    "nodes": nodes_a, "edges": edges_a, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
