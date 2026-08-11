"""Full-arc tree trace for Letter Combinations of a Phone Number.

Backtracking has no wasteful brute baseline — the tree IS the work — so the arc
is: the rule (one digit per level, branch over that digit's keypad letters) ->
run the DFS and watch the path walk the tree, leaves collecting complete words ->
an edge case (empty input -> no words at all). We precompute every node's x,y in
Python for digits="23". Each node is a partial string; a leaf (depth == number of
digits) is one finished word. Mirrors backtrack() in solution.py.
"""
import json
import os

KEYPAD = {
    "2": "abc", "3": "def", "4": "ghi", "5": "jkl",
    "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz",
}

XSTEP, YSTEP = 56, 84
frames = []

CODE = [
    "def backtrack(i):",
    "    if i == len(digits):",
    "        result.append(''.join(path))",
    "        return",
    "    for letter in KEYPAD[digits[i]]:",
    "        path.append(letter)  # choose",
    "        backtrack(i + 1)     # explore",
    "        path.pop()           # un-choose",
]


def add(**f):
    frames.append(f)


def build_tree(digits):
    """Enumerate the Cartesian-product decision tree; assign x,y by in-order sweep.

    node = {id, i (depth), val (partial word, "start" at root), leaf?, letter}.
    Returns (nodes, edges, order) where order is the DFS pre-order visit sequence
    matching the solution's traversal (letters tried in keypad order).
    """
    n = len(digits)
    nodes = {}
    edges = []
    order = []
    counter = [0]       # in-order x slot (leaves and inner nodes share the sweep)
    nid = [0]

    def make(i, path, letter):
        my = nid[0]; nid[0] += 1
        word = "".join(path)
        node = {"i": i, "leaf": i == n, "letter": letter,
                "val": word if word else "start", "x": 0, "y": i * YSTEP}
        nodes[my] = node
        order.append(my)
        if i == n:
            node["x"] = counter[0] * XSTEP; counter[0] += 1
            return my
        first = None
        child_xs = []
        for ch in KEYPAD[digits[i]]:
            path.append(ch)
            cid = make(i + 1, path, ch)
            path.pop()
            edges.append((my, cid, ch))
            child_xs.append(nodes[cid]["x"])
            if first is None:
                first = cid
        # center the parent over the span of its children
        node["x"] = sum(child_xs) / len(child_xs) if child_xs else counter[0] * XSTEP
        return my

    make(0, [], None)
    return nodes, edges, order


def render_nodes(nodes):
    return [{"id": k, "val": v["val"], "x": round(v["x"]), "y": v["y"]} for k, v in nodes.items()]


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


DIGITS = "23"
nodes, edges, order = build_tree(DIGITS)
NODES = render_nodes(nodes)
EDGES = render_edges(edges)

# ---- Act 0: the rule ----
add(act=0, nodes=NODES, edges=EDGES, code="backtrack", line=0,
    intro="each level is one digit; the branches are that digit's keypad letters.",
    invariant="depth = digit index; a leaf at the bottom row is one finished word.",
    note="The rule: at digit i, branch over its keypad letters — 2 gives a, b, c; "
    "3 gives d, e, f — then move to the next digit. Every root-to-leaf path spells "
    "one word.",
    active=[0], done={}, state=[["digits", DIGITS], ["2 -> ", "abc"], ["3 -> ", "def"]])
add(act=0, code="backtrack", line=1,
    note="The bottom row (i == 2, past the last digit) is where a path becomes a "
    "complete word — we join the letters and record it.",
    active=[0], done={},
    state=[["words", "3 x 3 = 9"], ["= leaves", 9]])

# ---- Act 1: run the DFS ----
done = {}
words_found = []
add(act=1, nodes=NODES, edges=EDGES, code="backtrack", line=0,
    intro="the active path is the letters chosen so far; leaves light green.",
    invariant="a green leaf spells exactly the letters picked on the way down.",
    note="Run it. The highlighted path is the letters chosen so far; each time we "
    "reach the bottom we record that word.",
    active=[0], done={}, state=[["found", 0]])
for oid in order:
    nd = nodes[oid]
    active = path_to(edges, oid)
    if nd["leaf"]:
        done[oid] = nd["val"]
        words_found.append(nd["val"])
        add(act=1, code="backtrack", line=2,
            note=f"Bottom of a path -> record the word \"{nd['val']}\". "
                 f"({len(words_found)} of 9 so far.)",
            active=active, done=dict(done),
            state=[["word", nd["val"]], ["found", len(words_found)]])
    elif nd["letter"] is None:
        add(act=1, code="backtrack", line=0,
            note="Start at the root with an empty path. Digit 2 first: try a, b, c.",
            active=active, done=dict(done),
            state=[["at digit", DIGITS[0]], ["letters", KEYPAD[DIGITS[0]]], ["found", len(words_found)]])
    else:
        add(act=1, code="backtrack", line=5,
            note=f"Chose '{nd['letter']}' for digit {DIGITS[nd['i'] - 1]}: path is now "
                 f"\"{nd['val']}\". Next digit {DIGITS[nd['i']]}: try {KEYPAD[DIGITS[nd['i']]]}.",
            active=active, done=dict(done),
            state=[["at digit", DIGITS[nd["i"]]], ["path", nd["val"]], ["found", len(words_found)]])
add(act=1, code="backtrack", line=2,
    note="Every leaf visited -> all 9 words collected: the full product of the two "
    "digits' letters.",
    active=[], done=dict(done),
    state=[["words", 9]],
    banner="9 words = 3 x 3, one per leaf")

# ---- Act 2: edge case — empty input ----
DIGITS_E = ""
nodes_e, edges_e, order_e = build_tree(DIGITS_E)
NODES_E = render_nodes(nodes_e)
EDGES_E = render_edges(edges_e)
add(act=2, nodes=NODES_E, edges=EDGES_E, code="backtrack", line=0,
    intro="with no digits there is nothing to spell — the answer is empty.",
    invariant="empty input returns [], not one empty word.",
    note="Edge case: digits = \"\". The function returns early with an empty list — "
    "there are no digits, so there is no word to build.",
    active=[0], done={}, state=[["digits", "\"\""], ["result", "[]"]])
add(act=2, code="backtrack", line=2,
    note="So \"\" gives [] (not [\"\"]). A single digit like \"2\" would instead give "
    "three one-letter words: a, b, c.",
    active=[], done={},
    state=[["words", 0], ["\"2\" ->", "a, b, c"]],
    banner="Empty input -> [] (no words)")

trace = {
    "player": "tree",
    "title": "Letter Combinations — one digit per level, branch over keypad letters",
    "acts": ["The rule", "Walk the decision tree", "Edge case: empty input"],
    "code": {"backtrack": CODE},
    "legend": [["active", "current path"], ["good", "finished word (leaf)"]],
    "nodes": NODES, "edges": EDGES, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
