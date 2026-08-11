"""Full-arc tree trace for N-Queens (backtracking decision tree, heavy pruning).

Backtracking has no wasteful brute baseline — the tree IS the work, and the whole
point here is the *pruning*: most column choices at a row are under attack and die
instantly. The arc is: the rule (one queen per row, prune on column/diagonal
clash) -> walk n=4 down the winning branch, watching attacked columns get pruned
and a valid board appear -> an edge case n=3 where every branch is pruned and
nothing survives.

We precompute every node's x,y in Python. Each level is a board row; each node is
a column choice for that row. A PLACED column recurses to the next row; an
ATTACKED column is a pruned leaf (badge "x"). A path that reaches row == n is a
solution (badge "ok"). The tree renderer only styles nodes as active / resolved,
so pruned and solved leaves are told apart by their badge and the note. To keep it
legible we render the row0 = column-1 branch (the one that reaches the first n=4
solution) with all its siblings; Act 2 shows the full, all-pruned n=3 tree.
Mirrors backtrack() in solution.py: `col in cols or (row-col) in diag or
(row+col) in anti_diag` prunes.
"""
import json
import os

XSTEP, YSTEP = 62, 84
frames = []

CODE = [
    "def backtrack(row):",
    "    if row == n:",
    "        result.append(build_board())",
    "        return",
    "    for col in range(n):",
    "        if col in cols or (row-col) in diag or (row+col) in anti_diag:",
    "            continue                 # under attack -> prune",
    "        cols.add(col); diag.add(row-col); anti_diag.add(row+col)",
    "        placement.append(col)",
    "        backtrack(row + 1)          # explore next row",
    "        placement.pop()             # un-choose",
]


def add(**f):
    frames.append(f)


def board_lines(placement, n):
    return ["." * c + "Q" + "." * (n - c - 1) for c in placement]


def build_tree(n, restrict_row0=None):
    """Enumerate the decision tree exactly as backtrack() explores it.

    Each node picks a column for its row. Attacked columns become pruned leaves;
    legal columns recurse. `restrict_row0`, if given, is the single column allowed
    at row 0 (so we render just the illustrative branch). Assigns x by an in-order
    sweep and y by row depth. Returns (nodes, edges, order).

    node fields: row, col, placement (cols chosen incl. this), kind
    ('place'|'prune'|'sol'|'root'), reason (attack reasons for prunes), val, x, y.
    """
    nodes = {}
    edges = []
    order = []
    counter = [0]
    nid = [0]

    def attack_reasons(row, col, cols, diag, adiag):
        r = []
        if col in cols:
            r.append("same column")
        if (row - col) in diag:
            r.append("down-diagonal")
        if (row + col) in adiag:
            r.append("up-diagonal")
        return r

    def make(row, col, placement, cols, diag, adiag, kind):
        my = nid[0]; nid[0] += 1
        if kind == "root":
            val = "start"
        elif kind == "sol":
            val = "ok"
        else:
            val = "c" + str(col)          # the column chosen at this row
        # y: root sits on its own top level (row -1 -> y 0); board row r -> y (r+1)*YSTEP
        depth = 0 if kind == "root" else (row + 1)
        node = {"row": row, "col": col, "placement": list(placement),
                "kind": kind, "reason": [], "val": val,
                "x": 0, "y": depth * YSTEP}
        nodes[my] = node
        order.append(my)

        if kind in ("prune", "sol"):
            node["x"] = counter[0] * XSTEP; counter[0] += 1
            return my

        # kind == 'root' or 'place': recurse over the children's row.
        # For root the children live at row 0; for a placed queen at `row`,
        # children live at row+1.
        children_row = 0 if kind == "root" else row + 1

        child_xs = []
        if children_row == n:
            # placing filled the board -> a solution leaf child
            child = make(children_row, -1, placement, cols, diag, adiag, "sol")
            edges.append((my, child))
            child_xs.append(nodes[child]["x"])
        else:
            for c in range(n):
                if restrict_row0 is not None and children_row == 0 and c not in restrict_row0:
                    continue
                reasons = attack_reasons(children_row, c, cols, diag, adiag)
                if reasons:
                    child = make(children_row, c, placement, cols, diag, adiag, "prune")
                    nodes[child]["reason"] = reasons
                    edges.append((my, child))
                else:
                    child = make(children_row, c, placement + [c],
                                 cols | {c}, diag | {children_row - c},
                                 adiag | {children_row + c}, "place")
                    edges.append((my, child))
                child_xs.append(nodes[child]["x"])

        # center a parent over the span of its children (keeps edges readable)
        node["x"] = (min(child_xs) + max(child_xs)) // 2 if child_xs else counter[0] * XSTEP
        return my

    make(-1, -1, [], set(), set(), set(), "root")
    return nodes, edges, order


