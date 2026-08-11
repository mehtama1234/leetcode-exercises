"""Rich full-arc trace for Reorder List (linked-list renderer).
Arc: the plan (three known moves) -> find middle -> reverse 2nd half -> weave ->
edge (two nodes, no-op). Mirrors reorder_list in solution.py. Nodes stay in
physical order; edges follow each node's live .next. Writes trace.json.
"""
import json
import os

frames = []

CODE_MID = [
    "slow = fast = head",
    "while fast and fast.next:",
    "    slow = slow.next",
    "    fast = fast.next.next",
]
CODE_REV = [
    "prev = None; cur = slow",
    "while cur:",
    "    nxt = cur.next",
    "    cur.next = prev",
    "    prev = cur; cur = nxt",
]
CODE_WEAVE = [
    "first = head; second = prev",
    "while second and second.next:",
    "    f_next = first.next",
    "    s_next = second.next",
    "    first.next = second",
    "    second.next = f_next",
    "    first = f_next; second = s_next",
]


def add(**f):
    frames.append(f)


# List 1 2 3 4 5 at indices 0..4. NEXT holds each node's live .next.
vals = [1, 2, 3, 4, 5]
NEXT = {0: 1, 1: 2, 2: 3, 3: 4, 4: None}


def edges():
    return [[i, NEXT[i]] for i in range(len(vals))]


# ============ Act 0: the plan ============
add(act=0, vals=vals, edges=edges(), code="mid", line=0,
    intro="the target front-back-front-back pattern is three standard list moves.",
    invariant="everything happens in place; no nodes are copied.",
    note="We want 1 5 2 4 3: front, back, front, back. That is exactly: split in half, "
    "reverse the back half, then interleave the two halves.",
    pointers={}, state=[["goal", "1 5 2 4 3"]])

# ============ Act 1: find the middle ============
add(act=1, vals=vals, edges=edges(), code="mid", line=0,
    intro="fast/slow: when fast runs out, slow marks the start of the second half.",
    invariant="slow is always half as far along as fast.",
    note="Step one: locate the midpoint with fast/slow pointers.",
    pointers={"slow": 0, "fast": 0}, state=[["slow", 1], ["fast", 1]])

slow = 0
fast = 0
while fast is not None and NEXT[fast] is not None:
    slow = NEXT[slow]
    fast = NEXT[NEXT[fast]]
    add(act=1, code="mid", line=2, edges=edges(),
        note=f"slow -> {vals[slow]}, fast -> "
             f"{vals[fast] if fast is not None else 'null'}.",
        pointers={"slow": slow, "fast": fast if fast is not None else None},
        marks={str(slow): "active"},
        state=[["slow", vals[slow]],
               ["fast", vals[fast] if fast is not None else "null"]])

add(act=1, code="mid", line=1, edges=edges(),
    note=f"fast is done. slow rests on {vals[slow]} — the start of the second half "
         f"({vals[slow]} onward).",
    pointers={"slow": slow}, marks={str(k): "good" for k in range(slow, len(vals))},
    state=[["second half starts", vals[slow]]])

mid = slow  # index 2 (value 3)

# ============ Act 2: reverse the second half ============
add(act=2, vals=vals, edges=edges(), code="rev", line=0,
    intro="flip every arrow from the midpoint onward; arrows move below the row.",
    invariant="the second half becomes a valid chain running the other way.",
    note=f"Step two: reverse everything from {vals[mid]} onward, the same flip-each-arrow "
    f"move as problem 206.",
    pointers={"cur": mid, "prev": None}, marks={str(k): "good" for k in range(mid, len(vals))},
    state=[["prev", "null"], ["cur", vals[mid]]])

