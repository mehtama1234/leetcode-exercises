"""Full-arc tree trace for Palindrome Partitioning (backtracking decision tree).

Backtracking has no wasteful brute baseline to beat — the tree IS the work — so
the arc is: the rule (cut only where the prefix is a palindrome) -> run the DFS
and watch the path walk the tree, leaves collecting valid partitions, non-
palindrome cuts pruned in place -> an edge case (all-equal string, nothing
pruned). We precompute every node's x,y in Python for s="aab". Each node is a
decision point at position `start`: its children are the candidate ends. A cut to
a palindromic prefix recurses; a non-palindromic prefix is shown pruned (✕) and
never recursed into. A leaf (start == n) is one finished partition. Mirrors
partition()/backtrack() in solution.py.
"""
import json
import os

XSTEP, YSTEP = 66, 88
frames = []

CODE = [
    "def backtrack(start):",
    "    if start == n:",
    "        result.append(path[:])   # a full partition",
    "        return",
    "    for end in range(start, n):",
    "        if is_palindrome(s, start, end):",
    "            path.append(s[start:end+1])  # choose",
    "            backtrack(end + 1)           # explore",
    "            path.pop()                   # un-choose",
]


def add(**f):
    frames.append(f)


def is_pal(s, lo, hi):
    """True if s[lo..hi] reads the same both ways (mirrors solution.is_palindrome)."""
    while lo < hi:
        if s[lo] != s[hi]:
            return False
        lo += 1
        hi -= 1
    return True


def build_tree(s):
    """Enumerate the cut decision tree; assign x,y by in-order sweep.

    Each real node carries a `start` position and the pieces cut so far. Its
    children are the candidate ends in range(start, n): a palindromic prefix
    becomes a real child (and recurses); a non-palindromic prefix becomes a
    pruned stub node (shown with a ✕, no recursion). Returns (nodes, edges, order)
    where order is the DFS visit sequence of ids matching solution.backtrack.
    """
    n = len(s)
    nodes = {}          # id -> dict
    edges = []          # (parent, child)
    order = []          # ids in DFS/loop order
    counter = [0]       # in-order x slot
    nid = [0]

    def label(pieces):
        return "·".join(pieces) if pieces else "root"

    def make(start, pieces):
        my = nid[0]; nid[0] += 1
        leaf = start == n
        node = {"start": start, "pieces": list(pieces), "leaf": leaf,
                "pruned": False, "piece": None,
                "val": label(pieces) if pieces else "start",
                "x": 0, "y": len(pieces) * YSTEP}
        nodes[my] = node
        order.append(my)
        if leaf:
            node["x"] = counter[0] * XSTEP; counter[0] += 1
            return my
        assigned_x = False
        for end in range(start, n):
            piece = s[start:end + 1]
            if is_pal(s, start, end):
                if not assigned_x and end > start:
                    node["x"] = counter[0] * XSTEP; counter[0] += 1
                    assigned_x = True
                pieces.append(piece)
                child = make(end + 1, pieces)
                pieces.pop()
                edges.append((my, child))
                if not assigned_x:
                    # first child was itself the leftmost; anchor after it
                    node["x"] = counter[0] * XSTEP; counter[0] += 1
                    assigned_x = True
            else:
                # pruned candidate: a real node in the picture, never recursed into
                pid = nid[0]; nid[0] += 1
                pruned = {"start": end + 1, "pieces": list(pieces) + [piece],
                          "leaf": False, "pruned": True, "piece": piece,
                          "val": "✕" + piece,
                          "x": counter[0] * XSTEP, "y": (len(pieces) + 1) * YSTEP}
                counter[0] += 1
                nodes[pid] = pruned
                order.append(pid)
                edges.append((my, pid))
        if not assigned_x:
            node["x"] = counter[0] * XSTEP; counter[0] += 1
        return my

    make(0, [])
    return nodes, edges, order


def render_nodes(nodes):
    return [{"id": k, "val": v["val"], "x": v["x"], "y": v["y"]} for k, v in nodes.items()]


def render_edges(edges):
    return [[a, b] for a, b in edges]


def path_to(edges, target):
    """ids on the root->target path, for the `active` highlight."""
    parent = {}
    for a, b in edges:
        parent[b] = a
    chain = [target]
    while chain[-1] in parent:
        chain.append(parent[chain[-1]])
    return chain[::-1]


def full(pieces):
    return "·".join(pieces)


# ---------- Act 0 + 1 scene: s = "aab" ----------
S = "aab"
nodes, edges, order = build_tree(S)
NODES = render_nodes(nodes)
EDGES = render_edges(edges)

# ---- Act 0: the rule ----
add(act=0, nodes=NODES, edges=EDGES, code="backtrack", line=5,
    intro="a cut is allowed only when the prefix it makes is itself a palindrome.",
    invariant="depth = number of pieces cut; every piece on a path is a palindrome.",
    note="The rule: at position start, try each end. Only cut where s[start..end] "
    "is a palindrome — any other prefix can never be part of a valid answer, so we "
    "don't recurse into it.",
    active=[0], done={}, state=[["string", S], ["allowed cut", "palindrome only"]])
