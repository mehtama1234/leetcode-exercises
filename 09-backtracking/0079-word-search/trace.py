"""Rich full-arc trace for Word Search (tree renderer as a DECISION TREE).

The prompt fixes the 09-backtracking renderer to a decision tree: nodes are
CHOICES (which neighbor cell to step to next), the active node is the cell on
the current path, and dead branches (letter mismatch / off-board / already
used) are marked X. A branch that spells the whole word is OK.

Because a full 4-way board DFS explodes, we trace one honest start cell and the
handful of branches it actually opens, mirroring dfs() in solution.py. Node
x,y positions are computed here in Python. Writes trace.json.
"""
import json
import os

XSTEP, YSTEP = 74, 92
frames = []

CODE = [
    "def dfs(r, c, k):",
    "    if k == len(word): return True",
    "    if off_board(r, c): return False",
    "    if board[r][c] != word[k]: return False",
    "    board[r][c] = '#'          # mark used",
    "    found = dfs(r+1,c,k+1) or dfs(r-1,c,k+1) \\",
    "         or dfs(r,c+1,k+1) or dfs(r,c-1,k+1)",
    "    board[r][c] = word[k]      # restore",
    "    return found",
]


def add(**f):
    frames.append(f)


BOARD = [
    ["A", "B", "C", "E"],
    ["S", "F", "C", "S"],
    ["A", "D", "E", "E"],
]
WORD = "ABCCED"
ROWS, COLS = len(BOARD), len(BOARD[0])

# ---------------------------------------------------------------------------
# Decision tree grown as the DFS descends. Each node is a *step onto a cell*.
# We place nodes with an in-order leaf counter (x) and depth (y = letter index).
# ---------------------------------------------------------------------------
nodes, edges, done = [], [], {}
_col = [0]
DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
DIRNAME = {(1, 0): "down", (-1, 0): "up", (0, 1): "right", (0, -1): "left"}


def new_node(label, depth, parent):
    nid = len(nodes)
    nodes.append({"id": nid, "val": label, "x": _col[0] * XSTEP, "y": depth * YSTEP})
    _col[0] += 1
    if parent is not None:
        edges.append([parent, nid])
    return nid


def snap():
    return [dict(n) for n in nodes], [list(e) for e in edges]


used = [[False] * COLS for _ in range(ROWS)]


def cell_label(r, c):
    return f"{BOARD[r][c]}"


# The real DFS, but tree-emitting. Returns True if this branch spells the word.
def dfs(r, c, k, nid, depth, act, path):
    # off board?
    if r < 0 or r >= ROWS or c < 0 or c >= COLS:
        done[nid] = "X"
        n, e = snap()
        add(act=act, nodes=n, edges=e, code="dfs", line=2,
            note=f"step {DIRNAME_LAST[0]} walks off the board -> dead branch.",
            active=[nid], done=dict(done), state=[["target", WORD[k] if k < len(WORD) else "-"],
                                                  ["cell", "off-grid"]])
        return False
    if used[r][c]:
        done[nid] = "X"
        n, e = snap()
        add(act=act, nodes=n, edges=e, code="dfs", line=4,
            note=f"cell ({r},{c})='{BOARD[r][c]}' is already used on this path -> can't reuse.",
            active=[nid], done=dict(done), state=[["need", WORD[k]], ["cell", "used"]])
        return False
    if BOARD[r][c] != WORD[k]:
        done[nid] = "X"
        n, e = snap()
        add(act=act, nodes=n, edges=e, code="dfs", line=3,
            note=f"cell ({r},{c})='{BOARD[r][c]}' but need '{WORD[k]}' -> mismatch, dead.",
            active=[nid], done=dict(done),
            state=[["need", WORD[k]], ["got", BOARD[r][c]]])
        return False

    # match! take the cell
    path.append(BOARD[r][c])
    n, e = snap()
    add(act=act, nodes=n, edges=e, code="dfs", line=3,
        note=f"cell ({r},{c})='{BOARD[r][c]}' matches word[{k}]='{WORD[k]}'. "
        f"path so far: {''.join(path)}.",
        active=[nid], done=dict(done),
        state=[["k", k], ["matched", "".join(path)], ["need next",
               WORD[k + 1] if k + 1 < len(WORD) else "(done)"]])

    if k + 1 == len(WORD):
        done[nid] = "OK"
        path.pop()
        n, e = snap()
        add(act=act, nodes=n, edges=e, code="dfs", line=1,
            note=f"that was the last letter -> the whole word '{WORD}' is spelled. True.",
            active=[nid], done=dict(done), state=[["spelled", WORD], ["result", "True"]])
        return True

    used[r][c] = True
    found = False
    for d in DIRS:
        DIRNAME_LAST[0] = DIRNAME[d]
        nr, nc = r + d[0], c + d[1]
        # only draw the promising letter-matching neighbor as an explored child;
        # off-board / mismatched neighbors are shown as X leaves for honesty.
        child = new_node(BOARD[nr][nc] if 0 <= nr < ROWS and 0 <= nc < COLS else "·",
                         depth + 1, nid)
        if dfs(nr, nc, k + 1, child, depth + 1, act, path):
            found = True
            break
    used[r][c] = False
    path.pop()
    if not found and done.get(nid) not in ("OK",):
        done[nid] = "X"
    return found