prev = None
cur = mid
while cur is not None:
    nxt = NEXT[cur]
    add(act=2, code="rev", line=2, edges=edges(),
        note=f"Remember {vals[cur]}.next = "
             f"{vals[nxt] if nxt is not None else 'null'} before overwriting it.",
        pointers={"cur": cur, "prev": prev if prev is not None else None,
                  "nxt": nxt if nxt is not None else None},
        state=[["cur", vals[cur]], ["nxt", vals[nxt] if nxt is not None else "null"]])
    NEXT[cur] = prev
    add(act=2, code="rev", line=3, edges=edges(),
        note=f"Flip: {vals[cur]}'s arrow now points back to "
             f"{vals[prev] if prev is not None else 'null'} (arc drops below the row).",
        pointers={"cur": cur, "prev": prev if prev is not None else None,
                  "nxt": nxt if nxt is not None else None},
        marks={str(cur): "good"},
        state=[["flipped", vals[cur]]])
    prev = cur
    cur = nxt

add(act=2, code="rev", line=1, edges=edges(),
    note=f"Second half reversed: it now heads {vals[prev]} -> ... . prev = {vals[prev]} is "
         f"its new head.",
    pointers={"prev": prev}, marks={str(k): "good" for k in range(mid, len(vals))},
    state=[["reversed head", vals[prev]]])

rev_head = prev  # index 4 (value 5); chain 5->4->3

# ============ Act 3: weave the two halves ============
add(act=3, vals=vals, edges=edges(), code="weave", line=0,
    intro="alternate: one node from the front, one from the reversed back.",
    invariant="second half is <= first half, so we stop when second runs out.",
    note=f"Step three: interleave. first starts at {vals[0]}, second at the reversed "
    f"head {vals[rev_head]}.",
    pointers={"first": 0, "second": rev_head},
    state=[["first", vals[0]], ["second", vals[rev_head]]])

first = 0
second = rev_head
while second is not None and NEXT[second] is not None:
    f_next = NEXT[first]
    s_next = NEXT[second]
    NEXT[first] = second
    add(act=3, code="weave", line=4, edges=edges(),
        note=f"Link {vals[first]} -> {vals[second]} (front node then back node).",
        pointers={"first": first, "second": second},
        marks={str(first): "good", str(second): "good"},
        state=[["linked", f"{vals[first]}->{vals[second]}"]])
    NEXT[second] = f_next
    add(act=3, code="weave", line=5, edges=edges(),
        note=f"Then {vals[second]} -> {vals[f_next]} to rejoin the front thread; advance both.",
        pointers={"first": f_next, "second": s_next if s_next is not None else None},
        marks={str(first): "good", str(second): "good"},
        state=[["next first", vals[f_next]],
               ["next second", vals[s_next] if s_next is not None else "null"]])
    first = f_next
    second = s_next

# verify final order by walking from head
order = []
p = 0
while p is not None:
    order.append(vals[p])
    p = NEXT[p]
add(act=3, code="weave", line=1, edges=edges(),
    note="Woven together. Reading from the head: " + " ".join(str(x) for x in order) + ".",
    pointers={"head": 0}, marks={str(k): "good" for k in range(len(vals))},
    state=[["result", " ".join(str(x) for x in order)]],
    banner="Reordered: 1 5 2 4 3")

# ============ Act 4: edge — two nodes, no-op ============
vals2 = [1, 2]
add(act=4, vals=vals2, edges=[[0, 1], [1, None]], code="weave", line=1,
    intro="with two nodes the weave loop never runs — the list is unchanged.",
    invariant="second.next is null, so the while condition is false at once.",
    note="Edge case: [1,2]. The midpoint split gives a one-node second half; second.next "
    "is null, so nothing is woven and the list stays [1,2].",
    pointers={"first": 0, "second": 1}, marks={"0": "good", "1": "good"},
    state=[["result", "1 2"]],
    banner="Two nodes: already in order")

trace = {
    "player": "linkedlist",
    "title": "Reorder List - split, reverse the back half, weave",
    "acts": ["The plan", "Find the middle", "Reverse second half", "Weave halves",
             "Edge: two nodes"],
    "code": {"mid": CODE_MID, "rev": CODE_REV, "weave": CODE_WEAVE},
    "legend": [["good", "resolved / second half / linked"], ["active", "slow pointer"]],
    "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
