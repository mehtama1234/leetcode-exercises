"""Rich full-arc trace for Implement Queue using Stacks (linear renderer).
A stack is LIFO; a queue must be FIFO. One stack reverses order; two stacks
reverse it twice, restoring arrival order. Arc: the problem -> the two-reversal
trick -> an interleaved edge where a transfer happens mid-stream. Mirrors the
two-stack solution in solution.py exactly. Writes trace.json.
"""
import json
import os

frames = []

CODE = [
    "def _shift():",
    "    if not s_out:            # only when out is empty",
    "        while s_in:",
    "            s_out.append(s_in.pop())",
    "def push(x): s_in.append(x)",
    "def pop():  _shift(); return s_out.pop()",
    "def peek(): _shift(); return s_out[-1]",
]


def add(**f):
    frames.append(f)


# s_in is drawn as the linear row: index 0 is the bottom, last index is the top
# (newest). s_out lives in the sidebar; its FRONT (what pop/peek return) is
# s_out[-1], so we show the sidebar rows top-to-bottom as "front first".
def out_sidebar(s_out):
    # front of queue = s_out[-1]; list rows from front (top) to back (bottom)
    rows = [[("front" if i == 0 else ""), v] for i, v in enumerate(reversed(s_out))]
    if not rows:
        rows = [["(empty)", ""]]
    return {"title": "s_out (serves; front on top)", "rows": rows}


def snapshot(**kw):
    """Build a frame carrying the current s_in as cells and s_out as sidebar."""
    s_in = kw.pop("s_in")
    s_out = kw.pop("s_out")
    kw["cells"] = list(s_in) if s_in else [None]
    kw["labels"] = list(range(len(s_in))) if s_in else [0]
    kw["sidebar"] = out_sidebar(s_out)
    add(**kw)


# ---- Act 0: the problem — a stack reverses order ----
s_in, s_out = [], []
snapshot(act=0, s_in=s_in, s_out=s_out, code="ops", line=4,
    intro="push 1,2,3 and read the stack top-down — it comes out 3,2,1, the WRONG "
    "order for a queue.",
    invariant="s_in holds arrivals with the newest on top (highest index).",
    note="A queue serves oldest-first (FIFO). A stack serves newest-first (LIFO). "
    "Push 1, 2, 3 onto the 'in' stack and watch the order.",
    marks={"0": "dim"}, state=[["s_in", "[]"], ["want first out", 1]])
for x in (1, 2, 3):
    s_in.append(x)
    top = len(s_in) - 1
    snapshot(act=0, s_in=s_in, s_out=s_out, code="ops", line=4,
        note=f"push({x}): {x} lands on TOP of s_in (index {top}).",
        pointers={"top": top}, marks={str(top): "active"},
        state=[["s_in", str(s_in)], ["top", x]])
snapshot(act=0, s_in=s_in, s_out=s_out, code="ops", line=4,
    note="s_in top-to-bottom is 3,2,1 — a single stack would serve 3 first, but a "
    "queue owes us 1 first. One reversal is backward; we need a second.",
    marks={"2": "bad"}, state=[["s_in top", 3], ["owed first", 1]],
    banner="One stack alone serves 3,2,1 — reversed from FIFO")

# ---- Act 1: the trick — two reversals restore arrival order ----
s_in, s_out = [1, 2, 3], []
snapshot(act=1, s_in=s_in, s_out=s_out, code="ops", line=5,
    intro="a pop with an empty s_out pours all of s_in across — reversing again, so "
    "the true front (1) ends up on TOP of s_out.",
    invariant="each element is moved from s_in to s_out at most once, ever.",
    note="pop() is called. s_out is empty, so _shift runs: pour s_in into s_out one "
    "at a time. A second reversal restores 1,2,3 order.",
    marks={"2": "active"}, state=[["s_out", "[]"], ["action", "transfer"]])
# transfer: while s_in: s_out.append(s_in.pop())
while s_in:
    moved = s_in.pop()
    s_out.append(moved)
    snapshot(act=1, s_in=s_in, s_out=s_out, code="ops", line=3,
        note=f"Move {moved}: pop it off s_in's top, push it onto s_out. "
             f"s_out front is now {s_out[-1]}.",
        marks={str(len(s_in) - 1): "active"} if s_in else {},
        state=[["moved", moved], ["s_in", str(s_in)], ["s_out front", s_out[-1]]])
front = s_out[-1]
served = s_out.pop()
snapshot(act=1, s_in=s_in, s_out=s_out, code="ops", line=5,
    note=f"After the transfer, s_out top is {front} — the oldest arrival. pop() "
         f"returns {served}. Two reversals gave back FIFO order.",
    state=[["returned", served], ["s_out", str(s_out)]],
    banner=f"pop() -> {served}  (oldest arrival served first)")