DIRNAME_LAST = ["down"]

# ---- Act 0: the rule ----
r0 = new_node(BOARD[0][0], 0, None)
n, e = snap()
add(act=0, nodes=n, edges=e, code="dfs", line=0,
    intro="each node is a choice of which neighbor to step to; a branch dies "
    "the instant a letter mismatches, walks off-grid, or reuses a cell.",
    invariant="the marked-used cells are exactly the ones on the current path.",
    note=f"Spell '{WORD}' by walking to adjacent cells, no cell reused. Try each "
    f"cell as a start; here the search from (0,0)='A' is the live one.",
    active=[r0], done={}, state=[["word", WORD], ["start", "(0,0)=A"]])
add(act=0, code="dfs", line=4,
    note="Trick: overwrite the current cell with '#' before recursing (mark "
    "used) and restore it after. Restoring is the backtracking step.",
    active=[r0], done={}, state=[["mark", "board=#"], ["restore", "on the way out"]])

# ---- Act 1: run the decision tree from (0,0) ----
n, e = snap()
add(act=1, nodes=n, edges=e, code="dfs", line=0,
    intro="watch the path grow A->B->C->C->E->D; X marks each abandoned branch.",
    invariant="a node's badge appears only once its whole subtree is resolved.",
    note="Run from (0,0)='A'. It matches word[0], so we open its neighbors and "
    "keep the branch that keeps matching.",
    active=[r0], done={}, state=[["start remaining", WORD]])
res = dfs(0, 0, 0, r0, 0, 1, [])
done.setdefault(r0, "OK")
n, e = snap()
add(act=1, nodes=n, edges=e, code="dfs", line=8,
    note="One path spelled every letter, so exist(...) is True. The X branches "
    "were the neighbors that didn't match and got abandoned.",
    active=[], done=dict(done), state=[["word", WORD], ["result", str(res)]],
    banner=f"exist(board, '{WORD}') = {res}")

# ---- Act 2: edge case — a word that must fail by the no-reuse rule ----
nodes2, edges2, done2 = [], [], {}
_c2 = [0]


def nn2(label, depth, parent):
    nid = len(nodes2)
    nodes2.append({"id": nid, "val": label, "x": _c2[0] * XSTEP, "y": depth * YSTEP})
    _c2[0] += 1
    if parent is not None:
        edges2.append([parent, nid])
    return nid


def snap2():
    return [dict(n) for n in nodes2], [list(e) for e in edges2]


# "ABCB" on the same board: A(0,0)->B(0,1)->C(0,2)->need B, but the only B is (0,1),
# already used -> every branch dies.
r2 = nn2("A", 0, None)
b2 = nn2("B", 1, r2)
c2 = nn2("C", 2, b2)
x2 = nn2("B?", 3, c2)
done2[r2] = done2[b2] = done2[c2] = ""  # on the live path
done2[x2] = "X"
n, e = snap2()
add(act=2, nodes=n, edges=e, code="dfs", line=4,
    intro="the fourth letter needs a 'B', but the only 'B' is already on the path.",
    invariant="no cell may appear twice on one path — that's what kills this word.",
    note="Edge case: word 'ABCB'. We reach A->B->C fine, but the next 'B' would "
    "have to reuse the same cell (0,1). It's marked used -> dead.",
    active=[x2], done=dict(done2), state=[["path", "A-B-C"], ["need", "B"], ["only B", "already used"]])
add(act=2, code="dfs", line=8,
    note="Every start hits the same wall, so exist(...) is False. The no-reuse "
    "rule is exactly the backtracking mark.",
    active=[], done=dict(done2), state=[["word", "ABCB"], ["result", "False"]],
    banner="exist(board, 'ABCB') = False  (would reuse the same B)")

trace = {
    "player": "tree",
    "title": "Word Search - a decision tree that steps cell to cell",
    "acts": ["The rule", "Run the decision tree", "Edge: no cell reused"],
    "code": {"dfs": CODE},
    "legend": [["active", "cell we're stepping onto now"],
               ["good", "OK = word spelled; X = mismatch / off-grid / reused"]],
    "nodes": [dict(nodes[0])], "edges": [], "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
