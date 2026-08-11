"""Rich full-arc trace for Linked List Cycle (linked-list renderer).
Arc: seen-set (O(n) memory, visible) -> Floyd's fast/slow (O(1)) -> no-cycle edge.
Mirrors has_cycle_seen and has_cycle in solution.py. A cycle edge is drawn as a
backward arc (to_idx < from_idx), which the renderer arcs below the row.
Writes trace.json.
"""
import json
import os

frames = []

CODE_SEEN = [
    "seen = set()",
    "node = head",
    "while node:",
    "    if id(node) in seen:",
    "        return True",
    "    seen.add(id(node))",
    "    node = node.next",
    "return False",
]

CODE_FAST = [
    "slow = head",
    "fast = head",
    "while fast and fast.next:",
    "    slow = slow.next",
    "    fast = fast.next.next",
    "    if slow is fast:",
    "        return True",
    "return False",
]


def add(**f):
    frames.append(f)


# List 3 -> 2 -> 0 -> -4, and -4 loops back to index 1 (value 2).
vals = [3, 2, 0, -4]
NEXT = {0: 1, 1: 2, 2: 3, 3: 1}  # 3 points back to index 1 -> cycle


def edges():
    return [[i, NEXT[i]] for i in range(len(vals))]


# ============ Act 0: brute force — remember every node ============
add(act=0, vals=vals, edges=edges(), code="seen", line=0,
    intro="every node we stand on gets stored — memory grows with the list.",
    invariant="a cycle means we return to a node already in the set.",
    note="The honest idea: a cycle is just 'we came back somewhere we have been'. So "
    "remember each node we visit and check for a repeat. The curved arrow below is the "
    "cycle: -4 points back to 2.",
    pointers={"node": 0}, state=[["seen", 0]])

seen = set()
node = 0
found = None
step = 0
while step < 8:  # bounded; will find repeat
    if node in seen:
        found = node
        add(act=0, code="seen", line=4, edges=edges(),
            note=f"Node {vals[node]} is already in the set — we have looped back. Cycle found.",
            pointers={"node": node}, marks={str(node): "good"},
            state=[["seen", len(seen)], ["repeat", vals[node]]],
            banner="Set method: cycle detected (used O(n) memory)")
        break
    add(act=0, code="seen", line=5, edges=edges(),
        note=f"First time on {vals[node]}. Store it (memory now holds {len(seen) + 1} nodes) "
             f"and move on.",
        pointers={"node": node},
        marks={str(k): "dim" for k in seen} | {str(node): "active"},
        state=[["seen", len(seen) + 1]])
    seen.add(node)
    node = NEXT[node]
    step += 1

# ============ Act 1: name the waste ============
add(act=1, vals=vals, edges=edges(), code="seen", line=0,
    intro="Floyd's trick decides the same yes/no with zero extra memory.",
    invariant="two runners on a loop must eventually collide.",
    note="The waste is the set itself — O(n) memory just to answer yes or no. Two pointers "
    "at different speeds settle it for free: on a circular track a faster runner always laps "
    "a slower one.",
    pointers={"node": 0}, state=[["extra memory", "O(n) -> O(1)"]])

# ============ Act 2: Floyd's fast/slow ============
add(act=2, vals=vals, edges=edges(), code="fast", line=1,
    intro="slow moves 1, fast moves 2; if they ever meet, there is a cycle.",
    invariant="with a cycle the gap between them shrinks by one each turn.",
    note="Both start at the head. Each turn slow steps once, fast steps twice.",
    pointers={"slow": 0, "fast": 0}, state=[["slow", vals[0]], ["fast", vals[0]]])

slow = 0
fast = 0
for _ in range(10):
    slow = NEXT[slow]
    fast = NEXT[NEXT[fast]]
    met = slow == fast
    add(act=2, code="fast", line=5, edges=edges(),
        note=f"slow -> {vals[slow]}, fast -> {vals[fast]}." +
             (" They collided — a cycle exists." if met else " No collision yet."),
        pointers={"slow": slow, "fast": fast},
        marks={str(slow): ("good" if met else "active")},
        state=[["slow", vals[slow]], ["fast", vals[fast]],
               ["met", "yes" if met else "no"]])
    if met:
        add(act=2, code="fast", line=6, edges=edges(),
            note=f"slow is fast — both on {vals[slow]}. Return True. No extra memory used.",
            pointers={"slow": slow, "fast": fast}, marks={str(slow): "good"},
            state=[["result", "cycle"]],
            banner="Floyd: cycle detected with O(1) memory")
        break

# ============ Act 3: no-cycle edge ============
vals2 = [1, 2, 3, 4]
E2 = [[i, i + 1 if i + 1 < len(vals2) else None] for i in range(len(vals2))]
add(act=3, vals=vals2, edges=E2, code="fast", line=2,
    intro="with no loop, fast simply runs off the end.",
    invariant="fast reaches null before it can ever meet slow.",
    note="Edge case: a straight list, no back-arrow. Fast races ahead and falls off the "
    "end (its next is null), so the loop stops and we return False.",
    pointers={"slow": 0, "fast": 0}, state=[["slow", 1], ["fast", 1]])

slow = 0
fast = 0
while fast + 1 < len(vals2):
    slow += 1
    fast += 2
    fast_shown = fast if fast < len(vals2) else None
    add(act=3, code="fast", line=4, edges=E2,
        note=f"slow -> {vals2[slow]}, fast -> "
             f"{vals2[fast] if fast < len(vals2) else 'null'}.",
        pointers={"slow": slow, "fast": fast_shown},
        marks={str(slow): "active"},
        state=[["slow", vals2[slow]],
               ["fast", vals2[fast] if fast < len(vals2) else "null"]])

add(act=3, code="fast", line=7, edges=E2,
    note="fast fell off the end without ever meeting slow. No cycle — return False.",
    pointers={"slow": slow}, marks={str(slow): "dim"},
    state=[["result", "no cycle"]],
    banner="No back-arrow: return False")

trace = {
    "player": "linkedlist",
    "title": "Linked List Cycle - Floyd's fast/slow needs no memory",
    "acts": ["Brute: remember every node", "The waste", "Floyd's fast/slow",
             "Edge: no cycle"],
    "code": {"seen": CODE_SEEN, "fast": CODE_FAST},
    "legend": [["good", "collision / repeat"], ["active", "current node"],
               ["dim", "already stored / passed"]],
    "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
