"""Rich full-arc trace for Remove Nth Node From End (linked-list renderer).
Arc: two-pass (measure length, then re-walk) -> one-pass gap-of-n+1 -> edge (remove head).
Mirrors remove_nth_two_pass and remove_nth in solution.py. A dummy head sits at
index 0 (shown as value "D"); real nodes follow. Writes trace.json.
"""
import json
import os

frames = []

CODE_SLOW = [
    "dummy = ListNode(0, head)",
    "length = 0; node = head",
    "while node:",
    "    length += 1; node = node.next",
    "before = dummy",
    "for _ in range(length - n):",
    "    before = before.next",
    "before.next = before.next.next",
    "return dummy.next",
]

CODE_FAST = [
    "dummy = ListNode(0, head)",
    "lead = dummy; trail = dummy",
    "for _ in range(n + 1):",
    "    lead = lead.next",
    "while lead:",
    "    lead = lead.next; trail = trail.next",
    "trail.next = trail.next.next",
    "return dummy.next",
]


def add(**f):
    frames.append(f)


# Real list 1 2 3 4 5, remove n=2 from the end -> remove value 4.
# Render with a dummy at index 0: values ["D",1,2,3,4,5]; edges chain forward.
N = 2
real = [1, 2, 3, 4, 5]
vals = ["D"] + real                 # index 0 = dummy
length = len(real)


def fwd_edges(skip_from=None):
    """Forward chain over the whole row; if skip_from given, that node's arrow
    jumps two ahead (the unlink)."""
    e = []
    for i in range(len(vals)):
        if i == skip_from:
            tgt = i + 2 if i + 2 < len(vals) else None
        else:
            tgt = i + 1 if i + 1 < len(vals) else None
        e.append([i, tgt])
    return e


# ============ Act 0: two-pass ============
add(act=0, vals=vals, edges=fwd_edges(), code="slow", line=0,
    intro="the same nodes get walked twice — once to count, once to reach the target.",
    invariant="'nth from the end' equals '(length - n)th from the front'.",
    note="A dummy node (D) sits before the head so deleting the real head is no special "
    "case. First we must learn the length, because 'from the end' hides the real index.",
    pointers={"node": 1}, state=[["length", 0], ["walks", 0]])

walks = 0
for i in range(1, len(vals)):
    walks += 1
    add(act=0, code="slow", line=3, edges=fwd_edges(),
        note=f"Counting node {vals[i]}. length is now {i}.",
        pointers={"node": i}, marks={str(i): "dim"},
        state=[["length", i], ["walks", walks]])

# pass 2: walk before to length-n
steps = length - N   # = 3, lands 'before' on node index 3 (value 3)
add(act=0, code="slow", line=4, edges=fwd_edges(),
    note=f"Length is {length}. The target is {length - N} from the front (value "
         f"{real[length - N]}); we stop 'before' on the node just ahead of it.",
    pointers={"before": 0}, marks={str(j): "dim" for j in range(1, len(vals))},
    state=[["length", length], ["target from front", length - N]])

before = 0
for s in range(steps):
    walks += 1
    before += 1
    add(act=0, code="slow", line=6, edges=fwd_edges(),
        note=f"Second walk step {s + 1} of {steps}: before -> {vals[before]} "
             f"(re-touching a counted node).",
        pointers={"before": before}, marks={str(before): "bad"},
        state=[["before", vals[before]], ["walks", walks]])

target = before + 1
add(act=0, code="slow", line=7, edges=fwd_edges(skip_from=before),
    note=f"before is on {vals[before]}; skip its arrow past {vals[target]} to "
         f"{vals[target + 1]}. Node {vals[target]} is unlinked. Total {walks} node-steps.",
    pointers={"before": before}, marks={str(target): "bad", str(before): "good"},
    state=[["removed", vals[target]], ["walks", walks]],
    banner="Two passes removed 4 -> 1 2 3 5")

# ============ Act 1: name the waste ============
add(act=1, vals=vals, edges=fwd_edges(), code="slow", line=1,
    intro="one pass can do it by holding two pointers a fixed gap apart.",
    invariant="if lead is n+1 ahead of trail, trail is exactly one before the target.",
    note="The waste: the whole first pass only measured length. Keep two pointers n+1 "
    "apart instead — when the front one falls off the end, the back one is already one "
    "step before the node to delete.",
    pointers={"trail": 0, "lead": 0}, state=[["gap wanted", N + 1]])

