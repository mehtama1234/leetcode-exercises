"""Full-arc tree trace for Permutations (backtracking decision tree).

Backtracking has no wasteful brute baseline to beat — the tree IS the work — so
the arc is: the rule (pick any unused number next) -> run the DFS and watch the
path walk the tree, leaves collecting orderings -> an edge case (single element).
We precompute every node's x,y in Python for nums=[1,2,3]. Each node picks one
still-unused number; its children are the remaining unused numbers. Depth =
len(path). A leaf (len(path) == n) is one complete permutation. Mirrors
backtrack() with the used[] mask in solution.py.
"""
import json
import os
import math

XSTEP, YSTEP = 58, 84
frames = []

CODE = [
    "def backtrack():",
    "    if len(path) == n:",
    "        result.append(path[:])",
    "        return",
    "    for i in range(n):",
    "        if used[i]:",
    "            continue          # already placed",
    "        used[i] = True        # choose",
    "        path.append(nums[i])",
    "        backtrack()           # explore",
    "        path.pop()            # un-choose",
    "        used[i] = False",
]


def add(**f):
    frames.append(f)


def build_tree(nums):
    """Enumerate the permutation decision tree; assign x,y by in-order sweep.

    node = {id, val, x, y, path, leaf?, picked (the number chosen to reach here)}.
    At each node we branch over numbers still unused, in input order — exactly the
    loop in the solution. Returns (nodes, edges, order) with order the DFS visit
    sequence of ids.
    """
    n = len(nums)
    nodes = {}
    edges = []
    order = []
    counter = [0]   # in-order x slot (leaves fill left->right)
    nid = [0]

    def label(path):
        return ",".join(str(x) for x in path) if path else "start"

    def make(path, used, picked):
        my = nid[0]; nid[0] += 1
        leaf = len(path) == n
        node = {"path": list(path), "leaf": leaf, "picked": picked,
                "val": label(path), "x": 0, "y": len(path) * YSTEP}
        nodes[my] = node
        order.append(my)
        if leaf:
            node["x"] = counter[0] * XSTEP; counter[0] += 1
            return my
        first_child = True
        for i in range(n):
            if used[i]:
                continue
            used[i] = True
            path.append(nums[i])
            child = make(path, used, nums[i])
            path.pop()
            used[i] = False
            edges.append((my, child, "take " + str(nums[i])))
            if first_child:
                # place this node's x once its first child column is known
                node["x"] = counter[0] * XSTEP - XSTEP  # sits above child span; refined below
                first_child = False
        # center this internal node over its children
        kids = [c for (a, c, _) in edges if a == my]
        node["x"] = sum(nodes[c]["x"] for c in kids) / len(kids)
        return my

    make([], [False] * n, None)
    return nodes, edges, order


def render_nodes(nodes):
    return [{"id": k, "val": v["val"], "x": v["x"], "y": v["y"]} for k, v in nodes.items()]


def render_edges(edges):
    return [[a, b] for a, b, _ in edges]


def path_to(edges, target):
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
add(act=0, nodes=NODES, edges=EDGES, code="backtrack", line=4,
    intro="each level places one more number; branches are the numbers still free.",
    invariant="depth = how many placed; a leaf uses every number exactly once.",
    note="The rule: at each step pick any number not yet placed, then recurse. "
    "Order matters and every number must be used, so the tree branches over "
    "whatever is still available.",
    active=[0], done={}, state=[["numbers", str(NUMS)], ["choice", "any unused"]])
add(act=0, code="backtrack", line=1,
    note="The root has 3 choices, the next level 2, then 1 — so 3·2·1 = 6 leaves. "
    "Each leaf, where len(path) == n, is one complete ordering.",
    active=[0], done={}, state=[["leaves", "3! = 6"], ["= permutations", 6]])

# ---- Act 1: run the DFS ----
done = {}
perms_found = []
add(act=1, nodes=NODES, edges=EDGES, code="backtrack", line=0,
    intro="the active path is the numbers placed so far; leaves light green.",
    invariant="a green leaf spells a full ordering of all the numbers.",
    note="Run it. The highlighted path shows the numbers placed so far; each time "
    "the path is full we record that permutation.",
    active=[0], done={}, state=[["found", 0]])
for oid in order:
    nd = nodes[oid]
    active = path_to(edges, oid)
    if nd["leaf"]:
        done[oid] = nd["val"]
        perms_found.append(nd["path"])
        add(act=1, code="backtrack", line=2,
            note=f"Path is full -> record the permutation [{nd['val']}]. "
                 f"({len(perms_found)} of 6 so far.)",
            active=active, done=dict(done),
            state=[["permutation", nd["val"]], ["found", len(perms_found)]])
    elif nd["picked"] is None:
        add(act=1, code="backtrack", line=4,
            note="Start with an empty path. Every number is still free to place.",
            active=active, done=dict(done),
            state=[["placed", 0], ["found", len(perms_found)]])
    else:
        add(act=1, code="backtrack", line=8,
            note=f"Place {nd['picked']} (it was unused) -> path is now [{nd['val']}]. "
                 f"{3 - len(nd['path'])} number(s) still free.",
            active=active, done=dict(done),
            state=[["just placed", nd["picked"]], ["path", nd["val"]],
                   ["found", len(perms_found)]])
add(act=1, code="backtrack", line=2,
    note="Every path walked to the bottom -> all 6 orderings collected.",
    active=[], done=dict(done),
    state=[["permutations", 6]],
    banner="6 permutations = 3!, every ordering of 1,2,3")

# sanity: our tree's leaves must match the real algorithm's output set + count
assert len(perms_found) == math.factorial(len(NUMS)) == 6
assert {tuple(p) for p in perms_found} == {
    (1, 2, 3), (1, 3, 2), (2, 1, 3), (2, 3, 1), (3, 1, 2), (3, 2, 1)}, perms_found

# ---- Act 2: edge case — single element ----
NUMS_E = [7]
nodes_e, edges_e, order_e = build_tree(NUMS_E)
NODES_E = render_nodes(nodes_e)
EDGES_E = render_edges(edges_e)
add(act=2, nodes=NODES_E, edges=EDGES_E, code="backtrack", line=4,
    intro="with one number there is a single choice, then the path is full.",
    invariant="n! collapses: 1! = 1, and 0! = 1 too.",
    note="Edge case: nums = [7]. The root has exactly one number to place, so the "
    "tree is a single branch down to one leaf.",
    active=[0], done={}, state=[["numbers", "[7]"], ["choices", 1]])
leaf_e = order_e[-1]
add(act=2, code="backtrack", line=2,
    note="Place 7 -> path [7] is full -> record it. So [7] yields one permutation. "
    "(Empty [] also yields one: the empty ordering, since 0! = 1.)",
    active=path_to(edges_e, leaf_e), done={leaf_e: "7"},
    state=[["permutation", "7"], ["found", 1]],
    banner="Single element -> exactly one permutation: [7]")

trace = {
    "player": "tree",
    "title": "Permutations — pick any unused number next, walked as a decision tree",
    "acts": ["The rule", "Walk the decision tree", "Edge case: single element"],
    "code": {"backtrack": CODE},
    "legend": [["active", "current path"], ["good", "finished permutation (leaf)"]],
    "nodes": NODES, "edges": EDGES, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
