"""Full-arc trace for Same Tree (tree renderer).
No wasteful baseline, so the arc is: the rule -> walk in lockstep -> edge cases
(shape differs, values differ). Mirrors is_same_tree in solution.py. Writes trace.json.
"""
import json
import os

XSTEP, YSTEP = 72, 82
frames = []

CODE = [
    "def same(p, q):",
    "    if p is None and q is None:",
    "        return True",
    "    if p is None or q is None:",
    "        return False",
    "    return (p.val == q.val",
    "            and same(p.left, q.left)",
    "            and same(p.right, q.right))",
]


def add(**f):
    frames.append(f)


def layout(tree, root, x0=0):
    """In-order x layout; returns nodes, edges, and next free column."""
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


def qid(x):
    return "q%d" % x


def prefix(tree):
    """Return a copy of `tree` with every id (and child ref) wrapped in qid()."""
    out = {}
    for k, (v, l, r) in tree.items():
        out[qid(k)] = (v, qid(l) if l is not None else None,
                       qid(r) if r is not None else None)
    return out


def two_trees(pt, proot, qt, qroot):
    """Lay p on the left, q on the right (id-prefixed) sharing one canvas."""
    pn, pe, nxt = layout(pt, proot, 0)
    qtp = prefix(qt)
    qn, qe, _ = layout(qtp, qid(qroot), nxt + 1)
    nodes = pn + qn
    edges = pe + qe
    return nodes, edges


# ---- Act 0: the rule -------------------------------------------------------
P0 = {0: (1, 1, 2), 1: (2, None, None), 2: (3, None, None)}
Q0 = {0: (1, 1, 2), 1: (2, None, None), 2: (3, None, None)}
nodes0, edges0 = two_trees(P0, 0, Q0, 0)
add(act=0, nodes=nodes0, edges=edges0, code="same", line=0,
    intro="the two trees are compared at the same position, step for step.",
    invariant="equal so far means every visited pair matched in value and shape.",
    note="The rule: two trees are the same when their roots match and their "
    "left and right subtrees are the same. That is already recursive.",
    active=[0, qid(0)], done={}, state=[["rule", "root == root, then sides"]])
add(act=0, code="same", line=1,
    note="Base case: two empty spots agree (True). One empty and one not means "
    "the shapes differ (False).",
    active=[], done={}, state=[["both empty", "True"], ["one empty", "False"]])


def compare(pt, proot, qt, qroot, act, done):
    """Walk p and q in lockstep, emitting frames. Returns True/False.

    pk is p's raw id (or None); qk is q's raw id (or None). Display id for a q
    node is qid(qk).
    """
    def go(pk, qk):
        pdisp = pk if pk is not None else None
        qdisp = qid(qk) if qk is not None else None
        act_ids = [x for x in (pdisp, qdisp) if x is not None]
        # both empty -> silently agree
        if pk is None and qk is None:
            return True
        if pk is not None and qk is not None:
            note = f"Compare {pt[pk][0]} with {qt[qk][0]}."
        else:
            note = "One side is empty here — shapes differ."
        add(act=act, code="same", line=5, note=note,
            active=act_ids, done=dict(done), state=[["at", "a matching spot"]])
        # one empty
        if pk is None or qk is None:
            for d in (pdisp, qdisp):
                if d is not None:
                    done[d] = "x"
            add(act=act, code="same", line=4,
                note="One tree has a node here and the other does not -> not same.",
                active=act_ids, done=dict(done), state=[["result", "False"]])
            return False
        pv, ql = pt[pk][0], qt[qk][0]
        if pv != ql:
            done[pdisp] = "x"; done[qdisp] = "x"
            add(act=act, code="same", line=5,
                note=f"Values differ: {pv} vs {ql} -> not same.",
                active=act_ids, done=dict(done), state=[["result", "False"]])
            return False
        # values equal -> recurse into both sides
        pl, pr = pt[pk][1], pt[pk][2]
        qlft, qrt = qt[qk][1], qt[qk][2]
        if not go(pl, qlft):
            return False
        if not go(pr, qrt):
            return False
        done[pdisp] = "="; done[qdisp] = "="
        add(act=act, code="same", line=5,
            note=f"{pv} matches and both subtrees matched -> this pair is equal.",
            active=act_ids, done=dict(done), state=[["pair", f"{pv} = {ql}"]])
        return True

    return go(proot, qroot)


# ---- Act 1: run it (identical trees) --------------------------------------
add(act=1, nodes=nodes0, edges=edges0, code="same", line=0,
    intro="matching pairs turn to '=' from the bottom up; a mismatch stops early.",
    invariant="a pair shows '=' only after its whole subtree pair matched.",
    note="Run it on p=[1,2,3], q=[1,2,3]. Every position lines up.",
    active=[0, qid(0)], done={}, state=[["start", "compare roots"]])
d1 = {}
r1 = compare(P0, 0, Q0, 0, 1, d1)
add(act=1, code="same", line=2,
    note=f"Every pair matched -> the trees are the same: {r1}.",
    active=[], done=dict(d1), state=[["same?", r1]],
    banner=f"Same tree = {r1}")

# ---- Act 2: shape differs --------------------------------------------------
P2 = {0: (1, 1, None), 1: (2, None, None)}
Q2 = {0: (1, None, 1), 1: (2, None, None)}
nodes2, edges2 = two_trees(P2, 0, Q2, 0)
add(act=2, nodes=nodes2, edges=edges2, code="same", line=3,
    intro="the same value at the root, but the child hangs on a different side.",
    invariant="matching values is not enough — the shape must line up too.",
    note="Edge: p has 2 on the left, q has 2 on the right. Values match at the "
    "root but the shape does not.",
    active=[0, qid(0)], done={}, state=[["shape", "left vs right"]])
d2 = {}
r2 = compare(P2, 0, Q2, 0, 2, d2)
add(act=2, code="same", line=4,
    note=f"A node faces an empty spot -> shapes differ -> not the same: {r2}.",
    active=[], done=dict(d2), state=[["same?", r2]],
    banner=f"Same tree = {r2}")

# ---- Act 3: values differ --------------------------------------------------
P3 = {0: (1, 1, 2), 1: (2, None, None), 2: (1, None, None)}
Q3 = {0: (1, 1, 2), 1: (1, None, None), 2: (2, None, None)}
nodes3, edges3 = two_trees(P3, 0, Q3, 0)
add(act=3, nodes=nodes3, edges=edges3, code="same", line=5,
    intro="same shape, but a value disagrees at a matching position.",
    invariant="the walk halts the instant one value pair disagrees.",
    note="Edge: p=[1,2,1], q=[1,1,2]. Same shape, but the left children differ.",
    active=[0, qid(0)], done={}, state=[["check", "values"]])
d3 = {}
r3 = compare(P3, 0, Q3, 0, 3, d3)
add(act=3, code="same", line=5,
    note=f"Left children 2 and 1 disagree -> not the same: {r3}.",
    active=[], done=dict(d3), state=[["same?", r3]],
    banner=f"Same tree = {r3}")

trace = {
    "player": "tree",
    "title": "Same Tree - the rule, run in lockstep, then shape and value edge cases",
    "acts": ["The rule", "Run: identical", "Edge: shape differs", "Edge: values differ"],
    "code": {"same": CODE},
    "legend": [["active", "comparing now"], ["good", "pair resolved"]],
    "nodes": nodes0, "edges": edges0, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
