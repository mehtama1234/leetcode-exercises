"""Rich full-arc trace for WordDictionary (tree renderer as the LETTER TREE).

Design problem: the arc is the rule (a trie whose search branches on '.') ->
run an exact walk, then a wildcard search that fans across children -> an edge
case where the wildcard must not walk off a too-short branch.

Each tree node is a character position. `active` = node(s) on the current walk;
at a '.', search recurses into ALL children, so several nodes light at once. A
node's badge shows • where is_word is set. Node x,y positions computed here in
Python. Mirrors dfs() in solution.search. Writes trace.json.
"""
import json
import os

XSTEP, YSTEP = 74, 88
frames = []

CODE = [
    "def search(word):",
    "    def dfs(i, node):",
    "        if i == len(word):",
    "            return node.is_word",
    "        ch = word[i]",
    "        if ch == '.':",
    "            return any(dfs(i+1, c) for c in node.children.values())",
    "        if ch not in node.children: return False",
    "        return dfs(i+1, node.children[ch])",
    "    return dfs(0, root)",
]


def add(**f):
    frames.append(f)


# ---------------------------------------------------------------------------
# Build a fixed trie of {bad, dad, mad}, then trace searches over it. Layout is
# assigned as nodes are created (in-order leaf counter for x, depth for y).
# ---------------------------------------------------------------------------
nodes, edges = [], []
is_word = {}
children = {}
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


def add_word(word):
    node = ROOT
    for depth, ch in enumerate(word, start=1):
        node = child_of(node, ch, depth)
    is_word[node] = True


for w in ["bad", "dad", "mad"]:
    add_word(w)

# lock in a tidy layout: re-space columns left-to-right by current x order so
# the three branches don't overlap after in-order creation.
order = sorted((n for n in nodes if n["id"] != ROOT), key=lambda n: (n["y"], n["x"]))
# (creation order already gives bad / dad / mad as three clean columns.)


def badges():
    return {nid: "•" for nid, w in is_word.items() if w}


def snap():
    return [dict(n) for n in nodes], [list(e) for e in edges]


# ---- Act 0: the rule ----
n, e = snap()
add(act=0, nodes=n, edges=e, code="dfs", line=0,
    intro="a normal trie follows ONE path; a '.' means 'any child could "
    "continue', so search becomes a depth-first fan-out.",
    invariant="each node is one character; is_word (•) marks where a word ends.",
    note="Stored: bad, dad, mad — three branches off the root that all rejoin "
    "the shape a-d. addWord is a plain trie insert; the '.' only appears in "
    "queries.",
    active=[ROOT], done=badges(), state=[["stored", "bad, dad, mad"], ["'.'", "matches any 1 char"]])
add(act=0, code="dfs", line=5,
    note="At a '.', instead of following one edge we try EVERY child and "
    "succeed if any branch reaches a real word. A plain char is just the "
    "one-branch case.",
    active=[ROOT], done=badges(), state=[["at '.'", "try all children"], ["at 'x'", "one child"]])


# a generic DFS that emits frames; returns True/False
def dfs(word, i, node, act, path_nodes):
    if i == len(word):
        ok = is_word.get(node, False)
        add(act=act, code="dfs", line=3,
            note=(f"reached the end on node '{nodes[node]['val']}' with is_word set "
                  f"-> this branch matches." if ok else
                  f"reached the end on node '{nodes[node]['val']}' but is_word is "
                  f"off -> no word ends here."),
            nodes=snap()[0], edges=snap()[1],
            active=[node], done=badges(),
            state=[["i", i], ["is_word", str(ok)]])
        return ok
    ch = word[i]
    if ch == ".":
        kids = list(children[node].values())
        add(act=act, code="dfs", line=6,
            nodes=snap()[0], edges=snap()[1],
            note=f"word[{i}]='.': fan out into all {len(kids)} children "
            f"({', '.join(nodes[k]['val'] for k in kids)}) and try each.",
            active=kids, done=badges(),
            state=[["i", i], ["wildcard", "try " + str(len(kids))]])
        for k in kids:
            if dfs(word, i + 1, k, act, path_nodes + [k]):
                return True
        return False
    # ordinary character
    if ch not in children[node]:
        add(act=act, code="dfs", line=7,
            nodes=snap()[0], edges=snap()[1],
            note=f"word[{i}]='{ch}' has no child from here -> this branch dies.",
            active=[node], done=badges(), state=[["i", i], ["need", ch], ["result", "dead"]])
        return False
    nxt = children[node][ch]
    add(act=act, code="dfs", line=8,
        nodes=snap()[0], edges=snap()[1],
        note=f"word[{i}]='{ch}' -> follow the single matching child.",
        active=[nxt], done=badges(), state=[["i", i], ["on", ch]])
    return dfs(word, i + 1, nxt, act, path_nodes + [nxt])


