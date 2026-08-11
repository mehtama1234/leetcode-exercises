"""Rich full-arc trace for Linked List Cycle II (linked-list renderer).
Arc: seen-set finds entrance (O(n) memory) -> Floyd's two phases -> no-cycle edge.
Mirrors detect_cycle_seen and detect_cycle in solution.py. The cycle is a
backward arc (to_idx < from_idx) which the renderer draws below the row.
Writes trace.json.
"""
import json
import os

frames = []

CODE_SEEN = [
    "seen = set(); node = head",
    "while node:",
    "    if id(node) in seen:",
    "        return node",
    "    seen.add(id(node))",
    "    node = node.next",
    "return None",
]

CODE_FAST = [
    "slow = fast = head",
    "while fast and fast.next:",
    "    slow = slow.next",
    "    fast = fast.next.next",
    "    if slow is fast:",
    "        ptr = head",
    "        while ptr is not slow:",
    "            ptr = ptr.next; slow = slow.next",
    "        return ptr",
    "return None",
]


def add(**f):
    frames.append(f)


# 3 -> 2 -> 0 -> -4, tail loops back to index 1 (value 2). Cycle start = index 1.
vals = [3, 2, 0, -4]
NEXT = {0: 1, 1: 2, 2: 3, 3: 1}
START = 1


def edges():
    return [[i, NEXT[i]] for i in range(len(vals))]


# ============ Act 0: brute — first repeat is the entrance ============
add(act=0, vals=vals, edges=edges(), code="seen", line=0,
    intro="the first node we meet twice is, by definition, where the loop rejoins.",
    invariant="a repeat can only happen at the cycle's entry point.",
    note="The honest idea: walk and remember every node; the first one already in memory "
    "is the cycle entrance. The arc below shows -4 looping back to 2.",
    pointers={"node": 0}, state=[["seen", 0]])

seen = set()
node = 0
for _ in range(8):
    if node in seen:
        add(act=0, code="seen", line=3, edges=edges(),
            note=f"Node {vals[node]} is already stored — this is where the loop begins. "
                 f"Return it.",
            pointers={"node": node}, marks={str(node): "good"},
            state=[["entrance", vals[node]], ["memory", len(seen)]],
            banner="Set method: cycle starts at 2 (used O(n) memory)")
        break
    add(act=0, code="seen", line=4, edges=edges(),
        note=f"First visit to {vals[node]}; store it and continue.",
        pointers={"node": node},
        marks={str(k): "dim" for k in seen} | {str(node): "active"},
        state=[["seen", len(seen) + 1]])
    seen.add(node)
    node = NEXT[node]

# ============ Act 1: name the waste ============
add(act=1, vals=vals, edges=edges(), code="seen", line=0,
    intro="a two-step distance argument finds the same entrance with no memory.",
    invariant="head-to-entrance distance equals meeting-to-entrance distance.",
    note="The waste is the set. Floyd's insight: after slow and fast collide inside the "
    "loop, the distance from the head to the entrance equals the distance from that "
    "meeting point to the entrance. So two lockstep walkers pin it exactly.",
    pointers={"node": 0}, state=[["extra memory", "O(n) -> O(1)"]])

# ============ Act 2: Floyd phase 1 (meet) ============
add(act=2, vals=vals, edges=edges(), code="fast", line=0,
    intro="phase 1: slow 1 step, fast 2 steps, until they collide somewhere in the loop.",
    invariant="if a cycle exists, the two pointers must meet inside it.",
    note="Phase 1 finds a meeting point (not yet the entrance). slow steps once, fast "
    "twice.",
    pointers={"slow": 0, "fast": 0}, state=[["slow", vals[0]], ["fast", vals[0]]])

slow = 0
fast = 0
for _ in range(10):
    slow = NEXT[slow]
    fast = NEXT[NEXT[fast]]
    met = slow == fast
    add(act=2, code="fast", line=4, edges=edges(),
        note=f"slow -> {vals[slow]}, fast -> {vals[fast]}." +
             (" They meet here." if met else ""),
        pointers={"slow": slow, "fast": fast},
        marks={str(slow): ("good" if met else "active")},
        state=[["slow", vals[slow]], ["fast", vals[fast]]])
    if met:
        break

meet = slow

# ============ Act 3: Floyd phase 2 (find entrance) ============
add(act=3, vals=vals, edges=edges(), code="fast", line=5,
    intro="phase 2: reset one pointer to the head; walk both one step until they meet.",
    invariant="they collide exactly at the cycle entrance.",
    note=f"They met at {vals[meet]}. Now reset ptr to the head and move ptr and slow one "
    f"step at a time — where they meet is the entrance.",
    pointers={"ptr": 0, "slow": meet},
    marks={str(meet): "active", "0": "active"},
    state=[["ptr", vals[0]], ["slow", vals[meet]]])

ptr = 0
sl = meet
while ptr != sl:
    ptr = NEXT[ptr]
    sl = NEXT[sl]
    same = ptr == sl
    add(act=3, code="fast", line=7, edges=edges(),
        note=f"ptr -> {vals[ptr]}, slow -> {vals[sl]}." +
             (" Same node — this is the entrance." if same else ""),
        pointers={"ptr": ptr, "slow": sl},
        marks={str(ptr): "good"} if same else {str(ptr): "active", str(sl): "active"},
        state=[["ptr", vals[ptr]], ["slow", vals[sl]]])

add(act=3, code="fast", line=8, edges=edges(),
    note=f"Both landed on {vals[ptr]}: the cycle begins here. No extra memory used.",
    pointers={"ptr": ptr}, marks={str(ptr): "good"},
    state=[["entrance", vals[ptr]]],
    banner="Floyd: cycle starts at 2 with O(1) memory")

# ============ Act 4: no-cycle edge ============
vals2 = [1, 2, 3]
E2 = [[0, 1], [1, 2], [2, None]]
add(act=4, vals=vals2, edges=E2, code="fast", line=1,
    intro="with no loop, fast reaches null and we never enter phase 2.",
    invariant="no collision means no cycle; return None.",
    note="Edge case: a straight list. fast walks off the end before it can meet slow, so "
    "the function returns None.",
    pointers={"slow": 0, "fast": 0}, state=[["slow", 1], ["fast", 1]])

add(act=4, code="fast", line=9, edges=E2,
    note="fast hit the end without meeting slow — there is no cycle. Return None.",
    pointers={"slow": 1}, marks={"2": "dim"},
    state=[["result", "no cycle"]],
    banner="No back-arrow: return None")

trace = {
    "player": "linkedlist",
    "title": "Linked List Cycle II - Floyd's two phases find the entrance",
    "acts": ["Brute: first repeat", "The waste", "Phase 1: meet",
             "Phase 2: find entrance", "Edge: no cycle"],
    "code": {"seen": CODE_SEEN, "fast": CODE_FAST},
    "legend": [["good", "entrance / collision"], ["active", "pointer here"],
               ["dim", "stored / passed"]],
    "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
