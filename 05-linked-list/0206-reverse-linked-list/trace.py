"""Rich full-arc trace for Reverse Linked List (linked-list renderer reference).
Arc: the idea (flip each arrow) -> reverse in one pass -> edge (single node).
Mirrors the iterative reversal in solution.py. Nodes stay in physical order;
edges reflect each node's current .next. Writes trace.json.
"""
import json
import os

vals = [1, 2, 3, 4]
frames = []

CODE = [
    "prev = None",
    "curr = head",
    "while curr:",
    "    nxt = curr.next",
    "    curr.next = prev",
    "    prev = curr",
    "    curr = nxt",
    "return prev",
]


def add(**f):
    frames.append(f)


def edges_from(nxt):
    # nxt[i] = index that node i points to, or None
    return [[i, nxt[i]] for i in range(len(vals))]


# forward list 1->2->3->4->null
nxt = {0: 1, 1: 2, 2: 3, 3: None}

# ---- Act 0: the idea ----
add(act=0, vals=vals, edges=edges_from(nxt), code="rev", line=0,
    intro="every arrow ends up pointing the other way — nothing moves in memory.",
    invariant="the list stays a valid chain the whole time; only arrows flip.",
    note="Reversing means every 'next' arrow should point backward instead of "
    "forward. We walk once and flip each arrow as we pass it.",
    pointers={"curr": 0}, state=[["list", "1->2->3->4"]])

# ---- Act 1: reverse in one pass ----
prev = None
curr = 0
add(act=1, vals=vals, edges=edges_from(nxt), code="rev", line=1,
    intro="prev trails behind; each node's arrow is bent back to prev.",
    invariant="everything left of curr is already reversed.",
    note="Two markers: curr is where we are, prev is the already-reversed part "
    "behind us (starts empty).",
    pointers={"curr": 0, "prev": None}, state=[["prev", "null"], ["curr", 1]])
while curr is not None:
    nx = nxt[curr]
    add(act=1, code="rev", line=3,
        note=f"Remember curr.next ({vals[nx] if nx is not None else 'null'}) before we "
             f"overwrite it — otherwise we lose the rest of the list.",
        pointers={"prev": prev if prev is not None else None, "curr": curr,
                  "nxt": nx if nx is not None else None},
        edges=edges_from(nxt), state=[["curr", vals[curr]],
                                      ["nxt", vals[nx] if nx is not None else "null"]])
    nxt[curr] = prev  # flip
    add(act=1, code="rev", line=4,
        note=f"Flip: node {vals[curr]}'s arrow now points back to "
             f"{vals[prev] if prev is not None else 'null'}.",
        pointers={"prev": prev if prev is not None else None, "curr": curr,
                  "nxt": nx if nx is not None else None},
        edges=edges_from(nxt), marks={str(curr): "good"},
        state=[["flipped", vals[curr]]])
    prev = curr
    curr = nx

add(act=1, code="rev", line=7,
    note=f"curr fell off the end. prev is the new head: {vals[3]}. The list now reads "
    f"4->3->2->1.",
    pointers={"prev": 3}, edges=edges_from(nxt),
    marks={"0": "good", "1": "good", "2": "good", "3": "good"},
    state=[["new head", vals[3]]], banner="Reversed: 4 -> 3 -> 2 -> 1")

# ---- Act 2: edge ----
add(act=2, vals=[7], edges=[[0, None]], code="rev", line=7,
    intro="the loop body runs zero or one time — nothing to flip.",
    invariant="prev ends as the head; for one node that is the node itself.",
    note="Edge case: a single node (or an empty list). curr flips nothing and prev "
    "ends pointing at the same node — reversing one node gives it back.",
    pointers={"prev": 0}, marks={"0": "good"}, state=[["head", 7]],
    banner="One node reverses to itself")

trace = {
    "player": "linkedlist",
    "title": "Reverse Linked List - flip each arrow in a single pass",
    "acts": ["The idea: flip arrows", "Reverse in one pass", "Edge: single node"],
    "code": {"rev": CODE},
    "legend": [["good", "already reversed"]],
    "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
