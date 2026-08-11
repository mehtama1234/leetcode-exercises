"""Rich full-arc trace for Combination Sum (tree renderer as a DECISION TREE).

Backtracking has no wasteful brute baseline worth animating, so the arc is:
the rule (ordering + reuse) -> run the decision tree -> a pruning edge case.

Each tree node is a *choice*: "add this candidate next". A branch that reaches
remaining==0 is a hit (badge OK); a branch pruned because the candidate exceeds
remaining is dead (badge X); the node we are currently extending is `active`.
Node x,y positions are computed here in Python. Mirrors backtrack() in
solution.py. Writes trace.json.
"""
import json
import os

XSTEP, YSTEP = 66, 92
frames = []

CODE = [
    "def backtrack(start, remaining):",
    "    if remaining == 0:",
    "        result.append(path.copy())",
    "        return",
    "    for i in range(start, len(candidates)):",
    "        c = candidates[i]",
    "        if c > remaining:",
    "            break",
    "        path.append(c)",
    "        backtrack(i, remaining - c)",
    "        path.pop()",
]


def add(**f):
    frames.append(f)


# ---------------------------------------------------------------------------
# We build the decision tree incrementally: every node we create gets a stable
# id and an (x, y). Layout is a simple "next free column" in-order sweep — we
# assign x by a running leaf counter at the moment a node is placed, y by depth.
# The nodes/edges lists grow as the search descends, and each frame ships the
# current snapshot so the tree literally draws itself branch by branch.
# ---------------------------------------------------------------------------

candidates = [2, 3, 6, 7]  # already sorted (solution sorts first)
TARGET = 7

nodes = []          # [{id,val,x,y}]
edges = []          # [[parent,child]]
done = {}           # id -> badge text ("OK" hit, "X" pruned/dead, number = remaining)
_col = [0]          # running x column for leaf placement


def new_node(val, depth, parent):
    nid = len(nodes)
    x = _col[0] * XSTEP
    _col[0] += 1
    nodes.append({"id": nid, "val": val, "x": x, "y": depth * YSTEP})
    if parent is not None:
        edges.append([parent, nid])
    return nid


def snap():
    return [dict(n) for n in nodes], [list(e) for e in edges]


# root: the empty combination, "remaining = target"
root = new_node("·", 0, None)

# ---- Act 0: the rule ----
n, e = snap()
add(act=0, nodes=n, edges=e, code="main", line=4,
    intro="each node is a choice — 'add this candidate next'; a branch dies "
    "when the candidate overshoots what's left.",
    invariant="every path is non-decreasing, so no multiset is built twice.",
    note="Rule: at each step pick a candidate to add, but never look left of "
    "where you started. That ordering makes each combination appear once. "
    "Candidates are sorted [2,3,6,7], target 7.",
    active=[root], done={}, state=[["target", TARGET], ["rule", "pick >= start"]])
add(act=0, code="main", line=6,
    note="Because they're sorted, the moment a candidate is bigger than what's "
    "left, every later candidate is too — so we prune the whole rest.",
    active=[root], done={}, state=[["prune when", "c > remaining"]])


