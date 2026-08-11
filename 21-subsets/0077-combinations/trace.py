"""Full-arc tree trace for Combinations (backtracking decision tree).

Backtracking has no wasteful brute baseline — the tree IS the work — so the arc
is: the rule (forward-only pick, prune when too few numbers remain) -> run the
DFS for n=4,k=2 and watch the path build combinations, with a dead branch pruned
in plain sight -> an edge case (k == n, no branching at all).

We precompute every node's x,y in Python. Each node is a choice of the next
number i; the root is "start" (path empty). Because order doesn't matter we only
ever move to numbers larger than the last, so each combination is visited once.
Depth = len(path). The prune from solution.py: last_ok = n - (k - len(path)) + 1;
any candidate i > last_ok can't leave enough numbers to reach size k, so it's a
dead branch — we draw it with a '✕' badge and never recurse into it. Mirrors
combine()/backtrack() in solution.py.
"""
import json
import os

XSTEP, YSTEP = 62, 90
frames = []

CODE = [
    "def backtrack(start):",
    "    if len(path) == k:",
    "        result.append(path[:])",
    "        return",
    "    need = k - len(path)",
    "    last_ok = n - need + 1",
    "    for i in range(start, last_ok + 1):",
    "        path.append(i)      # choose",
    "        backtrack(i + 1)    # explore",
    "        path.pop()          # un-choose",
]


def add(**f):
    frames.append(f)


def build_tree(n, k):
    """Enumerate the combination decision tree; assign x,y by a left-to-right sweep.

    node = {id, val, x, y, path, start, leaf?, pruned?, pick (number chosen to
    reach this node)}. A node is created for EVERY candidate i in range(start, n+1)
    so the pruned ones (i > last_ok) are visible; pruned nodes are drawn but not
    recursed into. Returns (nodes, edges, order) where order is DFS visit order
    matching the solution (candidates ascending, valid ones recursed depth-first).
    """
    nodes = {}          # id -> dict
    edges = []          # (parent, child, label)
    order = []          # ids in DFS visit order
    counter = [0]       # x slot (leftmost-leaf sweep)
    nid = [0]

    def label(path):
        return "[" + ",".join(str(x) for x in path) + "]" if path else "[ ]"

    def make(start, path, pick, pruned):
        my = nid[0]; nid[0] += 1
        leaf = (not pruned) and len(path) == k
        node = {"start": start, "path": list(path), "pick": pick, "leaf": leaf,
                "pruned": pruned, "val": label(path), "x": 0,
                "y": len(path) * YSTEP}
        nodes[my] = node
        order.append(my)

        if pruned or leaf:
            node["x"] = counter[0] * XSTEP; counter[0] += 1
            return my

        # interior node: loop candidates i in range(start, n+1). Valid ones
        # (i <= last_ok) recurse; the rest are pruned leaves shown with '✕'.
        need = k - len(path)
        last_ok = n - need + 1
        first_child = None
        for i in range(start, n + 1):
            child_pruned = i > last_ok
            path.append(i)
            child = make(i + 1, path, i, child_pruned)
            path.pop()
            edges.append((my, child, ("pick " + str(i)) if not child_pruned
                          else ("skip " + str(i))))
            if first_child is None:
                first_child = child
        # center this interior node over its children's x extent
        child_xs = [nodes[c]["x"] for (p, c, _) in edges if p == my]
        node["x"] = (min(child_xs) + max(child_xs)) // 2
        return my

    make(1, [], None, False)
    return nodes, edges, order


def render_nodes(nodes):
    return [{"id": k, "val": v["val"], "x": v["x"], "y": v["y"]}
            for k, v in nodes.items()]


def render_edges(edges):
    return [[a, b] for a, b, _ in edges]


def path_to(nodes, edges, target):
    """ids on the root->target path, for the `active` highlight."""
    parent = {}
    for a, b, _ in edges:
        parent[b] = a
    chain = [target]
    while chain[-1] in parent:
        chain.append(parent[chain[-1]])
    return chain[::-1]


def combo_str(path):
    return "{" + ",".join(str(x) for x in path) + "}"


N, K = 4, 2
nodes, edges, order = build_tree(N, K)
NODES = render_nodes(nodes)
EDGES = render_edges(edges)

# sanity: verify the leaves equal combine(4,2) exactly
import math
leaf_combos = sorted(tuple(nodes[i]["path"]) for i in nodes if nodes[i]["leaf"])
assert len(leaf_combos) == math.comb(N, K) == 6, (leaf_combos,)
assert leaf_combos == [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)], leaf_combos
pruned_ids = [i for i in nodes if nodes[i]["pruned"]]
assert len(pruned_ids) >= 1, "expected at least one pruned branch"

# ---- Act 0: the rule ----
add(act=0, nodes=NODES, edges=EDGES, code="backtrack", line=0,
    intro="each level adds one number; we only ever move to larger numbers.",
    invariant="depth = how many numbers chosen; a leaf at depth k is a full combo.",
    note="The rule: pick numbers in increasing order so each combination is built "
    "exactly once. From position 'start' we try each candidate number, then recurse "
    "starting just past it.",
    active=[0], done={},
    state=[["n, k", f"{N}, {K}"], ["order", "increasing"]])
