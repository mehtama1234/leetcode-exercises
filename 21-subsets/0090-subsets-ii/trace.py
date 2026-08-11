"""Full-arc tree trace for Subsets II (backtracking decision tree with a prune).

Subsets (0078) is a clean binary include/exclude tree. Subsets II is different in
two ways, and this trace makes both visible:
  1. EVERY node — not just leaves — is a recorded subset (result.append(path[:])
     happens on entry to each call), so we badge every visited node green.
  2. Duplicates are killed by a sibling skip: after sorting, within one loop level
     if nums[i] == nums[i-1] and i > start, that branch is skipped. We still draw
     those skipped children (badged "✕") so the prune is something you can see,
     not just read.

We precompute every node's x,y in Python for the sorted input. A node at "start"
loops over i in [start, n): each i that survives the skip becomes a child whose
path is the parent path + nums[i]. Mirrors backtrack() in solution.py.
"""
import json
import os

XSTEP, YSTEP = 66, 84
frames = []

CODE = [
    "def backtrack(start):",
    "    result.append(path[:])          # every node is a subset",
    "    for i in range(start, n):",
    "        if i > start and nums[i] == nums[i-1]:",
    "            continue                # skip duplicate sibling",
    "        path.append(nums[i])        # choose",
    "        backtrack(i + 1)            # explore the tail",
    "        path.pop()                  # un-choose",
]


def add(**f):
    frames.append(f)


def build_tree(raw):
    """Enumerate the choose-next-index tree for sorted(raw), INCLUDING the pruned
    duplicate-sibling branches so the skip is drawable.

    node = {id, path, val, x, y, i (the index picked to reach it, or None at root),
            pruned (bool), reason (str for pruned nodes)}.
    Layout: in-order-ish sweep — a subtree's parent x sits just left of its first
    child, computed as we recurse. Returns (nodes, edges, order):
      order = DFS visit sequence of the KEPT (non-pruned) nodes, matching the
      solution's recursion; pruned nodes are shown but never recursed into.
    """
    nums = sorted(raw)
    n = len(nums)
    nodes = {}
    edges = []
    order = []
    counter = [0]
    nid = [0]

    def label(path):
        return "{" + ",".join(str(x) for x in path) + "}" if path else "{}"

    def make(start, path, picked_i, depth):
        my = nid[0]; nid[0] += 1
        nodes[my] = {"i": picked_i, "path": list(path), "val": label(path),
                     "x": 0, "y": depth * YSTEP, "pruned": False, "reason": ""}
        order.append(my)
        # place this (kept) node just before its children by claiming a slot now
        nodes[my]["x"] = counter[0] * XSTEP; counter[0] += 1
        for i in range(start, n):
            if i > start and nums[i] == nums[i - 1]:
                # pruned sibling: draw it, badge "✕", but do NOT recurse
                pid = nid[0]; nid[0] += 1
                path.append(nums[i])
                nodes[pid] = {"i": i, "path": list(path), "val": label(path),
                              "x": counter[0] * XSTEP, "y": (depth + 1) * YSTEP,
                              "pruned": True,
                              "reason": f"nums[{i}]==nums[{i-1}] and i>start"}
                path.pop()
                counter[0] += 1
                edges.append((my, pid, "skip"))
                continue
            path.append(nums[i])
            child = make(i + 1, path, i, depth + 1)
            path.pop()
            edges.append((my, child, "+" + str(nums[i])))
        return my

    make(0, [], None, 0)
    return nums, nodes, edges, order


def render_nodes(nodes):
    return [{"id": k, "val": v["val"], "x": v["x"], "y": v["y"]} for k, v in nodes.items()]


def render_edges(edges):
    return [[a, b] for a, b, _ in edges]


def path_to(edges, target):
    parent = {}
    for a, b, _ in edges:
        parent[b] = a
    chain = [target]
    while chain[-1] in parent:
        chain.append(parent[chain[-1]])
    return chain[::-1]


def _solution_subsets(raw):
    """Independent replica of solution.subsets_with_dup for verification."""
    nums = sorted(raw)
    n = len(nums)
    res, path = [], []

    def bt(start):
        res.append(path[:])
        for i in range(start, n):
            if i > start and nums[i] == nums[i - 1]:
                continue
            path.append(nums[i])
            bt(i + 1)
            path.pop()
    bt(0)
    return res


# ============================ Act 0 + 1: [1,2,2] ============================
RAW = [1, 2, 2]
NUMS, nodes, edges, order = build_tree(RAW)
NODES = render_nodes(nodes)
EDGES = render_edges(edges)

# verify the kept nodes reproduce the real output exactly
kept_paths = [nodes[i]["path"] for i in order]
assert kept_paths == _solution_subsets(RAW), (kept_paths, _solution_subsets(RAW))
assert len({tuple(p) for p in kept_paths}) == len(kept_paths), "duplicate emitted"
N_SUB = len(kept_paths)  # 6

# ---- Act 0: the rule ----
add(act=0, nodes=NODES, edges=EDGES, code="backtrack", line=0,
    intro="sorting groups equal values so a duplicate sits right next to its twin.",
    invariant="every node is itself a valid subset — not just the leaves.",
    note=f"Sort first: {RAW} -> {NUMS}. Now equal numbers are neighbors, which is "
    "what lets us spot a duplicate sibling in O(1).",
    active=[0], done={}, state=[["input", str(RAW)], ["sorted", str(NUMS)]])
add(act=0, code="backtrack", line=1,
    note="Unlike plain Subsets, we record path the moment we ENTER a call, so "
    "every node in the tree is a subset — the root is {} , its children add one "
    "element each, and so on.",
    active=[0], done={0: "{}"}, state=[["node = subset", "yes"]])
