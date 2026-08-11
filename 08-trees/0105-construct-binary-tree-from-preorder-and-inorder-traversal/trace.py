"""Full-arc trace for Construct Binary Tree from Preorder and Inorder (tree renderer).
Arc: the two facts (preorder gives the root; inorder splits left/right) -> build
the tree node by node -> edge case (a left-leaning chain). Mirrors build_tree /
helper in solution.py. Writes trace.json.

The scene grows: each frame carries only the nodes placed so far, so the tree
appears one node at a time as the recursion creates it.
"""
import json
import os

XSTEP, YSTEP = 74, 82
frames = []

CODE = [
    "index = {val: i for i, val in enumerate(inorder)}",
    "pre = iter(preorder)",
    "def helper(lo, hi):",
    "    if lo > hi: return None",
    "    root_val = next(pre)      # preorder gives the root",
    "    mid = index[root_val]     # split inorder at the root",
    "    root.left  = helper(lo, mid - 1)   # left part",
    "    root.right = helper(mid + 1, hi)   # right part",
    "    return root",
]


def add(**f):
    frames.append(f)


def sidebar(pre, pre_ptr, ino, lo, hi):
    """Show preorder (with cursor) and the active inorder window."""
    pre_str = " ".join(("[%s]" % x if i == pre_ptr else str(x))
                        for i, x in enumerate(pre))
    ino_str = " ".join(("<%s>" % x if lo <= i <= hi else str(x))
                        for i, x in enumerate(ino))
    return {"title": "arrays", "rows": [["preorder", pre_str],
                                        ["inorder", ino_str],
                                        ["window", f"[{lo}..{hi}]" if lo <= hi else "empty"]]}


def build_trace(preorder, inorder, act, positions, edges_out, first_intro=None):
    """Run the reconstruction, emitting a growing tree. Returns (nodes_final).

    positions: dict node_id -> (x, y) precomputed from the final tree.
    Node ids are the node values (unique in these inputs).
    """
    index = {v: i for i, v in enumerate(inorder)}
    pre_iter = iter(range(len(preorder)))
    placed = {}   # val -> node dict
    done = {}     # val -> badge

    placed_ids = set()

    def nodes_now():
        return [placed[v] for v in placed]

    def edges_out_current():
        return [e for e in edges_out if e[0] in placed_ids and e[1] in placed_ids]

    pre_ptr = [0]

    def helper(lo, hi):
        if lo > hi:
            add(act=act, nodes=nodes_now(), edges=edges_out_current(),
                code="build", line=3,
                note=f"Empty range [{lo}..{hi}] -> no node here.",
                active=[], done=dict(done),
                sidebar=sidebar(preorder, pre_ptr[0], inorder, lo, hi),
                state=[["range", "empty"]])
            return None
        root_val = preorder[pre_ptr[0]]
        this_ptr = pre_ptr[0]
        pre_ptr[0] += 1
        mid = index[root_val]
        x, y = positions[root_val]
        placed[root_val] = {"id": root_val, "val": root_val, "x": x, "y": y}
        placed_ids.add(root_val)
        add(act=act, nodes=nodes_now(), edges=edges_out_current(),
            code="build", line=4,
            note=f"Preorder cursor -> {root_val}: that's this subtree's root. "
            f"Find it in inorder (index {mid}).",
            active=[root_val], done=dict(done),
            sidebar=sidebar(preorder, this_ptr, inorder, lo, hi),
            state=[["root", root_val], ["split at", mid]])
        add(act=act, nodes=nodes_now(), edges=edges_out_current(),
            code="build", line=5,
            note=f"Inorder splits at {root_val}: left part = [{lo}..{mid-1}], "
            f"right part = [{mid+1}..{hi}]. Build left first (preorder order).",
            active=[root_val], done=dict(done),
            sidebar=sidebar(preorder, pre_ptr[0], inorder, lo, hi),
            state=[["left", f"[{lo}..{mid-1}]"], ["right", f"[{mid+1}..{hi}]"]])
        helper(lo, mid - 1)
        helper(mid + 1, hi)
        done[root_val] = "ok"
        add(act=act, nodes=nodes_now(), edges=edges_out_current(),
            code="build", line=8,
            note=f"Both sides of {root_val} are built -> this subtree is done.",
            active=[root_val], done=dict(done),
            sidebar=sidebar(preorder, pre_ptr[0], inorder, lo, hi),
            state=[["placed", root_val]])
        return root_val

    helper(0, len(inorder) - 1)
    return nodes_now(), done


# ---- Layout the final tree so nodes land in the right spot as they appear ----
def layout_final(tree, root):
    pos = {}
    counter = [0]

    def walk(nid, depth):
        if nid is None:
            return
        l, r = tree[nid]
        walk(l, depth + 1)
        pos[nid] = (counter[0] * XSTEP, depth * YSTEP)
        counter[0] += 1
        walk(r, depth + 1)

    walk(root, 0)
    return pos


