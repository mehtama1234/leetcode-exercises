"""Full-arc tree trace for Subsets (backtracking decision tree).

Backtracking has no wasteful brute baseline to beat — the tree IS the work — so
the arc is: the rule (one binary choice per element) -> run the DFS and watch the
path walk the tree, leaves collecting subsets -> an edge case (empty input).
We precompute every node's x,y in Python for nums=[1,2,3]. Each node is a
decision: the root is "start", left child = leave nums[i] out, right child = take
it. A leaf (i == n) is one finished subset. Mirrors backtrack() in solution.py.
"""
import json
import os

XSTEP, YSTEP = 60, 84
frames = []

CODE = [
    "def backtrack(i):",
    "    if i == n:",
    "        result.append(path[:])",
    "        return",
    "    backtrack(i + 1)      # leave nums[i] out",
    "    path.append(nums[i])  # choose",
    "    backtrack(i + 1)      # explore",
    "    path.pop()            # un-choose",
]


def add(**f):
    frames.append(f)


def build_tree(nums):
    """Enumerate the include/exclude decision tree; assign x,y by in-order sweep.

    node = {id, val, x, y, path (subset here), leaf?, took? (edge label)}.
    Returns (nodes, edges, order) where order is the DFS visit sequence of ids
    matching the solution's traversal (leave-out branch first, then take).
    """
    n = len(nums)
    nodes = {}          # id -> dict
    edges = []
    order = []          # ids in DFS order (pre-order, left=exclude first)
    counter = [0]       # in-order x slot
    nid = [0]

    def label(path):
        return "{" + ",".join(str(x) for x in path) + "}" if path else "{}"

    def make(i, path, took):
        my = nid[0]; nid[0] += 1
        node = {"i": i, "path": list(path), "leaf": i == n, "took": took,
                "val": label(path), "x": 0, "y": i * YSTEP}
        nodes[my] = node
        order.append(my)
        if i == n:
            node["x"] = counter[0] * XSTEP; counter[0] += 1
            return my
        # left = exclude (backtrack i+1 with same path)
        left = make(i + 1, path, False)
        edges.append((my, left, "skip"))
        # this node's x sits between its children groups
        node["x"] = counter[0] * XSTEP; counter[0] += 1
        # right = include
        path.append(nums[i])
        right = make(i + 1, path, True)
        path.pop()
        edges.append((my, right, "take " + str(nums[i])))
        return my

    make(0, [], None)
    return nodes, edges, order


def render_nodes(nodes):
    return [{"id": k, "val": v["val"], "x": v["x"], "y": v["y"]} for k, v in nodes.items()]


def render_edges(edges):
    return [[a, b] for a, b, _ in edges]


def path_to(nodes, edges, target):
    """ids on the root->target path, for the `active` highlight."""
    parent = {}
    for a, b, _ in edges:
        parent[b] = a
    chain = [target]
    while chain[-1] in parent:
        chain.append(parent[chain[-1]])
    return chain[::-1]


NUMS = [1, 2, 3]
nodes, edges, order = build_tree(NUMS)
NODES = render_nodes(nodes)
EDGES = render_edges(edges)

# ---- Act 0: the rule ----
add(act=0, nodes=NODES, edges=EDGES, code="backtrack", line=0,
    intro="each level is one element; going left leaves it out, right takes it.",
    invariant="depth = index i; a leaf at the bottom row is one finished subset.",
    note="The rule: at element i make one binary choice — leave it out (left) or "
    "take it (right) — then move to i+1. The whole tree of choices has one leaf "
    "per subset.",
    active=[0], done={}, state=[["elements", str(NUMS)], ["choice", "out / take"]])
add(act=0, code="backtrack", line=1,
    note="The bottom row (i == 3, past the last element) is where a path becomes a "
    "complete subset — we copy the path into the result there.",
    active=[0], done={}, state=[["leaves", "2^3 = 8"], ["= subsets", 8]])

# ---- Act 1: run the DFS ----
done = {}
subsets_found = []
add(act=1, nodes=NODES, edges=EDGES, code="backtrack", line=0,
    intro="the active path is the current line of choices; leaves light green.",
    invariant="a green leaf holds exactly the elements taken on the way down.",
    note="Run it. The highlighted path is the choices made so far; each time we "
    "reach the bottom we record that subset.",
    active=[0], done={}, state=[["found", 0]])
for oid in order:
    nd = nodes[oid]
    active = path_to(nodes, edges, oid)
    if nd["leaf"]:
        done[oid] = nd["val"]
        subsets_found.append(nd["val"])
        add(act=1, code="backtrack", line=2,
            note=f"Bottom of a path -> record the subset {nd['val']}. "
                 f"({len(subsets_found)} of 8 so far.)",
            active=active, done=dict(done),
            state=[["subset", nd["val"]], ["found", len(subsets_found)]])
    else:
        took = "" if nd["took"] is None else ("took " + str(NUMS[nd["i"] - 1]))
        add(act=1, code="backtrack", line=(0 if nd["took"] is None else (6 if nd["took"] else 4)),
            note=(f"At element index {nd['i']}: decide out vs take. Path so far {nd['val']}."
                  if nd["took"] is None else
                  f"Went {'right (take)' if nd['took'] else 'left (leave out)'}: "
                  f"path is now {nd['val']}."),
            active=active, done=dict(done),
            state=[["at index", nd["i"]], ["path", nd["val"]], ["found", len(subsets_found)]])
add(act=1, code="backtrack", line=2,
    note=f"Every leaf visited -> all 8 subsets collected: the power set.",
    active=[], done=dict(done),
    state=[["subsets", 8]],
    banner="8 subsets = 2^3, the full power set")

# ---- Act 2: edge case — empty input ----
NUMS_E = []
nodes_e, edges_e, order_e = build_tree(NUMS_E)
NODES_E = render_nodes(nodes_e)
EDGES_E = render_edges(edges_e)
add(act=2, nodes=NODES_E, edges=EDGES_E, code="backtrack", line=1,
    intro="with no elements the tree is a single node — already a leaf.",
    invariant="the empty path is still a valid subset.",
    note="Edge case: nums = []. There are no choices to make, so the root is "
    "immediately the bottom (i == n == 0).",
    active=[0], done={}, state=[["elements", "[]"], ["choice", "none"]])
add(act=2, code="backtrack", line=2,
    note="The single leaf records the empty subset {}. So even [] yields one "
    "subset — the empty set.",
    active=[0], done={0: "{}"},
    state=[["subset", "{}"], ["found", 1]],
    banner="Empty input -> exactly one subset: {}")

trace = {
    "player": "tree",
    "title": "Subsets — one binary choice per element, walked as a decision tree",
    "acts": ["The rule", "Walk the decision tree", "Edge case: empty input"],
    "code": {"backtrack": CODE},
    "legend": [["active", "current path"], ["good", "finished subset (leaf)"]],
    "nodes": NODES, "edges": EDGES, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