add(act=0, code="backtrack", line=3,
    note="The prune: inside one loop, a value equal to the previous sibling "
    "(nums[i]==nums[i-1] and i>start) is skipped — we already built every subset "
    "that starts with that value here, so retrying only remakes the same sets.",
    active=[0], done={0: "{}"}, state=[["skip when", "nums[i]==nums[i-1]"]])

# ---- Act 1: walk the tree, prunes visible ----
done = {}
found = 0
add(act=1, nodes=NODES, edges=EDGES, code="backtrack", line=0,
    intro="green badges accrue on every entered node; a ✕ marks a skipped twin.",
    invariant="a ✕ child would only remake a subset already produced by its sibling.",
    note="Run it. Each entered node lights green and records its subset; the "
    "second 2 at a level is skipped so we don't duplicate {2} or {2,2}.",
    active=[0], done={}, state=[["found", 0]])

# emit kept nodes in DFS order; whenever a kept node has a pruned child, show it
children = {}
for a, b, lbl in edges:
    children.setdefault(a, []).append((b, lbl))

emitted_pruned = set()
for oid in order:
    nd = nodes[oid]
    active = path_to(edges, oid)
    done[oid] = nd["val"]
    found += 1
    if nd["i"] is None:
        note = "Enter the root: record the empty subset {}."
        line = 1
    else:
        note = (f"Pick nums[i]={NUMS[nd['i']]} -> path becomes {nd['val']}, and "
                f"record it. ({found} of {N_SUB} subsets.)")
        line = 5
    add(act=1, code="backtrack", line=line, note=note,
        active=active, done=dict(done),
        state=[["path", nd["val"]], ["found", found]])
    # reveal any pruned siblings hanging off this node
    for cid, lbl in children.get(oid, []):
        if nodes[cid]["pruned"] and cid not in emitted_pruned:
            emitted_pruned.add(cid)
            done_show = dict(done); done_show[cid] = "✗"  # ✕
            add(act=1, code="backtrack", line=4,
                note=f"Here the next value equals its left sibling "
                     f"({nodes[cid]['reason']}) -> skip. It would only remake "
                     f"{nodes[cid]['val']}, already found.",
                active=active, done=done_show,
                state=[["skipped", nodes[cid]["val"]], ["found", found]])

add(act=1, code="backtrack", line=2,
    note=f"Tree exhausted: {N_SUB} unique subsets, and every skipped ✕ was a "
         "duplicate we correctly avoided.",
    active=[], done=dict(done),
    state=[["unique subsets", N_SUB], ["duplicates made", 0]],
    banner=f"{N_SUB} unique subsets from {NUMS} — no repeats")

# ============================ Act 2: heavy dup [2,2,2] ============================
RAW_E = [2, 2, 2]
NUMS_E, nodes_e, edges_e, order_e = build_tree(RAW_E)
NODES_E = render_nodes(nodes_e)
EDGES_E = render_edges(edges_e)
kept_e = [nodes_e[i]["path"] for i in order_e]
assert kept_e == _solution_subsets(RAW_E), (kept_e, _solution_subsets(RAW_E))
N_E = len(kept_e)  # 4: {},{2},{2,2},{2,2,2}

children_e = {}
for a, b, lbl in edges_e:
    children_e.setdefault(a, []).append((b, lbl))

add(act=2, nodes=NODES_E, edges=EDGES_E, code="backtrack", line=3,
    intro="with everything equal, only ONE child survives at each level.",
    invariant="the kept path is the single increasing spine; all else is a ✕.",
    note="Edge case: all identical, nums = [2,2,2]. At every level only the first "
    "copy is kept; every later equal sibling is pruned.",
    active=[0], done={}, state=[["input", str(RAW_E)]])
done_e = {}
found_e = 0
emitted_e = set()
for oid in order_e:
    nd = nodes_e[oid]
    active = path_to(edges_e, oid)
    done_e[oid] = nd["val"]
    found_e += 1
    add(act=2, code="backtrack", line=(1 if nd["i"] is None else 5),
        note=(f"Enter root -> {{}}." if nd["i"] is None
              else f"Take the first available 2 -> {nd['val']}."),
        active=active, done=dict(done_e),
        state=[["path", nd["val"]], ["found", found_e]])
    for cid, lbl in children_e.get(oid, []):
        if nodes_e[cid]["pruned"] and cid not in emitted_e:
            emitted_e.add(cid)
            show = dict(done_e); show[cid] = "✗"
            add(act=2, code="backtrack", line=4,
                note=f"Another 2 here equals its sibling -> skip; it would remake "
                     f"{nodes_e[cid]['val']}.",
                active=active, done=show,
                state=[["skipped", nodes_e[cid]["val"]], ["found", found_e]])

add(act=2, code="backtrack", line=2,
    note=f"All-equal input collapses to just {N_E} subsets — one per length "
         "(0..3) — because every branching duplicate was pruned.",
    active=[], done=dict(done_e),
    state=[["unique subsets", N_E]],
    banner="[2,2,2] -> 4 subsets: {}, {2}, {2,2}, {2,2,2}")

trace = {
    "player": "tree",
    "title": "Subsets II — every node is a subset, and a sibling-skip prunes duplicates",
    "acts": ["The rule", "Walk the tree (prunes visible)", "Edge case: all equal"],
    "code": {"backtrack": CODE},
    "legend": [["active", "current path"], ["good", "recorded subset / ✕ = pruned twin"]],
    "nodes": NODES, "edges": EDGES, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
