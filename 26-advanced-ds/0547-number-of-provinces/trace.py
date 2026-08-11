"""Rich full-arc trace for Number of Provinces (tree renderer, Union-Find forest).
No wasteful baseline to race, so the arc is: the rule (start with n singleton
groups, each merge drops the count by one) -> run the merges over a connected chain,
watching the forest fuse -> an edge case with an isolated city. Nodes are cities;
edges are parent pointers; a node lights when it is a root, and merges redirect one
root under another. Mirrors UnionFind + findCircleNum in solution.py. Writes trace.json.
"""
import json
import os

# 4-city chain: 0-1-2-3 all in one province, plus we reuse the classic 3-city edge.
chain = [
    [1, 1, 0, 0],
    [1, 1, 1, 0],
    [0, 1, 1, 1],
    [0, 0, 1, 1],
]
frames = []

CODE = [
    "uf = UnionFind(n)          # count = n singleton groups",
    "for i in range(n):",
    "    for j in range(i+1, n):",
    "        if isConnected[i][j]:",
    "            uf.union(i, j)  # merge -> count -= 1 if new",
    "return uf.count",
]

XSTEP = 90


def add(**f):
    frames.append(f)


class UF:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.count = n

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
        self.count -= 1
        return True, ra, rb


def scene(uf, n, y=60):
    """Nodes in a row; parent-pointer edges. Root nodes get highlighted separately."""
    nodes = [{"id": i, "val": i, "x": i * XSTEP, "y": y} for i in range(n)]
    edges = [[uf.parent[i], i] for i in range(n) if uf.parent[i] != i]
    roots = [i for i in range(n) if uf.parent[i] == i]
    return nodes, edges, roots


# ---- Act 0: the rule ----
n = 4
uf = UF(n)
nodes, edges, roots = scene(uf, n)
add(act=0, nodes=nodes, edges=edges, code="uf", line=0,
    intro="each city starts as its own group; the group count starts at n.",
    invariant="number of provinces = current number of disjoint groups.",
    note=f"Number of provinces = connected components. Start with {n} singleton groups. "
    "Every merge of two DIFFERENT groups drops the count by one.",
    active=roots, done={i: "group" for i in roots}, state=[["groups", uf.count]])

# ---- Act 1: run the merges ----
add(act=1, nodes=nodes, edges=edges, code="uf", line=4,
    intro="each edge unions two cities; watch roots redirect and the count fall.",
    invariant="a merge only lowers the count when the two roots differ.",
    note="Scan the upper triangle. For each connection, union the two cities.",
    active=roots, done={}, state=[["groups", uf.count]])
for i in range(n):
    for j in range(i + 1, n):
        if chain[i][j] == 1:
            ra_before, rb_before = uf.find(i), uf.find(j)
            add(act=1, code="uf", line=3,
                note=f"cities {i} and {j} are connected. Their roots are {ra_before} and "
                     f"{rb_before}.",
                nodes=nodes, edges=[[uf.parent[k], k] for k in range(n) if uf.parent[k] != k],
                active=[ra_before, rb_before],
                done={r: "root" for r in range(n) if uf.parent[r] == r},
                state=[["union", f"{i},{j}"], ["roots", f"{ra_before},{rb_before}"],
                       ["groups", uf.count]])
            merged, ra, rb = uf.union(i, j)
            new_edges = [[uf.parent[k], k] for k in range(n) if uf.parent[k] != k]
            add(act=1, code="uf", line=4,
                note=(f"Different groups: attach root {rb} under root {ra}. Groups "
                      f"{uf.count + 1} -> {uf.count}." if merged
                      else f"Same group already: nothing merges, count stays {uf.count}."),
                nodes=nodes, edges=new_edges,
                active=[ra],
                done={r: "root" for r in range(n) if uf.parent[r] == r},
                state=[["merged", merged], ["groups", uf.count]])
add(act=1, code="uf", line=5,
    note=f"All cities fused into one tree -> {uf.count} province.",
    nodes=nodes, edges=[[uf.parent[k], k] for k in range(n) if uf.parent[k] != k],
    active=[uf.find(0)], done={uf.find(0): "root"},
    state=[["provinces", uf.count]], banner=f"Chain of 4 -> {uf.count} province")

# ---- Act 2: edge case, an isolated city ----
ex = [[1, 1, 0], [1, 1, 0], [0, 0, 1]]  # 0-1 joined, 2 alone -> 2 provinces
m = 3
uf2 = UF(m)
nodes2, edges2, roots2 = scene(uf2, m)
add(act=2, nodes=nodes2, edges=edges2, code="uf", line=0,
    intro="one connection, one isolated city -> two provinces.",
    invariant="a city with no connections stays its own province.",
    note="Edge case: cities 0 and 1 connected, city 2 alone. One merge, one lonely group.",
    active=roots2, done={i: "root" for i in roots2}, state=[["groups", uf2.count]])
uf2.union(0, 1)
add(act=2, code="uf", line=4,
    note="Union 0 and 1: count 3 -> 2. City 2 has no connection, so it stays its own "
    "province.",
    nodes=nodes2, edges=[[uf2.parent[k], k] for k in range(m) if uf2.parent[k] != k],
    active=[uf2.find(0), 2], done={r: "root" for r in range(m) if uf2.parent[r] == r},
    state=[["provinces", uf2.count]], banner=f"2 groups -> {uf2.count} provinces")

trace = {
    "player": "tree",
    "title": "Number of Provinces - Union-Find forest, count the groups",
    "acts": ["The rule", "Merge the chain", "Edge: an isolated city"],
    "code": {"uf": CODE},
    "legend": [["active", "roots being merged"], ["good", "current group root"]],
    "nodes": nodes, "edges": edges, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
