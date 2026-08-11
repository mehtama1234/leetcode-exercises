"""Rich full-arc trace for Maximum Depth of Binary Tree (tree renderer reference).
Trees have no wasteful brute baseline, so the arc is: the rule -> DFS bottom-up
-> a lopsided edge case. Mirrors the DFS in solution.py. Writes trace.json.
"""
import json
import os

XSTEP, YSTEP = 72, 82
frames = []

CODE = [
    "def max_depth(node):",
    "    if not node:",
    "        return 0",
    "    L = max_depth(node.left)",
    "    R = max_depth(node.right)",
    "    return 1 + max(L, R)",
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
    nodes = [{"id": nid, "val": tree[nid][0], "x": pos[nid][0], "y": pos[nid][1]} for nid in tree]
    edges = []
    for nid, (_, l, r) in tree.items():
        if l is not None:
            edges.append([nid, l])
        if r is not None:
            edges.append([nid, r])
    return nodes, edges


TREE_A = {0: (3, 1, 2), 1: (9, None, None), 2: (20, 3, 4),
          3: (15, None, None), 4: (7, None, None)}
nodes_a, edges_a = layout(TREE_A, 0)

# Act 0: the rule
add(act=0, nodes=nodes_a, edges=edges_a, code="dfs", line=5,
    intro="a node waits for BOTH children before it can answer.",
    invariant="a node's depth = 1 + the depth of its deeper child.",
    note="The rule from the definition: a node's depth is 1 + the depth of its "
    "deeper child. So we need the children's answers first.",
    active=[0], done={}, state=[["rule", "1 + max(L, R)"]])
add(act=0, code="dfs", line=2,
    note="A leaf has no children, so both sides are 0 -> depth 1 + 0 = 1. That base "
    "case is where the counting starts.", active=[1], done={},
    state=[["leaf depth", 1]])

done = {}


def depth(nid, tree, act):
    _, l, r = tree[nid]
    add(act=act, code="dfs", line=3,
        note=f"Visit node {tree[nid][0]}. Ask its children first.",
        active=[nid], done=dict(done),
        state=[["visiting", tree[nid][0]]])
    dl = depth(l, tree, act) if l is not None else 0
    dr = depth(r, tree, act) if r is not None else 0
    d = 1 + max(dl, dr)
    done[nid] = d
    leaf = l is None and r is None
    add(act=act, code="dfs", line=2 if leaf else 5,
        note=(f"Node {tree[nid][0]} is a leaf -> depth 1." if leaf
              else f"Node {tree[nid][0]}: 1 + max(left {dl}, right {dr}) = {d}."),
        active=[nid], done=dict(done),
        state=[["node", tree[nid][0]], ["depth", d]])
    return d


# Act 1: DFS bottom-up
add(act=1, nodes=nodes_a, edges=edges_a, code="dfs", line=0,
    intro="each node lights its answer only once both sides return.",
    invariant="a node's badge appears only after its whole subtree is done.",
    note="Run it. Watch answers appear from the leaves upward.",
    active=[0], done={}, state=[["start", "root 3"]])
ans = depth(0, TREE_A, 1)
add(act=1, code="dfs", line=5,
    note=f"The root's answer is the whole tree's depth: {ans}.",
    active=[], done=dict(done), state=[["max depth", ans]],
    banner=f"Maximum depth = {ans}  (longest root-to-leaf path)")

# Act 2: lopsided edge case
TREE_B = {0: (1, None, 1), 1: (2, None, 2), 2: (3, None, None)}
nodes_b, edges_b = layout(TREE_B, 0)
done = {}
add(act=2, nodes=nodes_b, edges=edges_b, code="dfs", line=0,
    intro="with no branching, depth is just the count down one path.",
    invariant="same rule, still 1 + max of the (single) child side.",
    note="Edge case: a lopsided tree, each node with only one child.",
    active=[0], done={}, state=[["shape", "single path"]])
ans2 = depth(0, TREE_B, 2)
add(act=2, code="dfs", line=5,
    note=f"No branches, so depth = number of nodes = {ans2}. (One node -> 1; empty -> 0.)",
    active=[], done=dict(done), state=[["max depth", ans2]],
    banner=f"Maximum depth = {ans2}")

trace = {
    "player": "tree",
    "title": "Maximum Depth - the rule, run bottom-up, then a lopsided tree",
    "acts": ["The rule", "DFS resolves bottom-up", "Edge case: lopsided"],
    "code": {"dfs": CODE},
    "legend": [["active", "visiting now"], ["good", "depth known"]],
    "nodes": nodes_a, "edges": edges_a, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
