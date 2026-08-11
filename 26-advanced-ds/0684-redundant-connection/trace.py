"""Rich full-arc trace for Redundant Connection (tree renderer, Union-Find forest).
No wasteful baseline, so the arc is: the rule (the redundant edge is the first one
joining two nodes already connected) -> process edges in order, unioning, until one
edge finds both ends already in the same group -> a tiny edge case. Nodes are graph
nodes; solid edges are ones we accepted into the forest; the offending edge lights
when its two endpoints share a root. Mirrors UnionFind + findRedundantConnection in
solution.py. Writes trace.json.
"""
import json
import os

edges = [[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]]  # redundant edge is [1, 4]
frames = []

CODE = [
    "uf = UnionFind(n)",
    "for (u, v) in edges:",
    "    if not uf.union(u, v):     # already connected?",
    "        return [u, v]          # this edge closes the cycle",
    "return []",
]

XSTEP = 90


def add(**f):
    frames.append(f)


class UF:
    def __init__(self, n):
        self.parent = list(range(n + 1))
        self.rank = [0] * (n + 1)

    def find(self, x):
        r = x
        while self.parent[r] != r:
            r = self.parent[r]
        while self.parent[x] != r:
            self.parent[x], x = r, self.parent[x]
        return r

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False, ra, rb
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True, ra, rb


NODE_IDS = sorted({x for e in edges for x in e})  # 1..5


def nodes_layout(y=70):
    return [{"id": v, "val": v, "x": (i) * XSTEP, "y": y} for i, v in enumerate(NODE_IDS)]


NODES = nodes_layout()


def roots_of(uf):
    return {v: v for v in NODE_IDS if uf.parent[v] == v}


# ---- Act 0: the rule ----
uf = UF(len(edges))
add(act=0, nodes=NODES, edges=[], code="rc", line=0,
    intro="a tree has no cycles; the one extra edge is the first that links two already-linked nodes.",
    invariant="two nodes are in the same group iff Union-Find gives them the same root.",
    note="A tree on n nodes has n-1 edges; we get n, so exactly one edge closes a cycle. "
    "Process edges in order and ask: are these two ends already connected?",
    active=NODE_IDS, done={}, state=[["nodes", len(NODE_IDS)], ["edges", len(edges)]])

# ---- Act 1: process edges, find the cycle-closer ----
accepted = []  # edges kept in the forest
answer = None
add(act=1, nodes=NODES, edges=[], code="rc", line=1,
    intro="each accepted edge joins two groups; the first that can't is the redundant one.",
    invariant="the forest stays acyclic as long as every edge merges different groups.",
    note="Union each edge in input order. The first time union reports 'already connected,' "
    "that edge is the answer.",
    active=[], done={}, state=[["edge", "-"]])
for (u, v) in edges:
    ru, rv = uf.find(u), uf.find(v)
    same = ru == rv
    add(act=1, code="rc", line=2,
        note=f"edge {u}-{v}: root({u}) = {ru}, root({v}) = {rv}. "
             + ("Same group -> this edge closes a cycle!" if same
                else "Different groups -> safe to add."),
        nodes=NODES, edges=list(accepted),
        active=[u, v], done={},
        state=[["edge", f"{u}-{v}"], ["roots", f"{ru},{rv}"], ["same group?", same]])
    if same:
        answer = [u, v]
        add(act=1, code="rc", line=3,
            note=f"{u} and {v} were already connected through the path we built. Edge "
                 f"[{u}, {v}] is the redundant one.",
            nodes=NODES, edges=accepted + [[u, v]],
            active=[u, v], done={u: "X", v: "X"},
            state=[["answer", f"[{u}, {v}]"]],
            banner=f"Redundant connection = [{u}, {v}]")
        break
    uf.union(u, v)
    accepted.append([u, v])
    add(act=1, code="rc", line=2,
        note=f"Added {u}-{v} to the forest; the two groups are now one.",
        nodes=NODES, edges=list(accepted),
        active=[uf.find(u)], done={}, state=[["edges kept", len(accepted)]])

# ---- Act 2: tiny edge case ----
edges2 = [[1, 2], [1, 2]]  # two nodes joined twice -> second is redundant
uf2 = UF(2)
NODES2 = [{"id": 1, "val": 1, "x": 0, "y": 70}, {"id": 2, "val": 2, "x": XSTEP, "y": 70}]
add(act=2, nodes=NODES2, edges=[], code="rc", line=1,
    intro="the smallest cycle: two nodes joined by two edges.",
    invariant="the second edge between the same pair is always redundant.",
    note="Edge case: nodes 1 and 2 joined twice. The first edge merges them; the second "
    "finds them already connected.",
    active=[1, 2], done={}, state=[["edges", 2]])
uf2.union(1, 2)
add(act=2, code="rc", line=2,
    note="Edge 1-2: merges the two singletons into one group.",
    nodes=NODES2, edges=[[1, 2]], active=[1], done={}, state=[["kept", "1-2"]])
add(act=2, code="rc", line=3,
    note="Second edge 1-2: root(1) == root(2) already -> [1, 2] is redundant.",
    nodes=NODES2, edges=[[1, 2]], active=[1, 2], done={1: "X", 2: "X"},
    state=[["answer", "[1, 2]"]], banner="Redundant = [1, 2]")

trace = {
    "player": "tree",
    "title": "Redundant Connection - the first edge that joins two already-linked nodes",
    "acts": ["The rule", "Find the cycle-closer", "Edge: doubled edge"],
    "code": {"rc": CODE},
    "legend": [["active", "endpoints being checked"], ["good", "in the same group already"]],
    "nodes": NODES, "edges": [], "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
