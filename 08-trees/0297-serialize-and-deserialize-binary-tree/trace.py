"""Full-arc trace for Serialize and Deserialize Binary Tree (tree renderer).
Arc: why a plain value list loses the shape -> serialize with '#' markers ->
deserialize rebuilds the exact tree. Mirrors Codec in solution.py. Writes
trace.json. The deserialize scene grows one node at a time.
"""
import json
import os

XSTEP, YSTEP = 74, 82
frames = []

CODE = [
    "def serialize(node):",
    "    if node is None: emit('#'); return",
    "    emit(node.val)",
    "    serialize(node.left)   # preorder: root, left, right",
    "    serialize(node.right)",
    "# --- deserialize ---",
    "def build():",
    "    val = next(tokens)",
    "    if val == '#': return None",
    "    node.left  = build()",
    "    node.right = build()",
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


# [1,2,3,null,null,4,5]
TREE = {0: (1, 1, 2), 1: (2, None, None), 2: (3, 3, 4),
        3: (4, None, None), 4: (5, None, None)}
nodes_a, edges_a = layout(TREE, 0)

# Act 0: a plain list loses the shape
add(act=0, nodes=nodes_a, edges=edges_a, code="serialize", line=1,
    intro="empty children must be recorded too, or the shape is ambiguous.",
    invariant="every node, present or missing, gets exactly one token.",
    note="A plain list of values loses the tree's shape: you can't tell where a "
    "child is missing. The fix is to write a '#' for every empty child.",
    active=[0], done={}, state=[["problem", "shape is lost"]])
add(act=0, nodes=nodes_a, edges=edges_a, code="serialize", line=0,
    note="Preorder (root, left, right) with '#' markers is unambiguous: reading "
    "tokens front-to-back rebuilds the exact same tree.",
    active=[0], done={}, state=[["format", "preorder + '#'"]])

# Act 1: serialize
tokens = []


def serialize(nid, tree, act, done):
    if nid is None:
        tokens.append("#")
        add(act=act, code="serialize", line=1,
            note="Empty child -> write '#'.",
            active=[], done=dict(done),
            state=[["emit", "#"], ["so far", ",".join(tokens)]])
        return
    v = tree[nid][0]
    tokens.append(str(v))
    done[nid] = "w"
    add(act=act, code="serialize", line=2,
        note=f"Visit {v} -> write '{v}', then recurse left, then right.",
        active=[nid], done=dict(done),
        state=[["emit", v], ["so far", ",".join(tokens)]])
    serialize(tree[nid][1], tree, act, done)
    serialize(tree[nid][2], tree, act, done)


add(act=1, nodes=nodes_a, edges=edges_a, code="serialize", line=0,
    intro="each node writes its value; each empty slot writes a '#'.",
    invariant="the token string grows in preorder as we descend.",
    note="Serialize [1,2,3,null,null,4,5]. Walk preorder, emitting tokens.",
    active=[0], done={}, state=[["tokens", ""]])
d1 = {}
serialize(0, TREE, 1, d1)
serial = ",".join(tokens)
add(act=1, nodes=nodes_a, edges=edges_a, code="serialize", line=4,
    note=f"Done. The string is: {serial}",
    active=[], done=dict(d1), state=[["serialized", serial]],
    banner=f"serialize -> {serial}")

# Act 2: deserialize (rebuild the growing tree)
# Precompute final layout so nodes land in place as they're created.
POS = {}
_nodes_tmp, _ = layout(TREE, 0)
for nd in _nodes_tmp:
    POS[nd["id"]] = (nd["x"], nd["y"])
# Map token order -> which node id it creates. Preorder over TREE:
pre_order_ids = []


def _pre(nid):
    if nid is None:
        return
    pre_order_ids.append(nid)
    _pre(TREE[nid][1])
    _pre(TREE[nid][2])


_pre(0)

tok_iter = iter(serial.split(","))
placed = {}
placed_ids = set()
create_seq = iter(pre_order_ids)  # non-'#' tokens create these ids in order
done2 = {}


def nodes_now():
    return [placed[i] for i in placed]


def edges_now():
    return [e for e in edges_a if e[0] in placed_ids and e[1] in placed_ids]


def build(act):
    val = next(tok_iter)
    if val == "#":
        add(act=act, nodes=nodes_now(), edges=edges_now(), code="serialize", line=8,
            note="Token '#' -> this child is empty (None).",
            active=[], done=dict(done2), state=[["read", "#"]])
        return None
    nid = next(create_seq)
    x, y = POS[nid]
    placed[nid] = {"id": nid, "val": int(val), "x": x, "y": y}
    placed_ids.add(nid)
    add(act=act, nodes=nodes_now(), edges=edges_now(), code="serialize", line=7,
        note=f"Token '{val}' -> make a node, then build its left, then its right.",
        active=[nid], done=dict(done2), state=[["read", val]])
    build(act)   # left
    build(act)   # right
    done2[nid] = "ok"
    add(act=act, nodes=nodes_now(), edges=edges_now(), code="serialize", line=10,
        note=f"Node {val}'s children are both attached -> it's complete.",
        active=[nid], done=dict(done2), state=[["placed", val]])
    return nid


add(act=2, nodes=[], edges=[], code="serialize", line=6,
    intro="tokens are consumed front-to-back; the same preorder rebuilds the tree.",
    invariant="a '#' closes a branch; a value opens a new node and two more reads.",
    note=f"Deserialize '{serial}'. Consume tokens in order; the tree grows back.",
    active=[], done={}, state=[["tokens", serial]])
build(2)
add(act=2, nodes=nodes_now(), edges=edges_now(), code="serialize", line=10,
    note="All tokens consumed -> the original tree [1,2,3,null,null,4,5] is back.",
    active=[], done=dict(done2), state=[["round-trip", "exact match"]],
    banner="deserialize -> [1,2,3,null,null,4,5]  (round-trips)")

trace = {
    "player": "tree",
    "title": "Serialize / Deserialize - '#' keeps the shape, then rebuild it back",
    "acts": ["Why a value list fails", "Serialize with '#'", "Deserialize: rebuild"],
    "code": {"serialize": CODE},
    "legend": [["active", "current node"], ["good", "written / rebuilt"]],
    "nodes": nodes_a, "edges": edges_a, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