# ============ Act 2: one-pass gap ============
add(act=2, vals=vals, edges=fwd_edges(), code="fast", line=1,
    intro="first open a gap of n+1, then move both together until lead runs out.",
    invariant="lead - trail stays n+1 for the whole second loop.",
    note="Both start at the dummy. Advance lead n+1 = 3 steps to open the gap.",
    pointers={"trail": 0, "lead": 0}, state=[["lead", "D"], ["trail", "D"]])

lead = 0
for s in range(N + 1):
    lead += 1
    add(act=2, code="fast", line=3, edges=fwd_edges(),
        note=f"Opening the gap, step {s + 1} of {N + 1}: lead -> {vals[lead]}.",
        pointers={"trail": 0, "lead": lead}, marks={str(lead): "active"},
        state=[["lead", vals[lead]], ["trail", "D"], ["gap", lead]])

trail = 0
while lead + 1 < len(vals):   # while lead (not off end)
    lead += 1
    trail += 1
    add(act=2, code="fast", line=5, edges=fwd_edges(),
        note=f"Move both: lead -> {vals[lead]}, trail -> {vals[trail]}. Gap still {N + 1}.",
        pointers={"trail": trail, "lead": lead}, marks={str(trail): "active"},
        state=[["lead", vals[lead]], ["trail", vals[trail]]])

# lead is now on last node; one more conceptual step puts it off the end
add(act=2, code="fast", line=4, edges=fwd_edges(),
    note=f"lead reached the last node; one more step and it is null. trail rests on "
         f"{vals[trail]} — exactly one before the target.",
    pointers={"trail": trail, "lead": None}, marks={str(trail): "good"},
    state=[["trail", vals[trail]], ["lead", "null"]])

tgt = trail + 1
add(act=2, code="fast", line=6, edges=fwd_edges(skip_from=trail),
    note=f"Unlink: trail ({vals[trail]}) skips past {vals[tgt]}. Done in one pass.",
    pointers={"trail": trail}, marks={str(tgt): "bad", str(trail): "good"},
    state=[["removed", vals[tgt]]],
    banner="One pass removed 4 -> 1 2 3 5")

# ============ Act 3: edge — remove the head ============
vals2 = ["D", 1, 2]     # list [1,2], n=2 -> remove head (value 1)
N2 = 2
add(act=3, vals=vals2, edges=[[0, 1], [1, 2], [2, None]], code="fast", line=1,
    intro="the dummy makes deleting the first real node just like any other.",
    invariant="trail landing on the dummy means the head itself is removed.",
    note="Edge case: list [1,2], remove the 2nd from the end — that is the head. Open a "
    "gap of n+1 = 3 from the dummy.",
    pointers={"trail": 0, "lead": 0}, state=[["lead", "D"], ["trail", "D"]])

# lead advances 3 steps: D->1->2->null
add(act=3, code="fast", line=3, edges=[[0, 1], [1, 2], [2, None]],
    note="After opening the gap, lead has run off the end (null) while trail is still on "
    "the dummy.",
    pointers={"trail": 0, "lead": None}, marks={"0": "good"},
    state=[["lead", "null"], ["trail", "D"]])

add(act=3, code="fast", line=6, edges=[[0, 2], [1, None], [2, None]],
    note="trail is the dummy, so we skip its arrow past node 1 to node 2 — the head is "
    "removed with no special case.",
    pointers={"trail": 0}, marks={"1": "bad", "0": "good"},
    state=[["removed", "1 (head)"]],
    banner="Dummy head: removing the first node is uniform")

trace = {
    "player": "linkedlist",
    "title": "Remove Nth From End - one pass with a gap of n+1",
    "acts": ["Brute: measure then re-walk", "The waste", "One pass, fixed gap",
             "Edge: remove the head"],
    "code": {"slow": CODE_SLOW, "fast": CODE_FAST},
    "legend": [["good", "pointer resting here / kept"], ["bad", "removed / re-walked"],
               ["active", "pointer moving"], ["dim", "counted node"]],
    "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
