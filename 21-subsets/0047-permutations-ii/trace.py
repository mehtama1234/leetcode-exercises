"""Full-arc tree trace for Permutations II (backtracking decision tree with a
duplicate-sibling prune).

Backtracking has no wasteful brute baseline — the tree IS the work — so the arc
is: the rule (sort, then skip a duplicate sibling unless its equal predecessor is
already placed) -> run the DFS on [1,1,2] with the pruned branches made visible
-> an edge case (all identical, where almost everything is pruned).

We precompute every node's x,y in Python. Each non-root node is a "place nums[i]"
choice; depth = len(path). A leaf (len(path) == n) is one finished permutation.
Nodes that the skip rule refuses are still drawn (so the prune is visible) and
badged "✕". Mirrors backtrack()/permute_unique() in solution.py exactly.
"""
import json
import os

XSTEP, YSTEP = 62, 88
frames = []

CODE = [
    "def backtrack():",
    "    if len(path) == n:",
    "        result.append(path[:])",
    "        return",
    "    for i in range(n):",
    "        if used[i]:",
    "            continue",
    "        if i>0 and nums[i]==nums[i-1] and not used[i-1]:",
    "            continue          # skip duplicate sibling",
    "        used[i] = True        # choose",
    "        path.append(nums[i])",
    "        backtrack()           # explore",
    "        path.pop()            # un-choose",
    "        used[i] = False",
]


def add(**f):
    frames.append(f)


def build_tree(nums):
    """Enumerate the permutation decision tree EXACTLY as solution.py walks it,
    including the duplicate-sibling branches the skip rule refuses (drawn so the
    prune is visible).

    node = {id, val (the path so far), x, y, leaf?, pruned?, placed (value just
    placed or None for root), from_i (index chosen)}.
    Returns (nodes, edges, order) with order = DFS visit sequence of ids.
    x is assigned by an in-order sweep over the children (leaves left-to-right).
    """
    nums = sorted(nums)
    n = len(nums)
    nodes = {}
    edges = []          # (parent, child, label)
    order = []
    counter = [0]       # leaf x-slot counter (in-order)
    nid = [0]
    used = [False] * n
    path = []

    def label(p):
        return "[" + ",".join(str(x) for x in p) + "]" if p else "start"

    def make(placed, from_i, parent):
        my = nid[0]; nid[0] += 1
        leaf = len(path) == n
        node = {"placed": placed, "from_i": from_i, "leaf": leaf,
                "pruned": False, "val": label(path), "x": 0,
                "y": len(path) * YSTEP}
        nodes[my] = node
        order.append(my)
        if parent is not None:
            edges.append((parent, my, "" if placed is None else str(placed)))
        if leaf:
            node["x"] = counter[0] * XSTEP; counter[0] += 1
            return my
        # branch over indices, mirroring the solution's loop and skips
        first_child = True
        for i in range(n):
            if used[i]:
                continue
            if i > 0 and nums[i] == nums[i - 1] and not used[i - 1]:
                # pruned duplicate sibling: draw a stub node so it's visible
                pid = nid[0]; nid[0] += 1
                pnode = {"placed": nums[i], "from_i": i, "leaf": False,
                         "pruned": True, "val": label(path + [nums[i]]),
                         "x": counter[0] * XSTEP, "y": (len(path) + 1) * YSTEP}
                counter[0] += 1
                nodes[pid] = pnode
                order.append(pid)
                edges.append((my, pid, str(nums[i])))
                if first_child:
                    node["x"] = pnode["x"]; first_child = False
                continue
            used[i] = True
            path.append(nums[i])
            child = make(nums[i], i, my)
            path.pop()
            used[i] = False
            if first_child:
                node["x"] = nodes[child]["x"]; first_child = False
        # center parent over its child span if it had real children
        return my

    make(None, None, None)
    # recenter every internal node over the midpoint of its own children
    kids = {}
    for a, b, _ in edges:
        kids.setdefault(a, []).append(b)
    # process deepest first so children are settled
    for pid in sorted(nodes, key=lambda k: -nodes[k]["y"]):
        if pid in kids:
            xs = [nodes[c]["x"] for c in kids[pid]]
            nodes[pid]["x"] = (min(xs) + max(xs)) / 2
    return nodes, edges, order


def render_nodes(nodes):
    return [{"id": k, "val": v["val"], "x": v["x"], "y": v["y"]} for k, v in nodes.items()]


def render_edges(edges):
    return [[a, b] for a, b, _ in edges]


def path_to(edges, target):
    """ids on the root->target path, for the `active` highlight."""
    parent = {}
    for a, b, _ in edges:
        parent[b] = a
    chain = [target]
    while chain[-1] in parent:
        chain.append(parent[chain[-1]])
    return chain[::-1]


