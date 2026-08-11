"""Full-arc trace for Lowest Common Ancestor of a BST (tree renderer).
Arc: the rule (BST order tells you which way both targets lie) -> run it when
they split -> edge case (one target IS an ancestor of the other). Mirrors
lowest_common_ancestor in solution.py. Writes trace.json.
"""
import json
import os

XSTEP, YSTEP = 66, 82
frames = []

CODE = [
    "node = root",
    "while node:",
    "    if p.val > node.val and q.val > node.val:",
    "        node = node.right      # both bigger -> right",
    "    elif p.val < node.val and q.val < node.val:",
    "        node = node.left       # both smaller -> left",
    "    else:",
    "        return node            # they split here",
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


# [6,2,8,0,4,7,9,null,null,3,5]
TREE = {0: (6, 1, 2), 1: (2, 3, 4), 2: (8, 5, 6),
        3: (0, None, None), 4: (4, 7, 8), 5: (7, None, None),
        6: (9, None, None), 7: (3, None, None), 8: (5, None, None)}
nodes_a, edges_a = layout(TREE, 0)

# id lookup by value for marking targets
by_val = {tree_v: nid for nid, (tree_v, _, _) in TREE.items()}

# Act 0: the rule
add(act=0, nodes=nodes_a, edges=edges_a, code="lca", line=2,
    intro="the BST order alone points you toward both targets — no full search.",
    invariant="the LCA is the first node where the two targets fall on opposite sides.",
    note="The rule: from any node, if both targets are bigger, the answer is to "
    "the right; if both smaller, to the left. When they split, that's the LCA.",
    active=[0], done={}, state=[["idea", "follow BST order"]])
add(act=0, code="lca", line=7,
    note="The split point is the deepest node that still has both targets below "
    "it — exactly the lowest common ancestor.",
    active=[0], done={0: "?"}, state=[["stop when", "targets split"]])


def lca(tree, root, pval, qval, act, done):
    """Walk down; badges the descent path, then the answer. Returns node id."""
    node = root
    while node is not None:
        v = tree[node][0]
        if pval > v and qval > v:
            done[node] = "->R"
            add(act=act, code="lca", line=2,
                note=f"At {v}: both {pval} and {qval} are bigger -> go right.",
                active=[node], done=dict(done),
                state=[["at", v], ["move", "right"]])
            node = tree[node][2]
        elif pval < v and qval < v:
            done[node] = "->L"
            add(act=act, code="lca", line=4,
                note=f"At {v}: both {pval} and {qval} are smaller -> go left.",
                active=[node], done=dict(done),
                state=[["at", v], ["move", "left"]])
            node = tree[node][1]
        else:
            done[node] = "LCA"
            add(act=act, code="lca", line=7,
                note=f"At {v}: {pval} and {qval} fall on opposite sides (or one "
                f"equals {v}) -> {v} is the LCA.",
                active=[node], done=dict(done),
                state=[["LCA", v]])
            return node
    return None


# Act 1: they split at the root
add(act=1, nodes=nodes_a, edges=edges_a, code="lca", line=0,
    intro="each step commits to one side; the walk stops the moment they diverge.",
    invariant="only nodes on the path from root to the LCA are ever visited.",
    note="Find LCA of 3 and 5. Both are under 6 on the left, then both under 4 "
    "on the right of 2 — we descend until they split.",
    active=[0], done={by_val[3]: "p", by_val[5]: "q"},
    state=[["targets", "3 and 5"]])
d1 = {by_val[3]: "p", by_val[5]: "q"}
ans1 = lca(TREE, 0, 3, 5, 1, d1)
add(act=1, code="lca", line=7,
    note=f"3 and 5 split at 4 (3 < 4 < 5) -> LCA = {TREE[ans1][0]}.",
    active=[ans1], done=dict(d1), state=[["LCA", TREE[ans1][0]]],
    banner=f"LCA(3, 5) = {TREE[ans1][0]}")

# Act 2: they split immediately at the root
add(act=2, nodes=nodes_a, edges=edges_a, code="lca", line=2,
    intro="targets on opposite sides of the very first node stop the walk at once.",
    invariant="the split can happen at the root itself.",
    note="Find LCA of 2 and 8. At root 6: 2 < 6 and 8 > 6 -> they already split.",
    active=[0], done={by_val[2]: "p", by_val[8]: "q"},
    state=[["targets", "2 and 8"]])
d2 = {by_val[2]: "p", by_val[8]: "q"}
ans2 = lca(TREE, 0, 2, 8, 2, d2)
add(act=2, code="lca", line=7,
    note=f"They split at the root -> LCA = {TREE[ans2][0]}.",
    active=[ans2], done=dict(d2), state=[["LCA", TREE[ans2][0]]],
    banner=f"LCA(2, 8) = {TREE[ans2][0]}")

# Act 3: one target is an ancestor of the other
add(act=3, nodes=nodes_a, edges=edges_a, code="lca", line=6,
    intro="when one target sits on the path to the other, it is its own ancestor.",
    invariant="the 'else' branch also fires when a target equals the current node.",
    note="Edge: LCA of 2 and 4. From 6 go left to 2; now 4 > 2 while 2 = 2, so "
    "they no longer both go the same way -> stop at 2.",
    active=[0], done={by_val[2]: "p", by_val[4]: "q"},
    state=[["targets", "2 and 4"]])
d3 = {by_val[2]: "p", by_val[4]: "q"}
ans3 = lca(TREE, 0, 2, 4, 3, d3)
add(act=3, code="lca", line=7,
    note=f"A node is an ancestor of itself -> LCA = {TREE[ans3][0]}.",
    active=[ans3], done=dict(d3), state=[["LCA", TREE[ans3][0]]],
    banner=f"LCA(2, 4) = {TREE[ans3][0]}")

trace = {
    "player": "tree",
    "title": "LCA in a BST - follow the order, deep split, root split, then self-ancestor",
    "acts": ["The rule", "Run: deep split", "They split at the root", "Edge: one is an ancestor"],
    "code": {"lca": CODE},
    "legend": [["active", "current node"], ["good", "path / LCA"]],
    "nodes": nodes_a, "edges": edges_a, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
