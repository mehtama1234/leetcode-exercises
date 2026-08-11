"""Full-arc trace for Min Cost to Connect All Points (tree renderer as a weighted graph).

Minimum Spanning Tree via Prim. Arc: brute (a wasteful full-pair rescan each step)
-> the waste -> Prim grows the tree, adding the cheapest crossing edge -> a tiny
two-point edge case. Node x,y come from the actual point coordinates (scaled).
`active` = point just pulled into the tree, `done` = the cost that attached it.
Mirrors solution.py's Prim. Writes trace.json.
"""
import json
import os
import heapq

frames = []

CODE = [
    "in_tree = [False]*n; total = 0",
    "heap = [(0, 0)]              # seed point 0 free",
    "while heap and edges < n:",
    "    cost, i = heappop(heap)",
    "    if in_tree[i]: continue",
    "    in_tree[i] = True; total += cost",
    "    for j in range(n):",
    "        if not in_tree[j]:",
    "            heappush(heap, (dist(i, j), j))",
]


def add(**f):
    frames.append(f)


PTS = [[0, 0], [2, 2], [3, 10], [5, 2], [7, 0]]
N = len(PTS)


def dist(i, j):
    (x1, y1), (x2, y2) = PTS[i], PTS[j]
    return abs(x1 - x2) + abs(y1 - y2)


# Map point coords -> screen. x grows right, y grows down; scale to fit ~360x220.
def layout(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    sx = 300 / max(1, (max(xs) - min(xs)))
    sy = 180 / max(1, (max(ys) - min(ys)))
    return [{"id": i, "val": i,
             "x": int((p[0] - min(xs)) * sx),
             "y": int((p[1] - min(ys)) * sy)} for i, p in enumerate(pts)]


nodes = layout(PTS)
# Show all candidate connections as faint edges (complete graph).
edges = [[i, j] for i in range(N) for j in range(i + 1, N)]

# ---- Act 0: brute — every step, rescan all pairs to find the cheapest crossing ----
add(act=0, nodes=nodes, edges=edges, code="dfs", line=0,
    intro="the naive tree-grower re-scans every point pair on each add.",
    invariant="the tree only grows; a joined point never leaves.",
    note="We must wire all 5 points for the least total Manhattan cost — a Minimum "
    "Spanning Tree. Naive Prim: at each of n steps, scan all pairs for the cheapest "
    "edge crossing out of the tree.",
    active=[0], done={0: 0}, state=[["points", N], ["pair scans", 0]])
scans = 0
in_tree = [False] * N
in_tree[0] = True
for _ in range(N - 1):
    # brute crossing-edge search
    for i in range(N):
        for j in range(N):
            if in_tree[i] and not in_tree[j]:
                scans += 1
    # pick cheapest crossing to actually advance (mirror of Prim result)
    best = min((dist(i, j), j) for i in range(N) if in_tree[i]
               for j in range(N) if not in_tree[j])
    in_tree[best[1]] = True
add(act=0, code="dfs", line=0,
    note=f"To grow a 5-point tree the naive scan touched {scans} ordered pairs, "
    "re-examining points already settled every single step.",
    active=[], done={i: None for i in range(N)},
    state=[["pair scans", scans]])

# ---- Act 1: name the waste ----
add(act=1, nodes=nodes, edges=edges, code="dfs", line=0,
    intro="the same finalized points get re-scanned again and again.",
    invariant="a point's cheapest attaching edge is fixed once it joins.",
    note=f"The waste: {scans} pair scans for {N} points. A min-heap of candidate "
    "edges out of the tree gives the cheapest crossing in one pop instead.",
    active=[], done={}, state=[["pair scans", scans], ["points", N]],
    banner="Rescanning all pairs is wasteful. A heap yields the cheapest crossing edge directly.")

# ---- Act 2: Prim with the heap ----
add(act=2, nodes=nodes, edges=edges, code="dfs", line=1,
    intro="the heap hands back the cheapest edge leaving the tree next.",
    invariant="each pop that survives adds exactly one point to the tree.",
    note="Prim: seed point 0 at cost 0, offer edges to all others, then repeatedly "
    "pull the cheapest edge that reaches a point not yet in the tree.",
    active=[0], done={}, state=[["heap", "[(0,0)]"], ["total", 0]])

in_tree = [False] * N
total = 0
built = 0
heap = [(0, 0)]
done = {}
while heap and built < N:
    cost, i = heapq.heappop(heap)
    if in_tree[i]:
        continue
    in_tree[i] = True
    total += cost
    built += 1
    done[i] = cost
    add(act=2, code="dfs", line=5,
        note=(f"Seed point 0 joins free (cost 0)." if built == 1
              else f"Cheapest crossing edge costs {cost}: point {i} joins the tree. Total now {total}."),
        active=[i], done=dict(done),
        state=[["join", f"point {i} +{cost}"], ["total", total], ["in tree", built]])
    offers = []
    for j in range(N):
        if not in_tree[j]:
            heapq.heappush(heap, (dist(i, j), j))
            offers.append(f"({dist(i, j)},{j})")
    if offers:
        add(act=2, code="dfs", line=8,
            note=f"Offer edges from point {i} to the remaining points: push {', '.join(offers)}.",
            active=[i], done=dict(done),
            state=[["total", total], ["candidates", len(offers)]])

add(act=2, code="dfs", line=2,
    note=f"All {N} points connected with no cycles. Sum of the attaching edges "
    f"= {total}.",
    active=[], done=dict(done), state=[["MST cost", total]],
    banner=f"Min cost to connect all points = {total}")

# ---- Act 3: edge case — two points, one edge ----
PTS_B = [[0, 0], [1, 1]]
nodes_b = layout(PTS_B)
edges_b = [[0, 1]]
d01 = abs(0 - 1) + abs(0 - 1)
add(act=3, nodes=nodes_b, edges=edges_b, code="dfs", line=1,
    intro="two points have exactly one possible connection.",
    invariant="a spanning tree on n points has n-1 edges.",
    note=f"Edge case: two points at (0,0) and (1,1). Only one edge to add, cost "
    f"|0-1|+|0-1| = {d01}.",
    active=[0], done={0: 0}, state=[["heap", "[(0,0)]"], ["total", 0]])
add(act=3, code="dfs", line=5,
    note=f"Point 1 joins at cost {d01}. Tree complete with one edge.",
    active=[1], done={0: 0, 1: d01}, state=[["MST cost", d01]],
    banner=f"Two points -> cost {d01}. (One point -> 0.)")

trace = {
    "player": "tree",
    "title": "Connect All Points - brute pair-scan, the waste, Prim grows the MST, then two points",
    "acts": ["Brute: rescan all pairs", "The waste", "Prim grows the tree", "Edge case: two points"],
    "code": {"dfs": CODE},
    "legend": [["active", "point joining now"], ["good", "in tree, attach cost"]],
    "nodes": nodes, "edges": edges, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