def verify(nums):
    """Independently confirm the tree's leaves == solution's output (as a set),
    with no duplicate orderings."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "sol", os.path.join(os.path.dirname(__file__), "solution.py"))
    sol = importlib.util.module_from_spec(spec); spec.loader.exec_module(sol)
    nodes, edges, order = build_tree(nums)
    leaves = []
    for nd in nodes.values():
        if nd["leaf"]:
            inner = nd["val"][1:-1]
            leaves.append(tuple(int(x) for x in inner.split(",")) if inner else ())
    got = [tuple(p) for p in sol.permute_unique(nums)]
    assert set(leaves) == set(got), (nums, sorted(leaves), sorted(got))
    assert len(leaves) == len(set(leaves)), (nums, "duplicate leaf emitted")
    assert len(got) == len(set(got)), (nums, "solution duplicate")
    return len(got)


NUMS = [1, 1, 2]
assert verify(NUMS) == 3
assert verify([2, 2, 2]) == 1
nodes, edges, order = build_tree(NUMS)
NODES = render_nodes(nodes)
EDGES = render_edges(edges)

# ---- Act 0: the rule ----
add(act=0, nodes=NODES, edges=EDGES, code="backtrack", line=0,
    intro="each level places one unused number; equal copies are kept in order.",
    invariant="depth = how many numbers placed; a bottom-row leaf is a full permutation.",
    note="The rule: sort so equal values sit together, then at each slot try every "
    "unused number — but refuse a value equal to the one just before it in the "
    "array unless that earlier copy is already placed.",
    active=[0], done={}, state=[["sorted nums", str(sorted(NUMS))], ["slots", len(NUMS)]])
add(act=0, code="backtrack", line=7,
    note="That single skip is the whole trick: it fixes one order among equal "
    "copies, so the same arrangement is never built two different ways. Skipped "
    "branches are marked ✕.",
    active=[0], done={}, state=[["prune", "dup sibling"], ["unique perms", 3]])

# ---- Act 1: run the DFS on [1,1,2] ----
done = {}
found = []
add(act=1, nodes=NODES, edges=EDGES, code="backtrack", line=0,
    intro="the active path is the numbers placed so far; leaves light green, ✕ = pruned.",
    invariant="a green leaf holds one full ordering; no two greens are equal.",
    note="Run it on [1,1,2]. Watch a duplicate sibling get pruned (✕) so we don't "
    "rebuild the same ordering.",
    active=[0], done={}, state=[["placed", "start"], ["found", 0]])
for oid in order:
    nd = nodes[oid]
    active = path_to(edges, oid)
    if nd["pruned"]:
        done[oid] = "✕"
        # active path should stop at the parent (this branch isn't taken)
        parent_path = active[:-1]
        add(act=1, code="backtrack", line=8,
            note=f"Trying to place another {nd['placed']} here would repeat an "
                 f"ordering — its equal earlier copy isn't placed yet. Skip it (✕).",
            active=parent_path, done=dict(done),
            state=[["would place", nd["placed"]], ["decision", "prune"], ["found", len(found)]])
    elif nd["leaf"]:
        done[oid] = nd["val"]
        found.append(nd["val"])
        add(act=1, code="backtrack", line=2,
            note=f"All {len(NUMS)} slots filled -> record the permutation {nd['val']}. "
                 f"({len(found)} of 3 unique so far.)",
            active=active, done=dict(done),
            state=[["permutation", nd["val"]], ["found", len(found)]])
    elif nd["placed"] is None:
        add(act=1, code="backtrack", line=4,
            note="At the root, no number placed yet — loop over the choices.",
            active=active, done=dict(done),
            state=[["placed", "start"], ["found", len(found)]])
    else:
        add(act=1, code="backtrack", line=10,
            note=f"Place {nd['placed']} (choose): path is now {nd['val']}. Recurse "
                 f"to fill the next slot.",
            active=active, done=dict(done),
            state=[["placed", nd["placed"]], ["path", nd["val"]], ["found", len(found)]])
add(act=1, code="backtrack", line=2,
    note="Tree exhausted -> exactly 3 unique permutations. The ✕ branch is what "
         "kept [1,1,2] built from the second 1 first from ever appearing twice.",
    active=[], done=dict(done),
    state=[["unique perms", 3]],
    banner="3 unique permutations of [1,1,2] (a naive n! would give 6, half duplicates)")

# ---- Act 2: edge case — all identical [2,2,2] ----
NUMS_E = [2, 2, 2]
nodes_e, edges_e, order_e = build_tree(NUMS_E)
NODES_E = render_nodes(nodes_e)
EDGES_E = render_edges(edges_e)
add(act=2, nodes=NODES_E, edges=EDGES_E, code="backtrack", line=7,
    intro="with every value equal, only ONE order survives — the rest are ✕.",
    invariant="a duplicate may only follow its already-placed twin, so one chain.",
    note="Edge case: [2,2,2]. At every slot only the leftmost unused 2 is allowed; "
    "each other 2 is a duplicate sibling and gets pruned.",
    active=[0], done={}, state=[["all equal", "2,2,2"], ["expected", 1]])
done_e = {}
found_e = []
for oid in order_e:
    nd = nodes_e[oid]
    active = path_to(edges_e, oid)
    if nd["pruned"]:
        done_e[oid] = "✕"
        add(act=2, code="backtrack", line=8,
            note=f"Another 2 here would just repeat the one ordering — skip (✕).",
            active=active[:-1], done=dict(done_e),
            state=[["would place", 2], ["decision", "prune"]])
    elif nd["leaf"]:
        done_e[oid] = nd["val"]
        found_e.append(nd["val"])
        add(act=2, code="backtrack", line=2,
            note=f"The one surviving chain fills all slots -> {nd['val']}.",
            active=active, done=dict(done_e),
            state=[["permutation", nd["val"]], ["found", 1]])
    elif nd["placed"] is not None:
        add(act=2, code="backtrack", line=10,
            note=f"Place the leftmost unused 2: path {nd['val']}.",
            active=active, done=dict(done_e),
            state=[["path", nd["val"]]])
add(act=2, code="backtrack", line=2,
    note="Every duplicate sibling pruned -> exactly one permutation of all-equal "
         "input, instead of 3! = 6 identical copies.",
    active=[], done=dict(done_e),
    state=[["unique perms", 1]],
    banner="All identical -> exactly 1 permutation")

trace = {
    "player": "tree",
    "title": "Permutations II — place each number, prune duplicate siblings",
    "acts": ["The rule", "Walk the tree ([1,1,2])", "Edge case: all identical"],
    "code": {"backtrack": CODE},
    "legend": [["active", "current path"], ["good", "finished permutation (leaf)"]],
    "nodes": NODES, "edges": EDGES, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
