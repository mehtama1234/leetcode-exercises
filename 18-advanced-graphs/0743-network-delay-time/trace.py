"""Full-arc trace for Network Delay Time (tree renderer used as a weighted graph).

Dijkstra from a source: the arc is brute (re-check everything each round) -> the
waste -> Dijkstra settling the closest node each pop -> an unreachable edge case.
Nodes are laid out by hand (x,y); `active` = node being settled, `done` = its
finalized shortest time badge. Mirrors solution.py. Writes trace.json.
"""
import json
import os
import heapq

frames = []

CODE = [
    "heap = [(0, k)]",
    "while heap:",
    "    d, node = heappop(heap)",
    "    if node in dist: continue",
    "    dist[node] = d",
    "    for nei, w in graph[node]:",
    "        if nei not in dist:",
    "            heappush(heap, (d + w, nei))",
    "return max(dist.values())",
]


def add(**f):
    frames.append(f)


# Graph: nodes 1..4, source k=2.  Edges (u,v,w): 2->1:1, 2->3:1, 3->4:1
# Hand-placed positions so edges read cleanly (60px circles, +30 = center).
POS = {2: (150, 0), 1: (20, 90), 3: (280, 90), 4: (280, 190)}
TIMES = [[2, 1, 1], [2, 3, 1], [3, 4, 1]]
N, K = 4, 2

graph = {n: [] for n in range(1, N + 1)}
for u, v, w in TIMES:
    graph[u].append((v, w))

nodes = [{"id": nid, "val": nid, "x": POS[nid][0], "y": POS[nid][1]} for nid in POS]
edges = [[u, v] for u, v, w in TIMES]


def state_dist(dist):
    return [["settled", " ".join(f"{k}:{v}" for k, v in sorted(dist.items())) or "-"]]


# ---- Act 0: brute force — recompute every node's best from scratch each pass ----
add(act=0, nodes=nodes, edges=edges, code="dfs", line=8,
    intro="watch the same distances get recomputed pass after pass.",
    invariant="a node's time never gets larger, only smaller.",
    note="Brute idea: relax every edge, over and over, until nothing improves. "
    "The signal starts at node 2 at time 0.",
    active=[2], done={2: 0}, state=[["passes", 0], ["relaxations", 0]])
relax = 0
best = {n: (0 if n == K else None) for n in range(1, N + 1)}
for p in range(1, 4):
    changed = False
    for u, v, w in TIMES:
        relax += 1
        if best[u] is not None and (best[v] is None or best[u] + w < best[v]):
            best[v] = best[u] + w
            changed = True
    done = {n: t for n, t in best.items() if t is not None}
    add(act=0, code="dfs", line=8,
        note=f"Pass {p}: swept all {len(TIMES)} edges again. "
        + ("Something improved, so we must sweep once more."
           if changed else "Nothing changed — but we only know that after re-sweeping."),
        active=[], done=dict(done),
        state=[["passes", p], ["relaxations", relax]])

# ---- Act 1: name the waste ----
add(act=1, nodes=nodes, edges=edges, code="dfs", line=8,
    intro="most of those edge sweeps changed nothing.",
    invariant="each node's final time is fixed the moment it is closest.",
    note=f"The waste: {relax} edge relaxations to settle {N} nodes. Every pass "
    "re-touched edges whose answer was already final.",
    active=[], done={n: t for n, t in best.items() if t is not None},
    state=[["relaxations", relax], ["nodes", N]],
    banner="Brute force re-checks finalized nodes. Dijkstra settles each one once.")

# ---- Act 2: Dijkstra — pop the closest unsettled node, settle it once ----
add(act=2, nodes=nodes, edges=edges, code="dfs", line=0,
    intro="the heap always hands back the closest unsettled node next.",
    invariant="once a node is popped, its time is final (non-negative edges).",
    note="Dijkstra: push (0, source). Pop the smallest distance, settle it, and "
    "offer its neighbors. No node is ever re-settled.",
    active=[K], done={}, state=[["heap", "[(0,2)]"], ["pops", 0]])

dist = {}
heap = [(0, K)]
pops = 0
while heap:
    d, node = heapq.heappop(heap)
    if node in dist:
        add(act=2, code="dfs", line=3,
            note=f"Popped ({d},{node}) but node {node} is already settled — stale entry, skip it.",
            active=[], done=dict(dist),
            state=[["heap", str(sorted(heap))], ["pops", pops]] )
        continue
    pops += 1
    dist[node] = d
    add(act=2, code="dfs", line=4,
        note=f"Pop the closest: node {node} at time {d}. It is now final.",
        active=[node], done=dict(dist),
        state=[["settle", f"node {node} = {d}"], ["pops", pops]])
    pushed = []
    for nei, w in graph[node]:
        if nei not in dist:
            heapq.heappush(heap, (d + w, nei))
            pushed.append(f"({d + w},{nei})")
    if pushed:
        add(act=2, code="dfs", line=7,
            note=f"Offer node {node}'s neighbors: push {', '.join(pushed)} onto the heap.",
            active=[node], done=dict(dist),
            state=[["heap", str(sorted(heap))], ["pops", pops]])

ans = max(dist.values())
add(act=2, code="dfs", line=8,
    note=f"Every node is settled. The last one to hear the signal fixes the answer: "
    f"max of {sorted(dist.values())} = {ans}.",
    active=[], done=dict(dist), state=[["answer", ans]],
    banner=f"Network delay time = {ans}  (slowest node's shortest path)")

# ---- Act 3: edge case — a node that can never be reached ----
# Edge 1->2 only; source k=2 cannot reach node 1.
POS_B = {2: (60, 40), 1: (240, 40)}
nodes_b = [{"id": nid, "val": nid, "x": POS_B[nid][0], "y": POS_B[nid][1]} for nid in POS_B]
edges_b = [[1, 2]]
add(act=3, nodes=nodes_b, edges=edges_b, code="dfs", line=1,
    intro="if a node is never popped, the signal never reaches it.",
    invariant="unsettled after the heap drains = unreachable.",
    note="Edge case: the only edge is 1 -> 2, but the signal starts at node 2. "
    "Node 1 is upstream and can never be reached.",
    active=[2], done={2: 0}, state=[["settled", "2:0"], ["heap", "[]"]])
add(act=3, code="dfs", line=8,
    note="Heap is empty but node 1 was never settled: fewer than n nodes reached. "
    "Return -1.",
    active=[], done={2: 0}, state=[["settled count", 1], ["n", 2]],
    banner="Node 1 unreachable -> return -1")

trace = {
    "player": "tree",
    "title": "Network Delay Time - brute relaxing, the waste, then Dijkstra settles each node once",
    "acts": ["Brute: re-sweep every edge", "The waste", "Dijkstra settles once", "Edge case: unreachable"],
    "code": {"dfs": CODE},
    "legend": [["active", "settling now"], ["good", "shortest time final"]],
    "nodes": nodes, "edges": edges, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
