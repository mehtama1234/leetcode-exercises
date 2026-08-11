"""Rich full-arc trace for Graph Valid Tree (tree renderer as an undirected graph).
Arc: the rule (tree == exactly n-1 edges AND connected) -> run it on a valid
5-node tree -> a same-edge-count-but-disconnected edge case (triangle + island).
Mirrors the edge-count shortcut + DFS connectivity in solution.py. Node x,y
computed here. Writes trace.json.
"""
import json
import os

frames = []

CODE = [
    "if len(edges) != n - 1:",
    "    return False        # too few -> split; too many -> a loop",
    "# n-1 edges: now just check it's all one piece",
    "seen = set(); stack = [0]",
    "while stack:",
    "    node = stack.pop()",
    "    seen.add(node)",
    "    for nb in adj[node]:",
    "        if nb not in seen: stack.append(nb)",
    "return len(seen) == n   # reached everything?",
]


def add(**f):
    frames.append(f)


def nodes_edges(pos, edges):
    nodes = [{"id": i, "val": i, "x": pos[i][0], "y": pos[i][1]} for i in pos]
    return nodes, [list(e) for e in edges]


def adj_of(n, edges):
    a = [[] for _ in range(n)]
    for x, y in edges:
        a[x].append(y)
        a[y].append(x)
    return a


# Valid tree: n=5, edges 0-1,0-2,0-3,1-4  (4 edges == n-1, connected)
POS_A = {0: (120, 0), 1: (0, 120), 2: (120, 120), 3: (240, 120), 4: (0, 230)}
N_A = 5
EDGES_A = [[0, 1], [0, 2], [0, 3], [1, 4]]
nodes_a, edges_a = nodes_edges(POS_A, EDGES_A)

# ---- Act 0: the rule ----
add(act=0, nodes=nodes_a, edges=edges_a, code="vt", line=0,
    intro="two checks: exactly n-1 edges, and every node reachable from node 0.",
    invariant="n-1 edges + connected => automatically acyclic (a tree).",
    note="A tree on n nodes has exactly n-1 edges AND is connected. The theorem: if "
    "both hold, there's no room for a cycle. So check the count, then connectivity.",
    active=[], done={}, state=[["n", N_A], ["edges", len(EDGES_A)], ["need", N_A - 1]])
add(act=0, code="vt", line=0,
    note=f"Edge count first: {len(EDGES_A)} edges, and n-1 = {N_A - 1}. They match, so "
    f"we can't already have too many (a loop) or too few (a split). Now check reach.",
    active=[], done={}, state=[["edges == n-1", "yes"]])

# ---- Act 1: connectivity DFS on the valid tree ----
adj_a = adj_of(N_A, EDGES_A)
add(act=1, nodes=nodes_a, edges=edges_a, code="vt", line=3,
    intro="DFS from node 0; a badge lights each node as we reach it.",
    invariant="seen only grows; we count how many of n nodes we touch.",
    note="Run the DFS from node 0. If we can reach all n nodes, it's connected — and "
    "with n-1 edges that makes it a valid tree.",
    active=[0], done={}, state=[["seen", 0], ["of", N_A]])
seen = set()
stack = [0]
badges = {}
while stack:
    node = stack.pop()
    if node in seen:
        continue
    seen.add(node)
    badges[node] = "seen"
    add(act=1, code="vt", line=6,
        note=f"Reach node {node}. Push its unseen neighbors. ({len(seen)}/{N_A} seen)",
        active=[node], done=dict(badges),
        state=[["at", node], ["seen", len(seen)], ["of", N_A]])
    for nb in adj_a[node]:
        if nb not in seen:
            stack.append(nb)
add(act=1, code="vt", line=9,
    note=f"DFS reached all {len(seen)} of {N_A} nodes: connected, and with n-1 edges "
    f"that's a valid tree.",
    active=[], done=dict(badges), state=[["seen", len(seen)], ["of", N_A]],
    banner="Valid tree: n-1 edges + connected")

# ---- Act 2: disconnected edge case (triangle + island) ----
# n=4, edges 0-1,1-2,0-2 : 3 edges == n-1, but node 3 is isolated AND there's a
# triangle cycle. Right edge count, still not a tree.
POS_B = {0: (60, 0), 1: (0, 120), 2: (120, 120), 3: (240, 60)}
N_B = 4
EDGES_B = [[0, 1], [1, 2], [0, 2]]
nodes_b, edges_b = nodes_edges(POS_B, EDGES_B)
adj_b = adj_of(N_B, EDGES_B)
add(act=2, nodes=nodes_b, edges=edges_b, code="vt", line=0,
    intro="the edge count passes, but connectivity fails — node 3 is stranded.",
    invariant="right count alone isn't enough; the graph must be one piece.",
    note=f"Edge case: {len(EDGES_B)} edges and n-1 = {N_B - 1} — the count passes. But "
    f"the edges form a triangle 0-1-2 (a cycle) and leave node 3 isolated.",
    active=[], done={}, state=[["n", N_B], ["edges", len(EDGES_B)], ["need", N_B - 1]])
seen = set()
stack = [0]
badges = {}
while stack:
    node = stack.pop()
    if node in seen:
        continue
    seen.add(node)
    badges[node] = "seen"
    add(act=2, code="vt", line=6,
        note=f"Reach node {node}. ({len(seen)} seen so far)",
        active=[node], done=dict(badges),
        state=[["at", node], ["seen", len(seen)], ["of", N_B]])
    for nb in adj_b[node]:
        if nb not in seen:
            stack.append(nb)
badges[3] = "?"
add(act=2, code="vt", line=9,
    note=f"DFS from 0 reaches only {len(seen)} of {N_B} nodes — node 3 is unreachable. "
    f"len(seen) != n, so not connected: NOT a valid tree, even with n-1 edges.",
    active=[3], done=dict(badges), state=[["seen", len(seen)], ["of", N_B]],
    banner="Not a tree: n-1 edges but disconnected")

trace = {
    "player": "tree",
    "title": "Graph Valid Tree - n-1 edges AND connected (which forces acyclic)",
    "acts": ["The rule: count + connect", "DFS a valid tree", "Edge: right count, disconnected"],
    "code": {"vt": CODE},
    "legend": [["active", "visiting now / stranded"], ["good", "reached from node 0"]],
    "nodes": nodes_a, "edges": edges_a, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