add(act=0, code="backtrack", line=5,
    note="The prune: with 'need' slots left, any start above last_ok = n - need + 1 "
    "leaves too few numbers to finish. Those dead branches are marked ✕ and never "
    "explored.",
    active=[0], done={},
    state=[["need", K], ["last_ok", N - K + 1]])

# ---- Act 1: run the DFS for n=4, k=2 ----
done = {}
found = []
add(act=1, nodes=NODES, edges=EDGES, code="backtrack", line=0,
    intro="the active path is the numbers chosen so far; leaves light green, dead "
    "branches show ✕.",
    invariant="a green leaf holds exactly the numbers picked on the way down.",
    note="Run it. Watch the path grow to size k, and watch one branch get pruned "
    "before it wastes any work.",
    active=[0], done={}, state=[["found", 0]])

for oid in order:
    nd = nodes[oid]
    active = path_to(nodes, edges, oid)
    if nd["pruned"]:
        done[oid] = "✕"
        need = K - (len(nd["path"]) - 1)
        last_ok = N - need + 1
        add(act=1, code="backtrack", line=6,
            note=f"Candidate {nd['pick']} is past last_ok = {last_ok}: only "
                 f"{N - nd['pick'] + 1} number(s) remain but {need} slot(s) need "
                 f"filling. Prune — don't recurse.",
            active=active, done=dict(done),
            state=[["candidate", nd["pick"]], ["pruned", "✕"],
                   ["found", len(found)]])
    elif nd["leaf"]:
        done[oid] = combo_str(nd["path"])
        found.append(tuple(nd["path"]))
        add(act=1, code="backtrack", line=2,
            note=f"Path reached size k = {K} -> record the combination "
                 f"{combo_str(nd['path'])}. ({len(found)} of 6.)",
            active=active, done=dict(done),
            state=[["combination", combo_str(nd["path"])], ["found", len(found)]])
    else:
        if nd["pick"] is None:
            note = (f"Start at the root, path empty. Try candidates from 1, "
                    f"stopping at last_ok.")
            line = 0
        else:
            note = (f"Pick {nd['pick']}: path is now {combo_str(nd['path'])}. "
                    f"Recurse starting past {nd['pick']}.")
            line = 7
        add(act=1, code="backtrack", line=line,
            note=note, active=active, done=dict(done),
            state=[["path", combo_str(nd["path"])], ["found", len(found)]])

add(act=1, code="backtrack", line=2,
    note="Every reachable leaf collected -> all 6 combinations, and one whole "
    "branch was skipped for free.",
    active=[], done=dict(done),
    state=[["combinations", len(found)], ["= C(4,2)", 6]],
    banner="6 combinations = C(4,2); the ✕ branch was pruned")

# ---- Act 2: edge case k == n ----
NE, KE = 3, 3
nodes_e, edges_e, order_e = build_tree(NE, KE)
NODES_E = render_nodes(nodes_e)
EDGES_E = render_edges(edges_e)
leaf_e = sorted(tuple(nodes_e[i]["path"]) for i in nodes_e if nodes_e[i]["leaf"])
assert leaf_e == [(1, 2, 3)] and math.comb(NE, KE) == 1, leaf_e

add(act=2, nodes=NODES_E, edges=EDGES_E, code="backtrack", line=5,
    intro="when k == n there is no room to choose — every number must be taken.",
    invariant="last_ok = start at every level, so the tree is a single path.",
    note="Edge case: n = 3, k = 3. With need == numbers remaining, last_ok always "
    "equals start, so there is never a second candidate — the tree is one straight "
    "chain.",
    active=[0], done={}, state=[["n, k", "3, 3"], ["branching", "none"]])

done_e = {}
found_e = []
for oid in order_e:
    nd = nodes_e[oid]
    active = path_to(nodes_e, edges_e, oid)
    if nd["leaf"]:
        done_e[oid] = combo_str(nd["path"])
        found_e.append(tuple(nd["path"]))
        add(act=2, code="backtrack", line=2,
            note=f"The single path reaches size 3 -> the only combination "
                 f"{combo_str(nd['path'])}.",
            active=active, done=dict(done_e),
            state=[["combination", combo_str(nd["path"])], ["found", 1]])
    else:
        if nd["pick"] is None:
            note = "Root: only candidate is 1 (last_ok = 1)."
            line = 0
        else:
            note = f"Forced pick {nd['pick']}: path {combo_str(nd['path'])}."
            line = 7
        add(act=2, code="backtrack", line=line, note=note,
            active=active, done=dict(done_e),
            state=[["path", combo_str(nd["path"])]])

add(act=2, code="backtrack", line=2,
    note="k == n gives exactly one combination: all n numbers, no choices to make.",
    active=[], done=dict(done_e),
    state=[["combinations", 1], ["= C(3,3)", 1]],
    banner="k == n -> exactly one combination: {1,2,3}")

trace = {
    "player": "tree",
    "title": "Combinations — pick numbers in order, prune the dead branches",
    "acts": ["The rule", "Walk the tree (n=4, k=2)", "Edge case: k == n"],
    "code": {"backtrack": CODE},
    "legend": [["active", "current path"], ["good", "finished combination / ✕ pruned"]],
    "nodes": NODES, "edges": EDGES, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
