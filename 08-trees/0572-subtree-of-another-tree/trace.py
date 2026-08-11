"""Full-arc trace for Subtree of Another Tree (tree renderer).
Arc: the rule (try same-tree at EVERY node) -> run it, find the match -> edge
case (a lone leaf is not a subtree when root's node still has children). Mirrors
is_subtree + is_same_tree in solution.py. Writes trace.json.
"""
import json
import os

XSTEP, YSTEP = 66, 82
frames = []

CODE = [
    "def is_subtree(root, sub):",
    "    if sub is None:  return True",
    "    if root is None: return False",
    "    if same(root, sub): return True   # match whole tree here",
    "    return (is_subtree(root.left, sub)",
    "            or is_subtree(root.right, sub))",
]


def add(**f):
    frames.append(f)


def layout(tree, root, x0=0):
    pos = {}
    counter = [x0]

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
    return nodes, edges, counter[0]


def sid(x):
    return "s%d" % x


def prefix(tree):
    out = {}
    for k, (v, l, r) in tree.items():
        out[sid(k)] = (v, sid(l) if l is not None else None,
                       sid(r) if r is not None else None)
    return out


def two(rt, rroot, st, sroot):
    rn, re, nxt = layout(rt, rroot, 0)
    sn, se, _ = layout(prefix(st), sid(sroot), nxt + 1)
    return rn + sn, re + se


def same(rt, rk, st, sk):
    """True if the tree rooted at rk in rt equals the sub rooted at sk in st."""
    if rk is None and sk is None:
        return True
    if rk is None or sk is None:
        return False
    if rt[rk][0] != st[sk][0]:
        return False
    return (same(rt, rt[rk][1], st, st[sk][1])
            and same(rt, rt[rk][2], st, st[sk][2]))


# root=[3,4,5,1,2], sub=[4,1,2]
ROOT = {0: (3, 1, 2), 1: (4, 3, 4), 2: (5, None, None),
        3: (1, None, None), 4: (2, None, None)}
SUB = {0: (4, 1, 2), 1: (1, None, None), 2: (2, None, None)}
nodes_a, edges_a = two(ROOT, 0, SUB, 0)
sub_ids = [sid(k) for k in SUB]

# Act 0: the rule
add(act=0, nodes=nodes_a, edges=edges_a, code="subtree", line=3,
    intro="at every node of root we ask: is the WHOLE tree here equal to sub?",
    invariant="a subtree must match sub all the way down, not just one value.",
    note="The rule: walk every node of root. At each, run the same-tree check "
    "against sub. A subtree means an entire tree below some node equals sub.",
    active=[0] + sub_ids, done={}, state=[["outer", "every root node"], ["inner", "same as sub?"]])
add(act=0, code="subtree", line=3,
    note="'The value 4 appears somewhere' is not enough — the shape and every "
    "value below must match sub exactly.",
    active=sub_ids, done={}, state=[["sub", "[4,1,2]"]])


def is_subtree(rt, rk, st, sroot, act, done):
    """Emit frames; try same() at each node of root. Returns bool."""
    if rk is None:
        return False
    rv = rt[rk][0]
    ok = same(rt, rk, st, sroot)
    add(act=act, code="subtree", line=3,
        note=f"Try node {rv} of root: does its whole tree equal sub? "
        + ("Yes!" if ok else "No — keep searching."),
        active=[rk] + [sid(k) for k in st],
        done=dict(done), state=[["trying at", rv], ["same as sub?", ok]])
    if ok:
        done[rk] = "match"
        add(act=act, code="subtree", line=3,
            note=f"The tree rooted at {rv} matches sub exactly -> found it.",
            active=[rk] + [sid(k) for k in st], done=dict(done),
            state=[["result", "True"]])
        return True
    done[rk] = "no"
    if is_subtree(rt, rt[rk][1], st, sroot, act, done):
        return True
    if is_subtree(rt, rt[rk][2], st, sroot, act, done):
        return True
    return False


# Act 1: run it
add(act=1, nodes=nodes_a, edges=edges_a, code="subtree", line=0,
    intro="each root node is tried in turn; the first exact match wins.",
    invariant="'no' badges mark nodes that failed the same-tree check.",
    note="Run it. Root 3 fails, then node 4's whole subtree equals [4,1,2].",
    active=[0], done={}, state=[["start", "root 3"]])
d1 = {}
r1 = is_subtree(ROOT, 0, SUB, 0, 1, d1)
add(act=1, code="subtree", line=3,
    note=f"Found sub hanging off node 4 -> {r1}.",
    active=[], done=dict(d1), state=[["is subtree?", r1]],
    banner=f"Is subtree = {r1}")

# Act 2: lone leaf is not a subtree here
ROOT2 = {0: (1, 1, None), 1: (2, None, None)}   # [1,2]
SUB2 = {0: (1, None, None)}                       # [1]
nodes_b, edges_b = two(ROOT2, 0, SUB2, 0)
add(act=2, nodes=nodes_b, edges=edges_b, code="subtree", line=3,
    intro="node 1 in root has a child, so it can't equal the lone leaf sub.",
    invariant="same-tree fails when one side has a child and the other doesn't.",
    note="Edge: root [1,2], sub [1]. Root's node 1 still has a left child, so its "
    "whole tree is not just a leaf -> no match there.",
    active=[0], done={}, state=[["sub", "[1] a lone leaf"]])
d2 = {}
r2 = is_subtree(ROOT2, 0, SUB2, 0, 2, d2)
add(act=2, code="subtree", line=5,
    note=f"Node 1 has a child (shape differs) and node 2's value is 2 not 1 -> "
    f"no node matches -> {r2}.",
    active=[], done=dict(d2), state=[["is subtree?", r2]],
    banner=f"Is subtree = {r2}")

trace = {
    "player": "tree",
    "title": "Subtree of Another Tree - try same-tree at every node, run it, then a lone leaf",
    "acts": ["The rule", "Run: find the match", "Edge: a lone leaf"],
    "code": {"subtree": CODE},
    "legend": [["active", "trying here / sub"], ["good", "match / decided"]],
    "nodes": nodes_a, "edges": edges_a, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
