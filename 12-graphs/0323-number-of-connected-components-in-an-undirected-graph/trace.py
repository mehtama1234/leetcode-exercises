"""Rich full-arc trace for Number of Connected Components (tree renderer as a graph).
Arc: the rule (start with n clubs; each merging edge drops the count by 1) ->
run Union-Find over edges -> a redundant-edge edge case that changes nothing.
Mirrors the union-find in solution.py. Node x,y computed here; badges show each
node's current root (club). Writes trace.json.
"""
import json
import os

frames = []

CODE = [
    "parent = list(range(n)); count = n   # n lonely clubs",
    "def find(x):                          # x's club root",
    "    while parent[x] != x: x = parent[x]",
    "    return x",
    "for a, b in edges:",
    "    ra, rb = find(a), find(b)",
    "    if ra == rb: continue             # same club: redundant",
    "    parent[rb] = ra                   # fuse two clubs",
    "    count -= 1",
    "return count",
]


def add(**f):
    frames.append(f)


def nodes_edges(pos, edges):
    nodes = [{"id": i, "val": i, "x": pos[i][0], "y": pos[i][1]} for i in pos]
    return nodes, [list(e) for e in edges]


# n=5, edges 0-1,1-2,3-4 -> two components {0,1,2} and {3,4}
POS_A = {0: (0, 0), 1: (110, 60), 2: (220, 0), 3: (0, 150), 4: (140, 150)}
N_A = 5
EDGES_A = [[0, 1], [1, 2], [3, 4]]
nodes_a, edges_a = nodes_edges(POS_A, EDGES_A)


class UF:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.count = n

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        self.count -= 1
        return True

    def roots(self, n):
        return {i: self.find(i) for i in range(n)}


# ---- Act 0: the rule ----
add(act=0, nodes=nodes_a, edges=[], code="uf", line=0,
    intro="every node starts as its own club; the badge is its club's root.",
    invariant="components = clubs; only a real merge lowers the count.",
    note="Start with n isolated nodes = n components. Each edge either joins two "
    "different clubs (count drops by 1) or connects two already together (no change).",
    active=[], done={i: i for i in range(N_A)},
    state=[["nodes", N_A], ["components", N_A]])

# ---- Act 1: run union-find ----
uf = UF(N_A)
add(act=1, nodes=nodes_a, edges=[], code="uf", line=4,
    intro="watch the count drop only when an edge fuses two distinct clubs.",
    invariant="badges share a value exactly when nodes are in the same club.",
    note="Process the edges one at a time. Draw each edge, check if its ends are "
    "already in the same club, and merge if not.",
    active=[], done=uf.roots(N_A), state=[["components", uf.count]])
drawn = []
for a, b in EDGES_A:
    drawn.append([a, b])
    ra, rb = uf.find(a), uf.find(b)
    same = ra == rb
    add(act=1, code="uf", line=5, edges=[list(e) for e in drawn],
        note=f"Edge {a}-{b}: root({a})={ra}, root({b})={rb}. " +
        ("Same club — redundant, count unchanged." if same
         else "Different clubs — fuse them, count drops by 1."),
        active=[a, b], done=uf.roots(N_A),
        state=[["edge", f"{a}-{b}"], ["merge?", "no" if same else "yes"],
               ["components", uf.count]])
    uf.union(a, b)
    add(act=1, code="uf", line=8 if not same else 6, edges=[list(e) for e in drawn],
        note=(f"Merged: {a} and {b} now share a root. Components = {uf.count}."
              if not same else "No change."),
        active=[a, b], done=uf.roots(N_A),
        state=[["components", uf.count]])
add(act=1, code="uf", line=9, edges=edges_a,
    note=f"All edges processed. Two clubs remain: {{0,1,2}} and {{3,4}}. "
    f"Components = {uf.count}.",
    active=[], done=uf.roots(N_A), state=[["components", uf.count]],
    banner=f"Connected components = {uf.count}")

# ---- Act 2: redundant edge edge case ----
POS_B = {0: (0, 0), 1: (140, 0), 2: (70, 130)}
N_B = 3
EDGES_B = [[0, 1], [1, 2], [0, 2]]  # triangle: last edge is redundant
nodes_b, edges_b = nodes_edges(POS_B, EDGES_B)
uf = UF(N_B)
add(act=2, nodes=nodes_b, edges=[], code="uf", line=4,
    intro="the third edge closes a triangle — both ends already share a root.",
    invariant="an edge inside one club never lowers the count.",
    note="Edge case: a triangle 0-1-2. The first two edges merge everything into one "
    "club; the third edge is redundant.",
    active=[], done={i: i for i in range(N_B)}, state=[["components", N_B]])
drawn = []
for a, b in EDGES_B:
    drawn.append([a, b])
    ra, rb = uf.find(a), uf.find(b)
    same = ra == rb
    merged = uf.union(a, b)
    add(act=2, code="uf", line=6 if same else 8, edges=[list(e) for e in drawn],
        note=f"Edge {a}-{b}: " + ("already in the same club — redundant, count stays "
                                  f"{uf.count}." if same else
                                  f"different clubs, merge. Components = {uf.count}."),
        active=[a, b], done=uf.roots(N_B),
        state=[["edge", f"{a}-{b}"], ["redundant?", "yes" if same else "no"],
               ["components", uf.count]])
add(act=2, code="uf", line=9, edges=edges_b,
    note=f"Three edges but only two did real merging — the triangle's closing edge "
    f"changed nothing. One component.",
    active=[], done=uf.roots(N_B), state=[["components", uf.count]],
    banner=f"Triangle -> {uf.count} component (redundant edge ignored)")

trace = {
    "player": "tree",
    "title": "Connected Components - n clubs; each merging edge drops the count",
    "acts": ["The rule: n clubs", "Run Union-Find", "Edge: redundant edge"],
    "code": {"uf": CODE},
    "legend": [["active", "edge's endpoints"], ["good", "club root (badge)"]],
    "nodes": nodes_a, "edges": [], "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