# ---- Act 1: run the decision tree ----
def backtrack(start, remaining, parent, depth, act, path):
    """Mirror of solution.backtrack, emitting a frame per choice."""
    if remaining == 0:
        done[parent] = "OK"
        n, e = snap()
        add(act=act, nodes=n, edges=e, code="main", line=2,
            note=f"remaining hit 0 — record {list(path)}. A real combination.",
            active=[], done=dict(done),
            state=[["found", str(list(path))], ["sum", TARGET]])
        return
    for i in range(start, len(candidates)):
        c = candidates[i]
        child = new_node(c, depth, parent)
        if c > remaining:
            # pruned: this and every later candidate are too big
            done[child] = "X"
            n, e = snap()
            add(act=act, nodes=n, edges=e, code="main", line=7,
                note=f"try {c}: {c} > {remaining} left -> too big. Sorted, so stop "
                f"this whole fan of choices.",
                active=[child], done=dict(done),
                state=[["at", c], ["remaining", remaining], ["action", "prune + break"]])
            break
        # take it
        path.append(c)
        n, e = snap()
        add(act=act, nodes=n, edges=e, code="main", line=9,
            note=f"take {c}: path {list(path)}, remaining {remaining} - {c} = {remaining - c}.",
            active=[child], done=dict(done),
            state=[["take", c], ["path", str(list(path))], ["remaining", remaining - c]])
        backtrack(i, remaining - c, child, depth + 1, act, path)  # i, not i+1: reuse allowed
        path.pop()
        if done.get(child) not in ("OK",):
            done[child] = "X"  # branch explored, nothing more here
        n, e = snap()
        add(act=act, nodes=n, edges=e, code="main", line=10,
            note=f"undo {c}; back up and try the next candidate from here.",
            active=[parent] if parent is not None else [], done=dict(done),
            state=[["pop", c], ["back to remaining", remaining]])


n, e = snap()
add(act=1, nodes=n, edges=e, code="main", line=0,
    intro="watch the tree grow: green-ish OK = a hit, X = a dead/pruned branch.",
    invariant="a node's badge appears only once its whole subtree is finished.",
    note="Run it from the root with remaining = 7. Each downward step commits to "
    "a candidate; each X is a branch we correctly abandon.",
    active=[root], done={}, state=[["start remaining", TARGET]])
backtrack(0, TARGET, root, 1, 1, [])
done[root] = "OK"
n, e = snap()
add(act=1, nodes=n, edges=e, code="main", line=0,
    note="The whole tree is explored. Two branches reached 0: [2,2,3] and [7]. "
    "Everything else was pruned or exhausted.",
    active=[], done=dict(done),
    state=[["combinations", "[2,2,3], [7]"], ["target", TARGET]],
    banner="Combination Sum([2,3,6,7], 7) = [[2,2,3], [7]]")

# ---- Act 2: pruning edge case ----
# candidates [2], target 1 -> the very first choice overshoots: no combination.
nodes2, edges2, done2, _col2 = [], [], {}, [0]


def nn2(val, depth, parent):
    nid = len(nodes2)
    x = _col2[0] * XSTEP
    _col2[0] += 1
    nodes2.append({"id": nid, "val": val, "x": x, "y": depth * YSTEP})
    if parent is not None:
        edges2.append([parent, nid])
    return nid


def snap2():
    return [dict(n) for n in nodes2], [list(e) for e in edges2]


r2 = nn2("·", 0, None)
n, e = snap2()
add(act=2, nodes=n, edges=e, code="main", line=6,
    intro="when the smallest candidate already overshoots, the search dies at "
    "the root — no work wasted.",
    invariant="pruning happens on the first choice, not after building a path.",
    note="Edge case: candidates [2], target 1. The only candidate is 2.",
    active=[r2], done={}, state=[["target", 1], ["candidates", "[2]"]])
c2 = nn2(2, 1, r2)
done2[c2] = "X"
n, e = snap2()
add(act=2, nodes=n, edges=e, code="main", line=7,
    note="try 2: 2 > 1 left -> too big. break. There's nothing smaller to try, "
    "so no combination exists.",
    active=[c2], done=dict(done2),
    state=[["at", 2], ["remaining", 1], ["result", "[]"]],
    banner="No subset of [2] sums to 1 -> []")

trace = {
    "player": "tree",
    "title": "Combination Sum - a decision tree that prunes overshoots",
    "acts": ["The rule", "Run the decision tree", "Edge: prune at the root"],
    "code": {"main": CODE},
    "legend": [["active", "choice we're extending now"],
               ["good", "OK = branch reached the target; X = pruned / exhausted"]],
    "nodes": [dict(nodes[0])], "edges": [], "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
