"""Full-arc trace for Validate Binary Search Tree (tree renderer).
Arc: the naive parent-only check fails -> the fix is an inherited (low, high)
range -> run it on a valid tree -> run it on a sneaky invalid one. Mirrors
valid() in solution.py. Writes trace.json.
"""
import json
import os

XSTEP, YSTEP = 78, 82
INF = float("inf")
frames = []

CODE = [
    "def valid(node, low, high):",
    "    if node is None:",
    "        return True",
    "    if not (low < node.val < high):",
    "        return False",
    "    return (valid(node.left, low, node.val)",
    "            and valid(node.right, node.val, high))",
]


def add(**f):
    frames.append(f)


def layout(tree, root):
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


def rng(low, high):
    lo = "-inf" if low == -INF else low
    hi = "+inf" if high == INF else high
    return f"({lo}, {hi})"


# BAD tree: [5,4,6,null,null,3,7]. 3 sits left-of-6 (ok vs parent) but < 5 (bad).
TREE_BAD = {0: (5, 1, 2), 1: (4, None, None), 2: (6, 3, 4),
            3: (3, None, None), 4: (7, None, None)}
nodes_bad, edges_bad = layout(TREE_BAD, 0)

# Act 0: the naive check is not enough
add(act=0, nodes=nodes_bad, edges=edges_bad, code="valid", line=3,
    intro="checking only 'left < node < right' at each parent misses a violator.",
    invariant="a value must beat EVERY ancestor, not just its parent.",
    note="Naive idea: at each node check left child < node < right child. Here "
    "6's children 3 and 7 look fine against 6.",
    active=[2], done={}, state=[["parent check", "3 < 6 < 7 ok"]])
add(act=0, code="valid", line=3,
    note="But 3 is in the RIGHT subtree of the root 5, so it must be > 5. The "
    "parent-only check never sees that -> the naive rule is wrong.",
    active=[3], done={0: "5", 3: "!"}, state=[["hidden rule", "3 must be > 5"]])

# Act 1: the fix — carry a (low, high) range
TREE_OK = {0: (5, 1, 2), 1: (3, 3, 4), 2: (8, 5, 6),
           3: (1, None, None), 4: (4, None, None),
           5: (7, None, None), 6: (9, None, None)}
nodes_ok, edges_ok = layout(TREE_OK, 0)


def valid(nid, tree, low, high, act, done):
    """DFS carrying an open (low, high) range; emits frames. Returns bool."""
    if nid is None:
        return True
    v = tree[nid][0]
    inside = low < v < high
    add(act=act, code="valid", line=3,
        note=f"Node {v}: allowed range {rng(low, high)}. "
        + (f"{v} fits." if inside else f"{v} is OUT of range -> invalid."),
        active=[nid], done=dict(done),
        state=[["node", v], ["range", rng(low, high)],
               ["fits?", inside]])
    if not inside:
        done[nid] = "x"
        add(act=act, code="valid", line=4,
            note=f"{v} breaks its range {rng(low, high)} -> the tree is not a BST.",
            active=[nid], done=dict(done), state=[["result", "False"]])
        return False
    _, l, r = tree[nid]
    # left tightens the high bound to v; right raises the low bound to v
    if not valid(l, tree, low, v, act, done):
        return False
    if not valid(r, tree, v, high, act, done):
        return False
    done[nid] = "ok"
    add(act=act, code="valid", line=5,
        note=f"{v} fits and both subtrees are valid under their tightened ranges.",
        active=[nid], done=dict(done),
        state=[["node", v], ["subtree", "valid"]])
    return True


add(act=1, nodes=nodes_ok, edges=edges_ok, code="valid", line=0,
    intro="each node inherits a range; going left lowers the ceiling, right lifts the floor.",
    invariant="a node is valid only if it sits strictly inside its inherited range.",
    note="The fix: carry an allowed (low, high) range down. Root starts with "
    "(-inf, +inf). Run it on a valid BST.",
    active=[0], done={}, state=[["start", "range (-inf, +inf)"]])
d1 = {}
r1 = valid(0, TREE_OK, -INF, INF, 1, d1)
add(act=1, code="valid", line=6,
    note=f"Every node stayed inside its inherited range -> valid BST: {r1}.",
    active=[], done=dict(d1), state=[["valid BST?", r1]],
    banner=f"Valid BST = {r1}")

# Act 2: the sneaky invalid tree caught
add(act=2, nodes=nodes_bad, edges=edges_bad, code="valid", line=0,
    intro="the 3 that fooled the naive check now inherits range (5, 6) and fails.",
    invariant="the inherited floor from ancestor 5 is what catches the violator.",
    note="Edge: run the range check on the sneaky tree. Going right at root 5 "
    "raises the floor to 5, so 6's left child must be > 5.",
    active=[0], done={}, state=[["start", "range (-inf, +inf)"]])
d2 = {}
r2 = valid(0, TREE_BAD, -INF, INF, 2, d2)
add(act=2, code="valid", line=4,
    note=f"Node 3 needed (5, 6) but 3 < 5 -> caught -> not a BST: {r2}.",
    active=[], done=dict(d2), state=[["valid BST?", r2]],
    banner=f"Valid BST = {r2}")

trace = {
    "player": "tree",
    "title": "Validate BST - why parent-only fails, the range fix, valid + invalid runs",
    "acts": ["Naive check fails", "The range fix (valid tree)", "Edge: sneaky invalid"],
    "code": {"valid": CODE},
    "legend": [["active", "checking now"], ["good", "in range / valid"]],
    "nodes": nodes_bad, "edges": edges_bad, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