# Example 1: preorder [3,9,20,15,7], inorder [9,3,15,20,7]
# Final tree children (by value):
CH_A = {3: (9, 20), 9: (None, None), 20: (15, 7),
        15: (None, None), 7: (None, None)}
POS_A = layout_final(CH_A, 3)
EDGES_A = []
for v, (l, r) in CH_A.items():
    if l is not None:
        EDGES_A.append([v, l])
    if r is not None:
        EDGES_A.append([v, r])

# Act 0: the two facts (static intro on the empty-ish canvas -> show root only)
add(act=0, nodes=[{"id": 3, "val": 3, "x": POS_A[3][0], "y": POS_A[3][1]}],
    edges=[], code="build", line=4,
    intro="preorder's front is always the current root; inorder splits the rest.",
    invariant="the size of inorder's left part decides how much of preorder is left subtree.",
    note="Two facts do all the work. Preorder visits the root first, so its front "
    "value is this subtree's root.",
    active=[3], done={},
    sidebar=sidebar([3, 9, 20, 15, 7], 0, [9, 3, 15, 20, 7], 0, 4),
    state=[["preorder[0]", 3]])
add(act=0, nodes=[{"id": 3, "val": 3, "x": POS_A[3][0], "y": POS_A[3][1]}],
    edges=[], code="build", line=5,
    note="Inorder visits left, root, right. Once we know the root, its spot in "
    "inorder splits everything into the left subtree and the right subtree.",
    active=[3], done={},
    sidebar=sidebar([3, 9, 20, 15, 7], 0, [9, 3, 15, 20, 7], 0, 4),
    state=[["inorder split", "9 | 3 | 15 20 7"]])

# Act 1: build it
add(act=1, nodes=[{"id": 3, "val": 3, "x": POS_A[3][0], "y": POS_A[3][1]}],
    edges=[], code="build", line=2,
    intro="the tree grows one node at a time as the recursion pulls roots off preorder.",
    invariant="each root is placed before recursing into its (smaller) inorder halves.",
    note="Build it. preorder=[3,9,20,15,7], inorder=[9,3,15,20,7].",
    active=[3], done={},
    sidebar=sidebar([3, 9, 20, 15, 7], 0, [9, 3, 15, 20, 7], 0, 4),
    state=[["start", "range [0..4]"]])
nodes_a, done_a = build_trace([3, 9, 20, 15, 7], [9, 3, 15, 20, 7], 1, POS_A, EDGES_A)
add(act=1, nodes=nodes_a, edges=EDGES_A, code="build", line=8,
    note="Preorder is used up and every inorder range is placed -> the unique "
    "tree is [3,9,20,null,null,15,7].",
    active=[], done=dict(done_a), state=[["built", "[3,9,20,_,_,15,7]"]],
    banner="Reconstructed: [3,9,20,null,null,15,7]")

# Act 2: left-leaning chain. preorder [1,2,3], inorder [3,2,1] -> chain 1->2->3 left
CH_B = {1: (2, None), 2: (3, None), 3: (None, None)}
POS_B = layout_final(CH_B, 1)
EDGES_B = [[1, 2], [2, 3]]
add(act=2, nodes=[{"id": 1, "val": 1, "x": POS_B[1][0], "y": POS_B[1][1]}],
    edges=[], code="build", line=5,
    intro="when inorder is fully reversed, every split has an empty right side.",
    invariant="an empty right range means no right child — the tree only leans left.",
    note="Edge: preorder=[1,2,3], inorder=[3,2,1]. Each root's inorder split has "
    "nothing on the right, so the tree is a left-leaning chain.",
    active=[1], done={},
    sidebar=sidebar([1, 2, 3], 0, [3, 2, 1], 0, 2),
    state=[["shape", "left chain"]])
nodes_b, done_b = build_trace([1, 2, 3], [3, 2, 1], 2, POS_B, EDGES_B)
add(act=2, nodes=nodes_b, edges=EDGES_B, code="build", line=8,
    note="Every right range came back empty -> [1,2,null,3], a left chain.",
    active=[], done=dict(done_b), state=[["built", "[1,2,null,3]"]],
    banner="Reconstructed: [1,2,null,3]")

trace = {
    "player": "tree",
    "title": "Construct from Preorder + Inorder - root from preorder, split by inorder, built live",
    "acts": ["The two facts", "Build the tree", "Edge: a left chain"],
    "code": {"build": CODE},
    "legend": [["active", "current root"], ["good", "subtree placed"]],
    "nodes": nodes_a, "edges": EDGES_A, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