# ---- Act 1: exact search 'bad', then wildcard '.ad' ----
add(act=1, code="dfs", line=9,
    nodes=snap()[0], edges=snap()[1],
    intro="first a plain walk (one path), then a '.' lights all three branches "
    "at once.",
    invariant="a branch only succeeds if it ends on a • node.",
    note="search('bad'): an ordinary walk b -> a -> d, then check is_word.",
    active=[ROOT], done=badges(), state=[["query", "bad"]])
r1 = dfs("bad", 0, ROOT, 1, [ROOT])
add(act=1, code="dfs", line=9, note=f"search('bad') = {r1}.",
    active=[], done=badges(), state=[["search('bad')", str(r1)]])

add(act=2, code="dfs", line=5,
    nodes=snap()[0], edges=snap()[1],
    intro="the '.' at position 0 forces all three first letters to be tried in "
    "parallel.",
    invariant="success = ANY branch reaches a • node; failure only after all fail.",
    note="search('.ad'): the '.' matches b, d, or m. Fan into all three, then "
    "each follows a -> d.",
    active=[ROOT], done=badges(), state=[["query", ".ad"]])
r2 = dfs(".ad", 0, ROOT, 2, [ROOT])
add(act=2, code="dfs", line=6, note=f"a branch reached a • node -> search('.ad') = {r2}.",
    active=[], done=badges(), state=[["search('.ad')", str(r2)]],
    banner="search('.ad') = True  ('.' matched b / d / m)")

# ---- Act 3: edge case — wildcard must not overrun a short branch ----
# fresh tiny dict {a}; search('..') must be False even though '.' matches 'a'.
nodes2, edges2, is_word2, children2 = [], [], {}, {}
_c2 = [0]
nodes2.append({"id": 0, "val": "▲", "x": 0, "y": 0})
children2[0] = {}
a_id = 1
nodes2.append({"id": a_id, "val": "a", "x": 0, "y": YSTEP})
edges2.append([0, a_id])
children2[0]["a"] = a_id
children2[a_id] = {}
is_word2[a_id] = True


def badges2():
    return {nid: "•" for nid, w in is_word2.items() if w}


add(act=3, nodes=[dict(n) for n in nodes2], edges=[list(e) for e in edges2],
    code="dfs", line=5,
    intro="'.' matches a character, but there has to BE a character — it can't "
    "invent a node past the end of a branch.",
    invariant="i must reach len(word) exactly on an is_word node to succeed.",
    note="Edge case: only 'a' is stored. search('.') fans to 'a', ends on a • "
    "node -> True.",
    active=[0], done=badges2(), state=[["stored", "a"], ["query", "."]])
add(act=3, code="dfs", line=6,
    nodes=[dict(n) for n in nodes2], edges=[list(e) for e in edges2],
    note="search('.'): '.' matches child 'a', i reaches the end on a • node -> True.",
    active=[a_id], done=badges2(), state=[["search('.')", "True"]])
add(act=3, code="dfs", line=7,
    nodes=[dict(n) for n in nodes2], edges=[list(e) for e in edges2],
    note="search('..'): the first '.' matches 'a', but 'a' has no children, so "
    "the second '.' has nothing to fan into -> False. It won't walk off the end.",
    active=[a_id], done=badges2(), state=[["search('..')", "False"], ["reason", "no child to match"]],
    banner="search('.')=True but search('..')=False  (no node past 'a')")

trace = {
    "player": "tree",
    "title": "WordDictionary - a trie whose search fans out on '.'",
    "acts": ["The rule", "Exact walk: 'bad'", "Wildcard: '.ad'", "Edge: '.' needs a real node"],
    "code": {"dfs": CODE},
    "legend": [["active", "node(s) on the current walk"],
               ["good", "• = a word ends here (is_word)"]],
    "nodes": [dict(nodes[0])], "edges": [], "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