def render_nodes(nodes):
    return [{"id": k, "val": v["val"], "x": v["x"], "y": v["y"]} for k, v in nodes.items()]


def render_edges(edges):
    return [[a, b] for a, b in edges]


def path_to(edges, target):
    parent = {}
    for a, b in edges:
        parent[b] = a
    chain = [target]
    while chain[-1] in parent:
        chain.append(parent[chain[-1]])
    return chain[::-1]


# ---------- the n=4 winning branch (row 0 = column 1) ----------
N = 4
nodes, edges, order = build_tree(N, restrict_row0={1})
NODES = render_nodes(nodes)
EDGES = render_edges(edges)
ROOT = order[0]

# ---- Act 0: the rule ----
add(act=0, nodes=NODES, edges=EDGES, code="backtrack", line=5,
    intro="one queen per row; a column dies the instant it shares a file or "
    "diagonal with a queen already placed.",
    invariant="row conflicts are impossible — we place exactly one queen per row.",
    note="The rule: put one queen in each row. Before committing a column, check "
    "three O(1) sets — same column, the down-diagonal (row-col), the up-diagonal "
    "(row+col). Any clash prunes that column immediately.",
    active=[ROOT], done={},
    state=[["board", str(N) + "x" + str(N)], ["prune on", "col / 2 diagonals"]])
add(act=0, code="backtrack", line=1,
    note="A path that reaches row == n has a queen safely in every row — that's a "
    "solution. Here we follow the branch that starts with a queen in row 0, "
    "column 1; watch how few columns survive below it.",
    active=[ROOT], done={},
    state=[["goal", "row == 4"], ["start", "row0 = col1"]])

# ---- Act 1: walk n=4, pruning attacked columns, reaching a board ----
done = {}
placed_leaf = None
add(act=1, nodes=NODES, edges=EDGES, code="backtrack", line=0,
    intro="attacked columns light with an x badge; a full safe board lights green.",
    invariant="the active path is the queens placed so far, top row downward.",
    note="Run it. At each row we scan columns left to right; most are attacked by "
    "queens already down and get pruned (x). Only a safe column recurses deeper.",
    active=[ROOT], done={}, state=[["row", 0], ["placed", "[]"]])

for oid in order:
    nd = nodes[oid]
    if nd["kind"] == "root":
        continue
    active = path_to(edges, oid)
    placement = nd["placement"]
    if nd["kind"] == "prune":
        done[oid] = "x"
        reasons = ", ".join(nd["reason"])
        add(act=1, code="backtrack", line=6,
            note=f"Row {nd['row']}, column {nd['col']}: attacked ({reasons}). "
                 f"Prune — don't recurse.",
            active=active, done=dict(done),
            state=[["row", nd["row"]], ["try col", nd["col"]],
                   ["verdict", "attacked"]])
    elif nd["kind"] == "sol":
        done[oid] = "ok"
        placed_leaf = oid
        board = board_lines(placement, N)
        add(act=1, code="backtrack", line=2,
            note=f"row == 4: a queen sits safely in every row. Record the board "
                 f"(columns {placement}).",
            active=active, done=dict(done),
            state=[["solution", str(placement)],
                   ["board", " / ".join(board)]])
    else:  # place
        done[oid] = "Q"
        board = board_lines(placement, N)
        add(act=1, code="backtrack", line=8,
            note=f"Row {nd['row']}, column {nd['col']} is safe -> place a queen and "
                 f"recurse to row {nd['row'] + 1}. Placed columns: {placement}.",
            active=active, done=dict(done),
            state=[["row", nd["row"]], ["place col", nd["col"]],
                   ["placed", str(placement)]])

