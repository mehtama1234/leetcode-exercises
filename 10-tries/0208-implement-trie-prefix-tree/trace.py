"""Rich full-arc trace for Implement Trie (tree renderer as the LETTER TREE).

Design problem: no wasteful brute baseline, so the arc is the rule (share
prefixes on one path; a flag marks a real word) -> insert + query it -> the
edge case that the flag exists at all (search vs startsWith on "app").

Each tree node is a character position. `active` = the node currently on the
walk; a node's badge shows a bullet when `is_word` is set there (a complete
word ends at this node). Node x,y positions computed here in Python. Mirrors
insert/_walk/search/startsWith in solution.py. Writes trace.json.
"""
import json
import os

XSTEP, YSTEP = 70, 88
frames = []

CODE = [
    "def insert(word):",
    "    node = root",
    "    for ch in word:",
    "        node = node.children.setdefault(ch, TrieNode())",
    "    node.is_word = True",
    "",
    "def _walk(prefix):        # -> node or None",
    "    node = root",
    "    for ch in prefix:",
    "        if ch not in node.children: return None",
    "        node = node.children[ch]",
    "    return node",
]


def add(**f):
    frames.append(f)


# ---------------------------------------------------------------------------
# Build the trie as nodes appear. x is assigned when a node is first created
# (in-order leaf counter); y is the depth (character index). A node's badge is
# "•" once a word ends there. Each frame ships the current snapshot.
# ---------------------------------------------------------------------------
nodes, edges = [], []           # {id,val,x,y}, [parent,child]
is_word = {}                    # id -> bool
children = {}                   # id -> {ch: child_id}
_col = [0]
ROOT = 0
nodes.append({"id": ROOT, "val": "▲", "x": 0, "y": 0})  # root sentinel
children[ROOT] = {}


def child_of(nid, ch, depth):
    """Return existing child for ch, or create a new node."""
    if ch in children[nid]:
        return children[nid][ch], False
    cid = len(nodes)
    nodes.append({"id": cid, "val": ch, "x": _col[0] * XSTEP, "y": depth * YSTEP})
    _col[0] += 1
    edges.append([nid, cid])
    children[nid][ch] = cid
    children[cid] = {}
    return cid, True


def badges():
    return {nid: "•" for nid, w in is_word.items() if w}


def snap():
    return [dict(n) for n in nodes], [list(e) for e in edges]


def do_insert(word, act):
    node = ROOT
    for depth, ch in enumerate(word, start=1):
        cid, created = child_of(node, ch, depth)
        n, e = snap()
        add(act=act, nodes=n, edges=e, code="insert", line=3,
            note=(f"'{ch}': no such child yet -> create the node." if created
                  else f"'{ch}': child already there -> reuse the shared prefix."),
            active=[cid], done=badges(),
            state=[["inserting", word], ["at", ch], ["shared", "no" if created else "yes"]])
        node = cid
    is_word[node] = True
    n, e = snap()
    add(act=act, nodes=n, edges=e, code="insert", line=4,
        note=f"end of '{word}': mark this node is_word (the • badge). That flag is "
        f"the only thing separating a real word from a passing-through prefix.",
        active=[node], done=badges(),
        state=[["inserted", word], ["is_word here", "True"]])
    return node


def do_walk(prefix, act, kind):
    """kind = 'search' or 'startsWith'. Returns landing node id or None."""
    node = ROOT
    for ch in prefix:
        if ch not in children[node]:
            n, e = snap()
            add(act=act, nodes=n, edges=e, code="walk", line=9,
                note=f"'{ch}' has no child from here -> the walk falls off. {kind} is False.",
                active=[node], done=badges(),
                state=[["query", prefix], ["stuck at", ch], [kind, "False"]])
            return None
        node = children[node][ch]
        n, e = snap()
        add(act=act, nodes=n, edges=e, code="walk", line=10,
            note=f"'{ch}' -> step to its child. Following the shared path IS the "
            f"prefix check.",
            active=[node], done=badges(), state=[["query", prefix], ["on", ch]])
    return node


# ---- Act 0: the rule ----
n, e = snap()
add(act=0, nodes=n, edges=e, code="insert", line=0,
    intro="words that share a start share a PATH; a • flag marks where a real "
    "word ends.",
    invariant="every node is one character; depth = position in the word.",
    note="A trie stores words along paths from the root. 'app' and 'apple' walk "
    "the same first three nodes. A set couldn't answer startsWith without "
    "scanning every word; a path walk answers it for free.",
    active=[ROOT], done={}, state=[["root", "▲"], ["node =", "one character"]])

# ---- Act 1: insert 'apple', then query ----
n, e = snap()
add(act=1, nodes=n, edges=e, code="insert", line=0,
    intro="the path a-p-p-l-e appears; only the last node gets the • flag.",
    invariant="creating a node just extends the path; the flag is set once, at the end.",
    note="insert('apple'): walk char by char, creating missing nodes.",
    active=[ROOT], done={}, state=[["insert", "apple"]])
do_insert("apple", 1)

# search('app') -> walk lands on a node, but its flag is off
land = do_walk("app", 1, "search")
add(act=1, code="walk", line=11,
    note="search('app') reached a real node, but is_word there is False — 'app' "
    "is only a prefix of 'apple', never inserted. So search is False...",
    active=[land], done=badges(),
    state=[["search('app')", "False"], ["reason", "no • flag here"]])
# startsWith('app') -> same node existing is enough
land = do_walk("app", 1, "startsWith")
add(act=1, code="walk", line=11,
    note="...but startsWith('app') only needs the node to EXIST, and it does. So "
    "startsWith is True. Same walk, different check at the end.",
    active=[land], done=badges(),
    state=[["startsWith('app')", "True"], ["needs", "node exists"]],
    banner="search('app')=False, startsWith('app')=True")

# ---- Act 2: insert 'app' so the flag flips ----
n, e = snap()
add(act=2, nodes=n, edges=e, code="insert", line=0,
    intro="no new nodes are made — 'app' already exists as a path; only its "
    "flag changes.",
    invariant="the flag is per-node, so 'app' and 'apple' can both be words on "
    "one shared path.",
    note="insert('app'): the path a-p-p is already there, so we create nothing "
    "and just set is_word on the second 'p'.",
    active=[ROOT], done=badges(), state=[["insert", "app"], ["new nodes", 0]])
do_insert("app", 2)
land = do_walk("app", 2, "search")
add(act=2, code="walk", line=11,
    note="Now search('app') lands on a node whose • is set -> True. The flag is "
    "exactly what distinguishes a stored word from a mere prefix.",
    active=[land], done=badges(),
    state=[["search('app')", "True"], ["flag", "now set"]],
    banner="After insert('app'): search('app') = True")

trace = {
    "player": "tree",
    "title": "Implement Trie - one path per word, a flag marks the real word",
    "acts": ["The rule", "Insert 'apple' + query", "Insert 'app': the flag flips"],
    "code": {"insert": CODE, "walk": CODE},
    "legend": [["active", "node on the current walk"],
               ["good", "• = a complete word ends here (is_word)"]],
    "nodes": [dict(nodes[0])], "edges": [], "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
