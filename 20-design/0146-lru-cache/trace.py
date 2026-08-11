"""Rich full-arc trace for LRU Cache (linked-list renderer).
Design problems have no wasteful baseline, so the arc is: the rule (dict finds
the node, list re-orders it) -> run a sequence of get/put -> an eviction, then a
capacity-1 edge. The doubly linked list is drawn in physical (index) order; edges
show each node's current .next, so a reorder visibly re-arcs. The dict lives in
the state HUD. Mirrors solution.py exactly. Writes trace.json.
"""
import json
import os

frames = []

CODE = [
    "def get(key):",
    "    node = map[key]        # dict jumps to the node",
    "    move_to_front(node)    # mark most-recent",
    "    return node.val",
    "def put(key, value):",
    "    if full: evict tail.prev  # least-recent",
    "    add_front(new node)",
]


def add(**f):
    frames.append(f)


# The scene is a fixed slot layout: [head, A, B, tail] growing to hold real
# nodes. To keep the linkedlist renderer stable we model a row of slots where
# index 0 = HEAD sentinel, last = TAIL sentinel, and the middle holds cache
# nodes in MRU->LRU order (left = most recent, right behind tail = least).
#
# We render node values with a "key:val" label baked into the value string.


def render(order, cap, hi=None, ghost=None, note="", act=0, line=0,
           mapd=None, extra=None, intro=None, invariant=None, banner=None):
    """order: list of (key,val) from MRU to LRU. Draw HEAD .. nodes .. TAIL.
    hi: index (in the drawn row) to mark active; ghost: index marked bad."""
    labels = ["HEAD"] + [f"{k}:{v}" for (k, v) in order] + ["TAIL"]
    n = len(labels)
    vals = labels  # value text shown in each node
    # edges: HEAD -> first node -> ... -> TAIL (forward chain, index i -> i+1)
    edges = [[i, i + 1] for i in range(n - 1)]
    edges.append([n - 1, None])  # tail's next is null stub
    marks = {}
    for i, (k, v) in enumerate(order):
        marks[str(i + 1)] = "good"
    if hi is not None:
        marks[str(hi)] = "active"
    if ghost is not None:
        marks[str(ghost)] = "bad"
    # sentinels dimmed
    marks["0"] = "dim"
    marks[str(n - 1)] = "dim"
    state = [["capacity", cap], ["size", len(order)]]
    if mapd is not None:
        state.append(["map", "{" + ", ".join(f"{k}" for k, _ in order) + "}"])
    if extra:
        state.extend(extra)
    f = dict(act=act, vals=vals, edges=edges, code="ops", line=line,
             marks=marks, note=note, state=state)
    if intro:
        f["intro"] = intro
    if invariant:
        f["invariant"] = invariant
    if banner:
        f["banner"] = banner
    return f


# ---- Act 0: the rule ----
add(**render([(1, 1), (2, 2)], cap=2, act=0, line=0,
    intro="the dict jumps straight to a node; the list only re-orders it. No scan.",
    invariant="the list reads most-recent (left) to least-recent (right, by tail).",
    note="An LRU cache = a dict (key -> node) plus a doubly linked list ordered by "
    "recency. Left of HEAD-side is most recent; right by TAIL is least recent.",
    mapd=True, extra=[["order", "MRU 2,1 LRU"]]))
add(**render([(1, 1), (2, 2)], cap=2, act=0, line=1, hi=1,
    note="A get(key) uses the dict to land on the node in O(1) — no walking the "
    "list to find it. Then the list moves it to the front.",
    mapd=True, extra=[["get", "dict -> node"]]))

# ---- Act 1: run get / put ----
# Start state after put(1,1), put(2,2): order MRU->LRU = [2, 1]
order = [(2, 2), (1, 1)]
add(**render(order, cap=2, act=1, line=4,
    intro="watch a used key jump to the front, and the size climb to capacity.",
    invariant="the node right before TAIL is always the next to be evicted.",
    note="Start: put(1,1) then put(2,2). Most recent is 2 (front), least recent is "
    "1 (by TAIL).", mapd=True, extra=[["last op", "put(2,2)"]]))

# get(1): dict finds node 1, move it to front. New order [1, 2]
add(**render(order, cap=2, act=1, line=1, hi=2,
    note="get(1): the dict lands on node 1:1 directly (it's the LRU node here).",
    mapd=True, extra=[["get(1)", "-> 1"]]))
order = [(1, 1), (2, 2)]
add(**render(order, cap=2, act=1, line=2, hi=1,
    note="Unlink 1 and re-add it just after HEAD. Now 1 is most recent, 2 is least "
    "recent — its arrow moved to the front of the chain.",
    mapd=True, extra=[["order", "MRU 1,2 LRU"], ["returned", 1]]))

# put(3,3): full -> evict tail.prev = 2, then add 3 at front
add(**render(order, cap=2, act=1, line=5, hi=2, ghost=2,
    note="put(3,3): cache is full (size 2 = capacity). The node before TAIL is 2 — "
    "the least recently used. Evict it.",
    mapd=True, extra=[["evict", "key 2 (LRU)"]]))
order = [(3, 3), (1, 1)]
add(**render(order, cap=2, act=1, line=6, hi=1,
    note="Drop 2 from the list and the dict, then add 3 at the front. Key 2 is gone.",
    mapd=True, extra=[["order", "MRU 3,1 LRU"], ["get(2) now", -1]],
    banner="put(3,3) evicted key 2 — the least recently used"))

# ---- Act 2: eviction detail + edge (capacity 1) ----
add(**render(order, cap=2, act=2, line=5,
    intro="the sentinels HEAD/TAIL mean 'evict' is always just tail.prev — no edge "
    "cases at the ends.",
    invariant="eviction never scans: it is always the one fixed node before TAIL.",
    note="Because two sentinels (HEAD, TAIL) bracket the real nodes, the least-recent "
    "node is always exactly tail.prev — found in O(1), never searched for.",
    mapd=True, extra=[["LRU node", "tail.prev = 1"]]))

# Edge: capacity 1
add(**render([(5, 50)], cap=1, act=2, line=6,
    note="Edge: capacity 1. put(5,50) fills the one slot.",
    mapd=True, extra=[["order", "just 5"]]))
add(**render([(5, 50)], cap=1, act=2, line=5, hi=1, ghost=1,
    note="put(9,90): full at capacity 1, so the single node 5 is both MRU and LRU — "
    "evict it.", mapd=True, extra=[["evict", "key 5"]]))
add(**render([(9, 90)], cap=1, act=2, line=6, hi=1,
    note="Every new key evicts the previous one. get(5) now returns -1; only 9 remains.",
    mapd=True, extra=[["get(5)", -1], ["get(9)", 90]],
    banner="Capacity 1: each put evicts the one prior key"))

trace = {
    "player": "linkedlist",
    "title": "LRU Cache - a dict finds the node, the linked list re-orders it",
    "acts": ["The rule: dict + recency list", "Run get / put", "Eviction + capacity-1 edge"],
    "code": {"ops": CODE},
    "legend": [["active", "the node we touched"], ["good", "live cache node"],
               ["bad", "evicted"], ["dim", "HEAD / TAIL sentinel"]],
    "vals": ["HEAD", "1:1", "2:2", "TAIL"],
    "edges": [[0, 1], [1, 2], [2, 3], [3, None]],
    "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
