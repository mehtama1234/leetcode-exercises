"""Rich full-arc trace for Clone Graph (tree renderer used as a general graph).
Graphs have no wasteful brute baseline worth animating, so the arc is: the rule
(map original->clone, record before recursing) -> DFS the square graph making
copies -> a 2-node cycle edge case that terminates. Mirrors the DFS in
solution.py. Node x,y are computed here. Writes trace.json.
"""
import json
import os

frames = []

CODE = [
    "def dfs(original):",
    "    if original in clones:",
    "        return clones[original]   # already copied",
    "    copy = Node(original.val)",
    "    clones[original] = copy       # record BEFORE recursing",
    "    for nb in original.neighbors:",
    "        copy.neighbors.append(dfs(nb))",
    "    return copy",
]


def add(**f):
    frames.append(f)


# Square graph 1-2-3-4-1 (LeetCode's example). Positions laid out as a square.
# ids are the original node vals; edges are undirected pairs.
POS_A = {1: (0, 0), 2: (150, 0), 3: (150, 130), 4: (0, 130)}
ADJ_A = {1: [2, 4], 2: [1, 3], 3: [2, 4], 4: [1, 3]}


def nodes_edges(pos, adj):
    nodes = [{"id": i, "val": i, "x": pos[i][0], "y": pos[i][1]} for i in pos]
    seen = set()
    edges = []
    for a, nbs in adj.items():
        for b in nbs:
            key = tuple(sorted((a, b)))
            if key not in seen:
                seen.add(key)
                edges.append([a, b])
    return nodes, edges


nodes_a, edges_a = nodes_edges(POS_A, ADJ_A)

# ---- Act 0: the rule ----
add(act=0, nodes=nodes_a, edges=edges_a, code="dfs", line=4,
    intro="each node gets ONE clone, recorded in the map before we recurse.",
    invariant="a node in the map is never cloned again — that's what stops cycles.",
    note="Deep-copy means new node objects with the same wiring. The trick is a map "
    "'original -> clone'. Record the clone BEFORE visiting neighbors, so a cycle "
    "finds the clone already there instead of looping forever.",
    active=[1], done={}, state=[["rule", "clone once, record first"]])
add(act=0, code="dfs", line=1,
    note="The map is also the done-list: the first line of dfs checks it. If the "
    "original was seen, hand back its existing clone and stop.",
    active=[], done={}, state=[["map", "original -> clone"]])

# ---- Act 1: DFS the square ----
clones = {}


def dfs(node, act):
    if node in clones:
        add(act=act, code="dfs", line=2,
            note=f"Reached node {node} again, but its clone already exists — return "
            f"it, don't recurse. This is what makes the cycle safe.",
            active=[node], done=dict(clones),
            state=[["revisit", node], ["clones", len(clones)]])
        return
    clones[node] = node
    add(act=act, code="dfs", line=4,
        note=f"First time at node {node}: make its clone and record it in the map "
        f"NOW, before touching neighbors.",
        active=[node], done=dict(clones),
        state=[["cloned", node], ["clones", len(clones)]])
    for nb in ADJ_A[node]:
        # Only narrate a step when it does real work: a first visit (new clone)
        # or a cycle-return. Skip the mirror back-edge that revisits the parent
        # trivially, so the trace stays tight.
        if nb not in clones:
            add(act=act, code="dfs", line=6,
                note=f"From clone {node}, copy the edge to neighbor {nb} by cloning {nb}.",
                active=[node, nb], done=dict(clones),
                state=[["at", node], ["recurse into", nb]])
        dfs(nb, act)


add(act=1, nodes=nodes_a, edges=edges_a, code="dfs", line=0,
    intro="clones (badges) appear once per node, then revisits just return them.",
    invariant="every node's clone is created exactly once.",
    note="Run it from node 1. Watch each node get cloned once; later arrivals just "
    "return the existing clone.",
    active=[1], done={}, state=[["start", "node 1"]])
dfs(1, 1)
add(act=1, code="dfs", line=7,
    note=f"All {len(clones)} nodes cloned exactly once; every edge copied to point "
    f"at clones. The new graph mirrors the old one with brand-new objects.",
    active=[], done=dict(clones), state=[["nodes cloned", len(clones)]],
    banner=f"Deep copy done: {len(clones)} new nodes, same square wiring")

# ---- Act 2: 2-node cycle edge case ----
POS_B = {1: (0, 0), 2: (150, 0)}
ADJ_B = {1: [2], 2: [1]}
nodes_b, edges_b = nodes_edges(POS_B, ADJ_B)
clones = {}
add(act=2, nodes=nodes_b, edges=edges_b, code="dfs", line=0,
    intro="the back-edge 2->1 arrives at an already-cloned node.",
    invariant="record-before-recurse turns the cycle into a map lookup.",
    note="Edge case: two nodes pointing at each other. Without the record-first map, "
    "this loops forever. With it, the cycle just returns the existing clone.",
    active=[1], done={}, state=[["shape", "1 <-> 2 cycle"]])
dfs(1, 2)
add(act=2, code="dfs", line=7,
    note="Node 1 cloned, node 2 cloned, then 2's edge back to 1 found 1's clone "
    "already in the map — done, no infinite loop.",
    active=[], done=dict(clones), state=[["clones", len(clones)]],
    banner="Cycle handled: 2 clones, no infinite recursion")

trace = {
    "player": "tree",
    "title": "Clone Graph - record each clone before recursing so cycles terminate",
    "acts": ["The rule: map + record first", "DFS the square graph", "Edge: a 2-node cycle"],
    "code": {"dfs": CODE},
    "legend": [["active", "visiting now"], ["good", "cloned (badge = clone)"]],
    "nodes": nodes_a, "edges": edges_a, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
