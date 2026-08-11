"""Full-arc trace for Maximum Depth of Binary Tree. Trees have no wasteful brute
baseline to contrast, so the arc is: the rule -> DFS resolving bottom-up -> a
lopsided edge case. Mirrors the DFS in solution.py. Writes trace.json.
"""
import json
import os

XSTEP, YSTEP = 72, 82
frames = []


def add(**f):
    frames.append(f)


def layout(tree, root):
    """Assign x by in-order position, y by depth."""
    pos = {}
    counter = [0]

    def walk(nid, depth):
        if nid is None:
            return
        _, l, r = tree[nid]
        walk(l, depth + 1)
        pos[nid] = (counter[0] * XSTEP, depth * YSTEP)
        counter[0] += 1
        walk(r, depth + 1)

    walk(root, 0)
    nodes = [{"id": nid, "val": tree[nid][0], "x": pos[nid][0], "y": pos[nid][1]}
             for nid in tree]
    edges = []
    for nid, (_, l, r) in tree.items():
        if l is not None:
            edges.append([nid, l])
        if r is not None:
            edges.append([nid, r])
    return nodes, edges


#            3
#          /   \
#         9     20
#              /  \
#             15   7
TREE_A = {0: (3, 1, 2), 1: (9, None, None), 2: (20, 3, 4),
          3: (15, None, None), 4: (7, None, None)}
nodes_a, edges_a = layout(TREE_A, 0)

# ---- Act 0: the rule ----
add(act=0, nodes=nodes_a, edges=edges_a,
    note="The rule, straight from the definition: a node's depth is 1 + the depth "
    "of its deeper child. So we need the children's answers first.",
    active=[0], done={})
add(act=0, note="A leaf has no children. The deeper child is 0, so a leaf's depth "
    "is 1 + 0 = 1. That is the base case everything builds on.",
    active=[1], done={})

# ---- Act 1: DFS resolves bottom-up ----
done = {}


def depth(nid, tree, act):
    _, l, r = tree[nid]
    add(act=act, note=f"Visit node {tree[nid][0]}. Ask its children first, then take "
        f"1 + the deeper answer.", active=[nid], done=dict(done))
    dl = depth(l, tree, act) if l is not None else 0
    dr = depth(r, tree, act) if r is not None else 0
    d = 1 + max(dl, dr)
    done[nid] = d
    if l is None and r is None:
        msg = f"Node {tree[nid][0]} is a leaf -> depth 1."
    else:
        msg = f"Node {tree[nid][0]}: 1 + max(left {dl}, right {dr}) = {d}."
    add(act=act, note=msg, active=[nid], done=dict(done))
    return d


add(act=1, nodes=nodes_a, edges=edges_a,
    note="Now run it. Each node lights up when visited and shows its answer once "
    "both sides come back.", active=[0], done={})
ans = depth(0, TREE_A, 1)
add(act=1, note=f"The root's answer is the whole tree's depth: {ans}.",
    active=[], done=dict(done),
    banner=f"Maximum depth = {ans}  (longest root-to-leaf path)")

# ---- Act 2: lopsided edge case ----
#   1 -> 2 -> 3   (each has only a right child)
TREE_B = {0: (1, None, 1), 1: (2, None, 2), 2: (3, None, None)}
nodes_b, edges_b = layout(TREE_B, 0)
done = {}
add(act=2, nodes=nodes_b, edges=edges_b,
    note="Edge case: a lopsided tree, each node with only one child. No branching "
    "means depth just counts the nodes down the single path.", active=[0], done={})
ans2 = depth(0, TREE_B, 2)
add(act=2, note=f"Same rule, no branches: depth = number of nodes on the path = {ans2}. "
    f"(A single node would give 1; an empty tree, 0.)",
    active=[], done=dict(done), banner=f"Maximum depth = {ans2}")

trace = {"player": "tree",
         "title": "Maximum Depth - the rule, run bottom-up, then a lopsided tree",
         "acts": ["The rule", "DFS resolves bottom-up", "Edge case: lopsided"],
         "nodes": nodes_a, "edges": edges_a, "frames": frames}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
