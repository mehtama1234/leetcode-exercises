"""Full-arc trace for Binary Tree Maximum Path Sum (tree renderer).
Arc: the two roles a node plays -> run the DFS (global best vs upward gain) ->
edge case (all negatives: pick the least-bad single node). Mirrors gain() in
solution.py. Writes trace.json.
"""
import json
import os

XSTEP, YSTEP = 74, 82
frames = []

CODE = [
    "def gain(node):",
    "    if node is None: return 0",
    "    left  = max(gain(node.left), 0)   # drop negative arms",
    "    right = max(gain(node.right), 0)",
    "    best = max(best, node.val + left + right)  # peak here",
    "    return node.val + max(left, right)         # extend up",
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


# [-10,9,20,null,null,15,7] -> answer 42 (15+20+7)
TREE = {0: (-10, 1, 2), 1: (9, None, None), 2: (20, 3, 4),
        3: (15, None, None), 4: (7, None, None)}
nodes_a, edges_a = layout(TREE, 0)

# Act 0: the two roles
add(act=0, nodes=nodes_a, edges=edges_a, code="pathsum", line=4,
    intro="a node peaks a path with BOTH arms, but hands up only ONE arm.",
    invariant="best tracks full peaks; the return value is a straight line upward.",
    note="The twist: each node plays two roles. As a path's peak it may use both "
    "arms (val + left + right). But it can hand its parent only one arm.",
    active=[2], done={}, state=[["peak here", "val + L + R"], ["give up", "val + max(L,R)"]])
add(act=0, code="pathsum", line=2,
    note="A negative arm is never worth taking, so clamp each side at 0 before "
    "using it. Track a global best separate from what we return.",
    active=[2], done={}, state=[["rule", "clamp arms at 0"]])


def gain(nid, tree, act, done, best_box):
    """DFS returning upward gain; updates best_box[0]. Emits frames."""
    if nid is None:
        return 0
    v = tree[nid][0]
    _, l, r = tree[nid]
    add(act=act, code="pathsum", line=0,
        note=f"Enter node {v}. Ask both arms for their best downward gain.",
        active=[nid], done=dict(done), state=[["visiting", v]])
    gl = max(gain(l, tree, act, done, best_box), 0)
    gr = max(gain(r, tree, act, done, best_box), 0)
    peak = v + gl + gr
    best_box[0] = max(best_box[0], peak)
    up = v + max(gl, gr)
    done[nid] = up
    add(act=act, code="pathsum", line=4,
        note=f"Node {v}: arms clamped to L={gl}, R={gr}. Peak here = {peak} "
        f"(best so far {best_box[0]}). Hand up {up}.",
        active=[nid], done=dict(done),
        state=[["node", v], ["peak", peak], ["give up", up], ["best", best_box[0]]])
    return up


# Act 1: run it
add(act=1, nodes=nodes_a, edges=edges_a, code="pathsum", line=0,
    intro="each badge is the value a node hands upward; the best is a separate tally.",
    invariant="best only grows; it captures the largest peak seen anywhere.",
    note="Run it on [-10,9,20,null,null,15,7]. The winning path 15-20-7 never "
    "touches the root.",
    active=[0], done={}, state=[["best", "-inf"]])
best = [float("-inf")]
d1 = {}
gain(0, TREE, 1, d1, best)
add(act=1, code="pathsum", line=4,
    note=f"The best peak found is at node 20: 15 + 20 + 7 = {int(best[0])}. The "
    f"root -10 was never part of the winner.",
    active=[2], done=dict(d1), state=[["max path sum", int(best[0])]],
    banner=f"Maximum path sum = {int(best[0])}")

# Act 2: all negatives
TREE_B = {0: (-2, 1, None), 1: (-1, None, None)}
nodes_b, edges_b = layout(TREE_B, 0)
add(act=2, nodes=nodes_b, edges=edges_b, code="pathsum", line=2,
    intro="every arm clamps to 0, so the best path is a single least-bad node.",
    invariant="clamping means we never add a negative neighbour.",
    note="Edge: all negatives [-2,-1]. Both arms clamp to 0, so each node's peak "
    "is just itself -> pick the least negative.",
    active=[0], done={}, state=[["best", "-inf"]])
best2 = [float("-inf")]
d2 = {}
gain(0, TREE_B, 2, d2, best2)
add(act=2, code="pathsum", line=4,
    note=f"Single-node peaks are -2 and -1 -> the best is {int(best2[0])}.",
    active=[1], done=dict(d2), state=[["max path sum", int(best2[0])]],
    banner=f"Maximum path sum = {int(best2[0])}")

trace = {
    "player": "tree",
    "title": "Max Path Sum - the two roles, run it, then all negatives",
    "acts": ["Two roles of a node", "Run: best peak wins", "Edge: all negatives"],
    "code": {"pathsum": CODE},
    "legend": [["active", "visiting now"], ["good", "gain handed up"]],
    "nodes": nodes_a, "edges": edges_a, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
