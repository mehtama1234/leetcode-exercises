"""Full-arc trace for Kth Smallest Element in a BST (tree renderer).
Arc: the rule (in-order of a BST is sorted) -> run it and stop at the k-th
emitted node -> edge case (k = n, the largest). Mirrors kth_smallest in
solution.py. Writes trace.json.
"""
import json
import os

XSTEP, YSTEP = 74, 82
frames = []

CODE = [
    "stack, node = [], root",
    "while stack or node:",
    "    while node:            # dive left",
    "        stack.append(node)",
    "        node = node.left",
    "    node = stack.pop()     # smallest unseen",
    "    k -= 1",
    "    if k == 0: return node.val",
    "    node = node.right      # then go right",
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


# [5,3,6,2,4,null,null,1] -> sorted 1,2,3,4,5,6
TREE = {0: (5, 1, 2), 1: (3, 3, 4), 2: (6, None, None),
        3: (2, 5, None), 4: (4, None, None), 5: (1, None, None)}
nodes_a, edges_a = layout(TREE, 0)

# Act 0: the rule
add(act=0, nodes=nodes_a, edges=edges_a, code="kth", line=2,
    intro="an in-order walk of a BST emits values in sorted order.",
    invariant="everything left of a node is smaller — so drain left before emitting.",
    note="The rule: in a BST, everything to the left of a node is smaller. So an "
    "in-order walk (left, node, right) emits values already sorted.",
    active=[0], done={}, state=[["order", "left, node, right"]])
add(act=0, code="kth", line=7,
    note="If in-order gives sorted values, the k-th node emitted is the k-th "
    "smallest. Use a stack so we can stop the instant k hits 0.",
    active=[5], done={5: "1st"}, state=[["1st smallest", 1]])


def kth(tree, root, k, act, done, stop=True):
    """Iterative in-order; badges each emitted node with its rank. Returns value."""
    stack = []
    node = root
    rank = 0
    ans = None
    while stack or node is not None:
        # dive left
        while node is not None:
            add(act=act, code="kth", line=3,
                note=f"Dive left from {tree[node][0]}: push it, go to its left child.",
                active=[node], done=dict(done),
                state=[["push", tree[node][0]], ["stack", [tree[s][0] for s in stack] + [tree[node][0]]]])
            stack.append(node)
            node = tree[node][1]
        node = stack.pop()
        rank += 1
        v = tree[node][0]
        done[node] = "%d" % rank
        hit = (rank == k)
        add(act=act, code="kth", line=6,
            note=f"Pop the smallest unseen: {v}. That is #{rank} smallest."
            + (f"  k={k} reached -> answer." if hit else ""),
            active=[node], done=dict(done),
            state=[["emitted #", rank], ["value", v], ["target k", k]])
        if hit and stop:
            ans = v
            break
        node = tree[node][2]  # go right
    return ans


# Act 1: run it, k=3
add(act=1, nodes=nodes_a, edges=edges_a, code="kth", line=0,
    intro="values pop out in sorted order; we stop the moment the count hits k.",
    invariant="the r-th node popped is the r-th smallest value.",
    note="Run it with k=3. Walk in-order, counting, and stop at the 3rd pop.",
    active=[0], done={}, state=[["k", 3]])
d1 = {}
r1 = kth(TREE, 0, 3, 1, d1)
add(act=1, code="kth", line=7,
    note=f"The 3rd node emitted is {r1}. We stop without touching the rest.",
    active=[], done=dict(d1), state=[["3rd smallest", r1]],
    banner=f"Kth smallest (k=3) = {r1}")

# Act 2: k = n (the largest)
add(act=2, nodes=nodes_a, edges=edges_a, code="kth", line=0,
    intro="with k = n we walk the entire tree and the last pop is the maximum.",
    invariant="same in-order walk, no early stop until the very last node.",
    note="Edge: k=6 = number of nodes. Now we must walk the whole tree; the last "
    "value emitted is the largest.",
    active=[0], done={}, state=[["k", 6]])
d2 = {}
r2 = kth(TREE, 0, 6, 2, d2)
add(act=2, code="kth", line=7,
    note=f"The 6th (last) node emitted is the maximum: {r2}.",
    active=[], done=dict(d2), state=[["6th smallest", r2]],
    banner=f"Kth smallest (k=6) = {r2}")

trace = {
    "player": "tree",
    "title": "Kth Smallest in a BST - in-order is sorted, stop at k, then k = n",
    "acts": ["The rule: in-order is sorted", "Run: k = 3", "Edge: k = n (the max)"],
    "code": {"kth": CODE},
    "legend": [["active", "on the stack / popping"], ["good", "emitted (rank badge)"]],
    "nodes": nodes_a, "edges": edges_a, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
