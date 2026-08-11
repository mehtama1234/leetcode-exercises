"""Full-arc trace for Invert Binary Tree (tree renderer).
Arc: the rule -> invert bottom-up (children swap at every node) -> edge cases
(single node, lopsided). Mirrors invert_tree in solution.py. Writes trace.json.
"""
import json
import os

XSTEP, YSTEP = 72, 82
frames = []

CODE = [
    "def invert(node):",
    "    if node is None:",
    "        return None",
    "    node.left, node.right = (invert(node.right),",
    "                             invert(node.left))",
    "    return node",
]


def add(**f):
    frames.append(f)


def layout(tree, root):
    """In-order x layout. tree: {id: (val, left, right)}."""
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


# TREE_A = [4,2,7,1,3,6,9]
TREE_A = {0: (4, 1, 2), 1: (2, 3, 4), 2: (7, 5, 6),
          3: (1, None, None), 4: (3, None, None),
          5: (6, None, None), 6: (9, None, None)}
nodes_a, edges_a = layout(TREE_A, 0)

# Act 0: the rule
add(act=0, nodes=nodes_a, edges=edges_a, code="invert", line=3,
    intro="at each node the two children trade places, all the way down.",
    invariant="a node is 'done' only once both its subtrees are inverted.",
    note="The rule: the mirror of a node is a node whose left is the mirror of "
    "the old right, and whose right is the mirror of the old left.",
    active=[0], done={}, state=[["rule", "swap left <-> right"]])
add(act=0, code="invert", line=1,
    note="Base case: an empty spot is already its own mirror -> return None.",
    active=[], done={}, state=[["empty", "its own mirror"]])


def invert(nid, tree, act, done):
    """Post-order: invert children first, then mark this node swapped."""
    _, l, r = tree[nid]
    add(act=act, code="invert", line=3,
        note=f"Enter node {tree[nid][0]}. Invert its two subtrees first.",
        active=[nid], done=dict(done), state=[["visiting", tree[nid][0]]])
    if l is not None:
        invert(l, tree, act, done)
    if r is not None:
        invert(r, tree, act, done)
    leaf = l is None and r is None
    done[nid] = "M"
    add(act=act, code="invert", line=5,
        note=(f"Leaf {tree[nid][0]}: nothing below to swap -> done."
              if leaf else
              f"Node {tree[nid][0]}: swap its (now-inverted) children -> done."),
        active=[nid], done=dict(done),
        state=[["node", tree[nid][0]], ["state", "mirrored"]])


# Act 1: run it
add(act=1, nodes=nodes_a, edges=edges_a, code="invert", line=0,
    intro="each node gets its 'M' badge only after both sides below are flipped.",
    invariant="the swap happens once, bottom-up, at every node.",
    note="Run it on [4,2,7,1,3,6,9]. Watch the swap ripple up from the leaves.",
    active=[0], done={}, state=[["start", "root 4"]])
d1 = {}
invert(0, TREE_A, 1, d1)
add(act=1, code="invert", line=5,
    note="Every node swapped its children -> the tree is now [4,7,2,9,6,3,1].",
    active=[], done=dict(d1), state=[["result", "[4,7,2,9,6,3,1]"]],
    banner="Inverted: [4,7,2,9,6,3,1]")

# Act 2: single node
TREE_B = {0: (1, None, None)}
nodes_b, edges_b = layout(TREE_B, 0)
add(act=2, nodes=nodes_b, edges=edges_b, code="invert", line=1,
    intro="a lone node has no children, so mirroring changes nothing.",
    invariant="the base cases (empty, single node) return unchanged.",
    note="Edge: a single node is its own mirror. Nothing to swap.",
    active=[0], done={}, state=[["shape", "one node"]])
d2 = {}
invert(0, TREE_B, 2, d2)
add(act=2, code="invert", line=5,
    note="No children to swap -> the node is returned as-is: [1].",
    active=[], done=dict(d2), state=[["result", "[1]"]],
    banner="Inverted: [1]")

# Act 3: lopsided (mirror flips the lean)
TREE_C = {0: (1, 1, None), 1: (2, 2, None), 2: (3, None, None)}
nodes_c, edges_c = layout(TREE_C, 0)
add(act=3, nodes=nodes_c, edges=edges_c, code="invert", line=3,
    intro="a left-leaning chain becomes a right-leaning chain.",
    invariant="the same rule flips each single child to the other side.",
    note="Edge: a left-leaning chain. Inverting sends every child to the right, "
    "so the whole tree leans the other way.",
    active=[0], done={}, state=[["shape", "left chain"]])
d3 = {}
invert(0, TREE_C, 3, d3)
add(act=3, code="invert", line=5,
    note="Each left child moved right -> [1,null,2,null,3] leans right now.",
    active=[], done=dict(d3), state=[["result", "right chain"]],
    banner="Inverted: lean flipped left -> right")

trace = {
    "player": "tree",
    "title": "Invert Binary Tree - the rule, run bottom-up, then edge cases",
    "acts": ["The rule", "Run: swap bottom-up", "Edge: single node", "Edge: lopsided"],
    "code": {"invert": CODE},
    "legend": [["active", "visiting now"], ["good", "mirrored"]],
    "nodes": nodes_a, "edges": edges_a, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
