"""Step trace for Maximum Depth of Binary Tree (mirrors solution.py's DFS).

Shows each node being visited and its depth resolving upward. Layout (x,y) is
computed here so viz.js only has to draw. Writes trace.json next to this file.
"""
import json
import os

# Tree:            3
#                /   \
#               9     20
#                    /  \
#                   15   7
# node id -> (value, left_id, right_id)
TREE = {
    0: (3, 1, 2),
    1: (9, None, None),
    2: (20, 3, 4),
    3: (15, None, None),
    4: (7, None, None),
}
XSTEP, YSTEP = 72, 82
pos = {}

_counter = [0]


def layout(nid, depth):
    if nid is None:
        return
    val, l, r = TREE[nid]
    layout(l, depth + 1)
    x = _counter[0] * XSTEP
    _counter[0] += 1
    pos[nid] = (x, depth * YSTEP)
    layout(r, depth + 1)


layout(0, 0)

nodes = [{"id": nid, "val": TREE[nid][0], "x": pos[nid][0], "y": pos[nid][1]}
         for nid in TREE]
edges = []
for nid, (_, l, r) in TREE.items():
    if l is not None:
        edges.append([nid, l])
    if r is not None:
        edges.append([nid, r])

frames = []
done: dict[int, int] = {}


def depth(nid):
    if nid is None:
        return 0
    val, l, r = TREE[nid]
    frames.append({
        "note": f"Visit node {val}. Its depth is 1 + the deeper of its two sides, "
                f"so first go down.",
        "active": [nid], "done": dict(done)})
    dl = depth(l)
    dr = depth(r)
    d = 1 + max(dl, dr)
    done[nid] = d
    if l is None and r is None:
        msg = f"Node {val} is a leaf (no children) -> depth 1."
    else:
        msg = f"Node {val}: 1 + max(left {dl}, right {dr}) = {d}."
    frames.append({"note": msg, "active": [nid], "done": dict(done)})
    return d


ans = depth(0)
frames.append({
    "note": f"The root's value is the answer: the longest root-to-leaf path is {ans} nodes.",
    "active": [], "done": dict(done)})

trace = {"player": "tree",
         "title": "Maximum Depth - each node's depth resolves from its children upward",
         "nodes": nodes, "edges": edges, "frames": frames}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
