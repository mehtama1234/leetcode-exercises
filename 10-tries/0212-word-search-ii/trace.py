"""Rich full-arc trace for Word Search II (tree renderer as the LETTER TREE).

This one has an honest wasteful baseline (find_words_brute), so the arc is:
brute (each word re-walks the board, re-treading shared prefixes) -> the waste
-> the trie of ALL words guides ONE board DFS (active = the trie node the walk
sits on) -> edge case (shared prefix + duplicate word collected once).

The tree drawn is the TRIE of the target words. `active` = the node the board
walk is currently matching; a node's badge shows the whole word where one ends
(and flips to a check once collected). Node x,y positions computed here in
Python. Mirrors Solution.findWords / _build_trie / dfs in solution.py.
Writes trace.json.
"""
import json
import os

XSTEP, YSTEP = 66, 82
frames = []

CODE = [
    "def dfs(r, c, node):",
    "    ch = board[r][c]",
    "    nxt = node.children.get(ch)",
    "    if nxt is None: return          # off the trie -> prune",
    "    if nxt.word is not None:",
    "        found.append(nxt.word); nxt.word = None   # collect once",
    "    board[r][c] = '#'               # mark visited",
    "    for nr, nc in neighbors(r, c):",
    "        if board[nr][nc] != '#': dfs(nr, nc, nxt)",
    "    board[r][c] = ch                # restore",
]


def add(**f):
    frames.append(f)


BOARD = [
    ["o", "a", "a", "n"],
    ["e", "t", "a", "e"],
    ["i", "h", "k", "r"],
    ["i", "f", "l", "v"],
]
WORDS = ["oath", "pea", "eat", "rain"]

# ---------------------------------------------------------------------------
# Build the trie of the target words and lay it out. x is a leaf counter at
# creation time, y is depth. Each node stores the word that ends there.
# ---------------------------------------------------------------------------
nodes, edges = [], []
children = {}       # id -> {ch: cid}
word_at = {}        # id -> full word (or None)
collected = {}      # id -> True once found, flips badge to a check
_col = [0]
ROOT = 0
nodes.append({"id": ROOT, "val": "▲", "x": 0, "y": 0})
children[ROOT] = {}


def child_of(nid, ch, depth):
    if ch in children[nid]:
        return children[nid][ch]
    cid = len(nodes)
    nodes.append({"id": cid, "val": ch, "x": _col[0] * XSTEP, "y": depth * YSTEP})
    _col[0] += 1
    edges.append([nid, cid])
    children[nid][ch] = cid
    children[cid] = {}
    return cid


def build(words):
    for w in words:
        node = ROOT
        for depth, ch in enumerate(w, start=1):
            node = child_of(node, ch, depth)
        word_at[node] = w


build(WORDS)


def badges():
    out = {}
    for nid, w in word_at.items():
        if w is not None:
            out[nid] = ("check " if collected.get(nid) else "") + w
    for nid in collected:
        if word_at.get(nid) is None:
            out[nid] = "check"
    return out


def snap():
    return [dict(n) for n in nodes], [list(e) for e in edges]


# ---- Act 0: brute force — each word re-walks the board ----
add(act=0, nodes=snap()[0], edges=snap()[1], code=None,
    intro="each word launches its OWN full-board search, re-treading whatever "
    "prefix it shares with another word.",
    invariant="the answer set is the words that can be spelled on the board.",
    note="Brute force: for each of the 4 words, DFS the whole board looking for "
    "just that word. 'oath' and (say) 'oat' would each re-walk the shared 'oa' "
    "from every start.",
    active=[ROOT], done=badges(), state=[["words", len(WORDS)], ["searches", len(WORDS)]])
add(act=0, note="With w words that's w independent board sweeps. Nothing is "
    "shared between them, even when the words start the same.",
    active=[ROOT], done=badges(), state=[["cost", "w x board-DFS"], ["shared prefixes", "re-walked"]])

# ---- Act 1: the waste ----
add(act=1, nodes=snap()[0], edges=snap()[1],
    intro="the repeated work is every shared prefix, walked once per word "
    "instead of once total.",
    invariant="a prefix walked for word A is identical to the same prefix for word B.",
    note="Put all the words in ONE trie. Now shared starts are a single shared "
    "PATH, so one board walk can chase every word that shares that start at once.",
    active=[ROOT], done=badges(), state=[["idea", "one trie of all words"], ["searches", 1]])


# ---- Act 2: trie-guided single board DFS ----
ROWS, COLS = len(BOARD), len(BOARD[0])
DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
found = []


