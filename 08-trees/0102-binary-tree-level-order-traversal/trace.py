"""Full-arc trace for Binary Tree Level Order Traversal (tree renderer).
Arc: the rule (freeze the level size) -> run BFS level by level -> edge case
(a left-leaning tree = one node per level). Mirrors level_order in solution.py.
Writes trace.json.
"""
import json
import os

XSTEP, YSTEP = 72, 82
frames = []

CODE = [
    "queue = [root]",
    "while queue:",
    "    level_size = len(queue)   # frozen now",
    "    level = []",
    "    for _ in range(level_size):",
    "        node = queue.pop(0)",
    "        level.append(node.val)",
    "        if node.left:  queue.append(node.left)",
    "        if node.right: queue.append(node.right)",
    "    result.append(level)",
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


# TREE_A = [3,9,20,null,null,15,7]
TREE_A = {0: (3, 1, 2), 1: (9, None, None), 2: (20, 3, 4),
          3: (15, None, None), 4: (7, None, None)}
nodes_a, edges_a = layout(TREE_A, 0)

# Act 0: the rule
add(act=0, nodes=nodes_a, edges=edges_a, code="bfs", line=2,
    intro="each round handles exactly one level — the frozen count is the trick.",
    invariant="level_size counts only the nodes already in the queue this round.",
    note="The rule: at the start of each round, freeze how many nodes are in the "
    "queue. That count is exactly one level. Pop that many, no more.",
    active=[0], done={}, state=[["frozen size", 1], ["level", 0]])
add(act=0, code="bfs", line=7,
    note="As we pop a level we enqueue its children — they become the NEXT "
    "level, but the frozen count keeps them out of this round.",
    active=[1, 2], done={0: "L0"}, state=[["next queue", "9, 20"]])


def level_order(tree, root, act, done):
    """BFS, one frame per popped node plus a frame per completed level."""
    result = []
    queue = [root]
    level_idx = 0
    while queue:
        size = len(queue)
        add(act=act, code="bfs", line=2,
            note=f"Start level {level_idx}: freeze size = {size}. "
            f"These {size} node(s) form this level.",
            active=list(queue), done=dict(done),
            state=[["level", level_idx], ["frozen size", size]])
        level = []
        for _ in range(size):
            nid = queue.pop(0)
            v = tree[nid][0]
            level.append(v)
            done[nid] = "L%d" % level_idx
            _, l, r = tree[nid]
            for c in (l, r):
                if c is not None:
                    queue.append(c)
            add(act=act, code="bfs", line=6,
                note=f"Pop {v} -> add to level {level_idx}. "
                + (f"Enqueue its children for the next level."
                   if (l is not None or r is not None)
                   else "It's a leaf, nothing to enqueue."),
                active=[nid], done=dict(done),
                state=[["popped", v], ["level so far", level]])
        result.append(level)
        add(act=act, code="bfs", line=9,
            note=f"Level {level_idx} complete: {level}.",
            active=[], done=dict(done),
            state=[["result", result]])
        level_idx += 1
    return result


# Act 1: run it
add(act=1, nodes=nodes_a, edges=edges_a, code="bfs", line=0,
    intro="nodes light up a whole level at once, then drain one at a time.",
    invariant="every node ends badged with the level it was read on.",
    note="Run it on [3,9,20,null,null,15,7]. Read top to bottom, left to right.",
    active=[0], done={}, state=[["start", "queue = [3]"]])
d1 = {}
r1 = level_order(TREE_A, 0, 1, d1)
add(act=1, code="bfs", line=9,
    note=f"Queue empty -> done. Levels: {r1}.",
    active=[], done=dict(d1), state=[["result", r1]],
    banner=f"Level order = {r1}")

# Act 2: left-leaning edge case
TREE_B = {0: (1, 1, None), 1: (2, 2, None), 2: (3, None, None)}
nodes_b, edges_b = layout(TREE_B, 0)
add(act=2, nodes=nodes_b, edges=edges_b, code="bfs", line=2,
    intro="with no branching the frozen size is always 1 -> one node per level.",
    invariant="the same freeze-and-drain rule, now with single-node levels.",
    note="Edge: a left-leaning tree [1,2,null,3]. Each level holds just one node.",
    active=[0], done={}, state=[["shape", "single chain"]])
d2 = {}
r2 = level_order(TREE_B, 0, 2, d2)
add(act=2, code="bfs", line=9,
    note=f"One node per level all the way down: {r2}.",
    active=[], done=dict(d2), state=[["result", r2]],
    banner=f"Level order = {r2}")

trace = {
    "player": "tree",
    "title": "Level Order Traversal - freeze the level size, run BFS, then a chain",
    "acts": ["The rule: freeze the size", "Run BFS level by level", "Edge: a chain"],
    "code": {"bfs": CODE},
    "legend": [["active", "current level / popping"], ["good", "read (level badge)"]],
    "nodes": nodes_a, "edges": edges_a, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