peeked = s_out[-1]
snapshot(act=1, s_in=s_in, s_out=s_out, code="ops", line=6,
    note=f"peek() now finds s_out non-empty, so NO transfer — it just reads the top: "
         f"{peeked}. The remaining 2,3 stay ready in order.",
    state=[["peek()", peeked], ["s_out", str(s_out)]])
snapshot(act=1, s_in=s_in, s_out=s_out, code="ops", line=1,
    note="Amortized O(1): each element is pushed to s_in once, moved to s_out once, "
    "and popped once — three constant steps over its whole life, even though the "
    "one pop that triggers a transfer looks O(n).",
    state=[["per element", "push+move+pop"], ["amortized", "O(1)"]])

# ---- Act 2: edge — interleave so a transfer happens mid-stream ----
# push1; pop->1; push2; push3; peek->2; push4; pop->2; pop->3; pop->4
s_in, s_out = [], []
snapshot(act=2, s_in=s_in, s_out=s_out, code="ops", line=4,
    intro="pushes keep going to s_in even while s_out still has items — 4 arrives "
    "after a transfer and must still leave last.",
    invariant="_shift only fires when s_out is empty, so half-drained s_out is safe.",
    note="Edge: interleave. push(1).", marks={"0": "dim"},
    state=[["s_in", "[]"], ["s_out", "[]"]])
s_in.append(1)
snapshot(act=2, s_in=s_in, s_out=s_out, code="ops", line=4,
    note="push(1): s_in = [1].", pointers={"top": 0}, marks={"0": "active"},
    state=[["s_in", "[1]"]])
# pop() -> _shift moves 1 to s_out, then serves 1
s_out.append(s_in.pop())
served = s_out.pop()
snapshot(act=2, s_in=s_in, s_out=s_out, code="ops", line=5,
    note=f"pop(): s_out empty -> shift 1 across, then serve it. Returns {served}. Both "
    "stacks empty again.", state=[["returned", served], ["s_in", "[]"], ["s_out", "[]"]],
    banner="pop() -> 1")
# push 2, 3
for x in (2, 3):
    s_in.append(x)
    top = len(s_in) - 1
    snapshot(act=2, s_in=s_in, s_out=s_out, code="ops", line=4,
        note=f"push({x}): s_in = {s_in}.", pointers={"top": top},
        marks={str(top): "active"}, state=[["s_in", str(s_in)]])
# peek() -> _shift (s_out empty) moves 3 then 2; front is 2
while s_in:
    s_out.append(s_in.pop())
peeked = s_out[-1]
snapshot(act=2, s_in=s_in, s_out=s_out, code="ops", line=6,
    note=f"peek(): s_out empty -> shift 2,3 across (now s_out front is 2). Returns "
         f"{peeked} without removing it — 2 arrived before 3.",
    state=[["peek()", peeked], ["s_out front", 2]])
# push 4 -> goes to s_in while s_out still holds [3,2] (front 2)
s_in.append(4)
snapshot(act=2, s_in=s_in, s_out=s_out, code="ops", line=4,
    note="push(4): s_out still has 2,3 waiting, so 4 goes to s_in and does NOT jump "
    "the line. No transfer fires (s_out isn't empty).",
    pointers={"top": len(s_in) - 1}, marks={str(len(s_in) - 1): "active"},
    state=[["s_in", str(s_in)], ["s_out front", s_out[-1]]])
# pop -> 2 (no shift, s_out non-empty)
a = s_out.pop()
snapshot(act=2, s_in=s_in, s_out=s_out, code="ops", line=5,
    note=f"pop(): s_out non-empty, no shift. Serve {a}.",
    state=[["returned", a], ["s_out", str(s_out)]], banner="pop() -> 2")
# pop -> 3 (no shift, s_out still has [3])
b = s_out.pop()
snapshot(act=2, s_in=s_in, s_out=s_out, code="ops", line=5,
    note=f"pop(): still no shift, serve {b}. Now s_out is empty and only 4 remains "
    "in s_in.", state=[["returned", b], ["s_in", str(s_in)], ["s_out", "[]"]],
    banner="pop() -> 3")
# pop -> 4 (shift moves 4)
s_out.append(s_in.pop())
c = s_out.pop()
snapshot(act=2, s_in=s_in, s_out=s_out, code="ops", line=5,
    note=f"pop(): s_out empty -> shift 4 across, serve {c}. It arrived after the "
    "transfer yet still leaves last — FIFO held.",
    state=[["returned", c], ["s_in", "[]"], ["s_out", "[]"]],
    banner="pop() -> 4  (pushed after a transfer, still served last)")

trace = {
    "player": "linear",
    "title": "Queue using Stacks - two reversals restore arrival order",
    "acts": ["The problem: LIFO vs FIFO", "The trick: two reversals",
             "Edge: transfer mid-stream"],
    "code": {"ops": CODE},
    "legend": [["active", "element being moved / served"], ["good", "served / front"],
               ["bad", "wrong order (one stack)"], ["dim", "waiting"]],
    "cells": [1], "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