add(act=0, code="backtrack", line=1,
    note="Reaching start == n means the whole string is cut into palindromes: "
    "record that partition. A ✕ marks a cut we refused because the prefix was not "
    "a palindrome.",
    active=[0], done={}, state=[["leaf", "start == n"], ["✕", "pruned cut"]])

# ---- Act 1: run the DFS on "aab" ----
done = {}
found = []
add(act=1, nodes=NODES, edges=EDGES, code="backtrack", line=0,
    intro="the active path is the pieces cut so far; ✕ nodes are refused cuts.",
    invariant="a green leaf shows a full cutting where every piece is a palindrome.",
    note="Run it on \"aab\". Watch the path try each cut; non-palindrome prefixes "
    "get pruned in place, and each time we reach the end we record the partition.",
    active=[0], done={}, state=[["found", 0]])
for oid in order:
    nd = nodes[oid]
    active = path_to(edges, oid)
    if nd["pruned"]:
        done[oid] = "✕"
        add(act=1, code="backtrack", line=5,
            note=f"Prefix \"{nd['piece']}\" (from position {nd['start'] - len(nd['piece'])}) "
                 f"is not a palindrome -> refuse this cut, don't recurse.",
            active=active[:-1] + [oid], done=dict(done),
            state=[["tried prefix", nd["piece"]], ["palindrome?", "no -> ✕"],
                   ["found", len(found)]])
    elif nd["leaf"]:
        part = full(nd["pieces"])
        done[oid] = part
        found.append(part)
        add(act=1, code="backtrack", line=2,
            note=f"start == n -> the whole string is cut into palindromes: record "
                 f"{part}. ({len(found)} of 2 so far.)",
            active=active, done=dict(done),
            state=[["partition", part], ["found", len(found)]])
    else:
        if nd["start"] == 0:
            note = "Start at position 0 with nothing cut yet."
            line = 0
        else:
            piece = nd["pieces"][-1]
            note = (f"Prefix \"{piece}\" is a palindrome -> cut it and recurse on the "
                    f"rest. Pieces so far: {full(nd['pieces'])}.")
            line = 6
        add(act=1, code="backtrack", line=line, note=note,
            active=active, done=dict(done),
            state=[["at position", nd["start"]],
                   ["pieces", full(nd["pieces"]) or "—"], ["found", len(found)]])
add(act=1, code="backtrack", line=2,
    note="Every branch explored: \"aab\" has exactly two palindrome partitions.",
    active=[], done=dict(done), state=[["partitions", len(found)]],
    banner="aab -> [a·a·b, aa·b]  (the 'aab' prefix was pruned — not a palindrome)")

# ---- Act 2: edge case — all-equal "aaa" (nothing pruned) ----
S2 = "aaa"
nodes2, edges2, order2 = build_tree(S2)
NODES2 = render_nodes(nodes2)
EDGES2 = render_edges(edges2)
done2 = {}
found2 = []
add(act=2, nodes=NODES2, edges=EDGES2, code="backtrack", line=4,
    intro="when every character is the same, every prefix is a palindrome — no ✕.",
    invariant="with no pruning, the count is the raw 2^(n-1) cuttings.",
    note="Edge case: \"aaa\". Every substring of equal characters is a palindrome, "
    "so no cut is ever refused — the full tree survives.",
    active=[0], done={}, state=[["string", S2], ["pruned", "none"]])
for oid in order2:
    nd = nodes2[oid]
    active = path_to(edges2, oid)
    if nd["leaf"]:
        part = full(nd["pieces"])
        done2[oid] = part
        found2.append(part)
        add(act=2, code="backtrack", line=2,
            note=f"Record {part}. ({len(found2)} of 4.)",
            active=active, done=dict(done2),
            state=[["partition", part], ["found", len(found2)]])
    elif nd["start"] != 0:
        piece = nd["pieces"][-1]
        add(act=2, code="backtrack", line=6,
            note=f"\"{piece}\" is a palindrome -> cut and recurse. Pieces: {full(nd['pieces'])}.",
            active=active, done=dict(done2),
            state=[["at position", nd["start"]], ["pieces", full(nd["pieces"])],
                   ["found", len(found2)]])
add(act=2, code="backtrack", line=2,
    note="No cut was ever refused, so all 2^(3-1) = 4 cuttings are valid partitions.",
    active=[], done=dict(done2), state=[["partitions", len(found2)]],
    banner="aaa -> 4 partitions = 2^(n-1), nothing pruned")

# --- correctness check against the real solution before writing ---
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "sol", os.path.join(os.path.dirname(__file__), "solution.py"))
_sol = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_sol)
assert {tuple(p) for p in _sol.partition(S)} == {("a", "a", "b"), ("aa", "b")}
assert sorted(found) == sorted(full(list(p)) for p in _sol.partition(S)), (found,)
assert len(found2) == len(_sol.partition(S2)) == 4, (found2,)
assert sorted(found2) == sorted(full(list(p)) for p in _sol.partition(S2))

trace = {
    "player": "tree",
    "title": "Palindrome Partitioning — cut only at palindromes, walked as a decision tree",
    "acts": ["The rule", "Walk the decision tree", "Edge case: all-equal string"],
    "code": {"backtrack": CODE},
    "legend": [["active", "current path"], ["good", "finished partition / valid cut"]],
    "nodes": NODES, "edges": EDGES, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