sol_board = board_lines(nodes[placed_leaf]["placement"], N)
add(act=1, code="backtrack", line=2,
    note="A valid board found: " + " / ".join(sol_board) +
         ".  (n=4 has 2 solutions total; this is the first — the other is its "
         "left-right mirror.)",
    active=path_to(edges, placed_leaf), done=dict(done),
    state=[["solution", str(nodes[placed_leaf]['placement'])]],
    banner="Valid 4-queens board: " + " ".join(sol_board))

# ---- Act 2: edge case n=3 -> every branch pruned, zero solutions ----
N3 = 3
# row0 = col0 and col1 are enough; col2 is the mirror of col0.
nodes3, edges3, order3 = build_tree(N3, restrict_row0={0, 1})
NODES3 = render_nodes(nodes3)
EDGES3 = render_edges(edges3)
ROOT3 = order3[0]
done3 = {}
add(act=2, nodes=NODES3, edges=EDGES3, code="backtrack", line=5,
    intro="on a 3x3 board no path ever reaches row 3 — pruning erases every line.",
    invariant="same rule; there is simply no attack-free queen in every row.",
    note="Edge case: n = 3. Follow row 0 = column 0 and column 1 (column 2 is the "
    "mirror). The diagonals are too tight — every deeper column is attacked.",
    active=[ROOT3], done={}, state=[["board", "3x3"], ["solutions so far", 0]])

sols3 = 0
for oid in order3:
    nd = nodes3[oid]
    if nd["kind"] == "root":
        continue
    active = path_to(edges3, oid)
    placement = nd["placement"]
    if nd["kind"] == "prune":
        done3[oid] = "x"
        reasons = ", ".join(nd["reason"])
        add(act=2, code="backtrack", line=6,
            note=f"Row {nd['row']}, column {nd['col']}: attacked ({reasons}). Prune.",
            active=active, done=dict(done3),
            state=[["row", nd["row"]], ["try col", nd["col"]], ["verdict", "attacked"]])
    elif nd["kind"] == "sol":
        done3[oid] = "ok"; sols3 += 1
        add(act=2, code="backtrack", line=2,
            note="Reached row 3 — a solution.",
            active=active, done=dict(done3), state=[["solution", str(placement)]])
    else:
        done3[oid] = "Q"
        add(act=2, code="backtrack", line=8,
            note=f"Row {nd['row']}, column {nd['col']} is (so far) safe -> place and "
                 f"go deeper. Placed: {placement}.",
            active=active, done=dict(done3),
            state=[["row", nd["row"]], ["place col", nd["col"]], ["placed", str(placement)]])

add(act=2, code="backtrack", line=0,
    note="No branch ever reached row 3 — every path hit an attack and pruned. So "
    "n=3 has zero solutions. (n=2 is empty for the same reason.)",
    active=[], done=dict(done3),
    state=[["solutions", sols3]],
    banner="n=3: 0 solutions — pruning kills every branch")

trace = {
    "player": "tree",
    "title": "N-Queens — one queen per row, pruning the attacked columns away",
    "acts": ["The rule (prune on attack)",
             "Walk n=4 to a valid board",
             "Edge case: n=3 has no solution"],
    "code": {"backtrack": CODE},
    "legend": [["active", "queens placed so far (current path)"],
               ["good", "resolved: Q placed, x pruned, ok = solution"]],
    "nodes": NODES, "edges": EDGES, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