def dfs(r, c, nid, act):
    ch = BOARD[r][c]
    nxt = children[nid].get(ch)
    if nxt is None:
        return  # off the trie -> prune
    add(act=act, nodes=snap()[0], edges=snap()[1], code="dfs", line=2,
        note=f"board ({r},{c})='{ch}' matches a trie child -> descend. The board "
        f"walk and the trie walk move together.",
        active=[nxt], done=badges(),
        state=[["cell", f"({r},{c})={ch}"], ["on trie node", nodes[nxt]['val']]])
    if word_at.get(nxt) is not None:
        w = word_at[nxt]
        collected[nxt] = True
        word_at[nxt] = None  # collect once (dedupe)
        found.append(w)
        add(act=act, nodes=snap()[0], edges=snap()[1], code="dfs", line=5,
            note=f"this trie node carries a whole word -> collect '{w}'. Clear it "
            f"so a duplicate can't be collected twice.",
            active=[nxt], done=badges(),
            state=[["found", w], ["total", len(found)]])
    saved = BOARD[r][c]
    BOARD[r][c] = "#"
    for dr, dc in DIRS:
        nr, nc = r + dr, c + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS and BOARD[nr][nc] != "#":
            dfs(nr, nc, nxt, act)
    BOARD[r][c] = saved


add(act=2, nodes=snap()[0], edges=snap()[1], code="dfs", line=0,
    intro="active = the trie node the board walk is on; when it leaves the trie "
    "we prune instantly.",
    invariant="collecting a word clears its marker, so each word is found once.",
    note="Walk the board once. From each cell, descend the trie while the letter "
    "is a valid next character; the moment it isn't, prune.",
    active=[ROOT], done=badges(), state=[["one pass", "board + trie together"]])
for r in range(ROWS):
    for c in range(COLS):
        dfs(r, c, ROOT, 2)
add(act=2, nodes=snap()[0], edges=snap()[1], code="dfs", line=5,
    note=f"One board pass collected {sorted(found)}. 'pea' and 'rain' never "
    f"matched a start and were pruned immediately.",
    active=[], done=badges(), state=[["found", str(sorted(found))]],
    banner=f"findWords = {sorted(found)}  (one pass, shared prefixes walked once)")

# ---- Act 3: edge case — shared prefix + duplicate word, collected once ----
nodes2, edges2, children2, word_at2, collected2 = [], [], {}, {}, {}
_c2 = [0]
nodes2.append({"id": 0, "val": "▲", "x": 0, "y": 0})
children2[0] = {}


def child2(nid, ch, depth):
    if ch in children2[nid]:
        return children2[nid][ch]
    cid = len(nodes2)
    nodes2.append({"id": cid, "val": ch, "x": _c2[0] * XSTEP, "y": depth * YSTEP})
    _c2[0] += 1
    edges2.append([nid, cid])
    children2[nid][ch] = cid
    children2[cid] = {}
    return cid


# words: oat, oath, oat (duplicate). Shared prefix o-a-t.
for w in ["oat", "oath", "oat"]:
    node = 0
    for depth, ch in enumerate(w, start=1):
        node = child2(node, ch, depth)
    word_at2[node] = w  # duplicate 'oat' just re-marks the same node


def badges2():
    out = {}
    for nid, w in word_at2.items():
        if w is not None:
            out[nid] = ("check " if collected2.get(nid) else "") + w
    for nid in collected2:
        if word_at2.get(nid) is None:
            out[nid] = "check"
    return out


snap2 = lambda: ([dict(n) for n in nodes2], [list(e) for e in edges2])
add(act=3, nodes=snap2()[0], edges=snap2()[1], code="dfs", line=4,
    intro="'oat' and 'oath' share the path o-a-t; a duplicate 'oat' is the same "
    "node, so it can only be collected once.",
    invariant="clearing the word marker after collecting is what dedupes.",
    note="Edge case: words ['oat','oath','oat']. The trie has ONE path o-a-t and "
    "one more node h. The duplicate 'oat' just marks the same 't' node.",
    active=[0], done=badges2(),
    state=[["stored", "oat, oath, oat"], ["distinct paths", "o-a-t(-h)"]])
# collect oat once
t_id = children2[children2[children2[0]["o"]]["a"]]["t"]
collected2[t_id] = True
word_at2[t_id] = None
add(act=3, nodes=snap2()[0], edges=snap2()[1], code="dfs", line=5,
    note="Reaching the 't' node collects 'oat' and clears its marker. The "
    "duplicate can't fire again -> 'oat' appears once.",
    active=[t_id], done=badges2(), state=[["collected", "oat (once)"]],
    banner="Duplicate 'oat' collected once; 'oath' still found on the same path")

trace = {
    "player": "tree",
    "title": "Word Search II - one trie guides one board walk",
    "acts": ["Brute: a search per word", "The waste", "Trie-guided one pass", "Edge: shared prefix, once"],
    "code": {"dfs": CODE},
    "legend": [["active", "trie node the board walk is on"],
               ["good", "word label = a word ends here; 'check' = collected"]],
    "nodes": [dict(nodes[0])], "edges": [], "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
