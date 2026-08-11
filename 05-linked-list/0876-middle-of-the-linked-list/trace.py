"""Rich full-arc trace for Middle of the Linked List (linked-list renderer).
Arc: two-pass count (walk twice, waste visible) -> fast/slow one pass -> even edge.
Mirrors middle_two_pass and middle in solution.py. Writes trace.json.
"""
import json
import os

frames = []

CODE_SLOW = [
    "n = 0",
    "node = head",
    "while node:",
    "    n += 1",
    "    node = node.next",
    "node = head",
    "for _ in range(n // 2):",
    "    node = node.next",
    "return node",
]

CODE_FAST = [
    "slow = head",
    "fast = head",
    "while fast and fast.next:",
    "    slow = slow.next",
    "    fast = fast.next.next",
    "return slow",
]


def add(**f):
    frames.append(f)


def fwd_edges(vals):
    return [[i, i + 1 if i + 1 < len(vals) else None] for i in range(len(vals))]


# ============ Act 0: brute force — count, then walk again ============
vals = [1, 2, 3, 4, 5]
E = fwd_edges(vals)
add(act=0, vals=vals, edges=E, code="slow", line=0,
    intro="watch the same nodes get walked a second time — that repeat is the waste.",
    invariant="you cannot know the middle index until you know the length.",
    note="The literal reading: the middle is at index n // 2, but we do not know n "
    "yet. So pass one just counts.",
    pointers={"node": 0}, state=[["n", 0], ["walks", 0]])

# pass 1: count
walks = 0
for i in range(len(vals)):
    walks += 1
    add(act=0, code="slow", line=3, edges=E,
        note=f"Counting node {vals[i]}. n is now {i + 1}.",
        pointers={"node": i}, marks={str(i): "dim"},
        state=[["n", i + 1], ["walks", walks]])

add(act=0, code="slow", line=5, edges=E,
    note="First pass done: length is 5. Now go back to the head and walk again.",
    pointers={"node": 0}, marks={str(j): "dim" for j in range(len(vals))},
    state=[["n", 5], ["walks", walks]])

# pass 2: walk n//2
mid = len(vals) // 2
for step in range(mid):
    walks += 1
    add(act=0, code="slow", line=7, edges=E,
        note=f"Second walk, step {step + 1} of {mid}. Re-touching node {vals[step + 1]}.",
        pointers={"node": step + 1}, marks={str(step + 1): "bad"},
        state=[["target idx", mid], ["walks", walks]])

add(act=0, code="slow", line=8, edges=E,
    note=f"Landed on index {mid}: the middle is {vals[mid]}. But we walked {walks} node-steps "
    f"for a {len(vals)}-node list — most nodes twice.",
    pointers={"node": mid}, marks={str(mid): "good"},
    state=[["middle", vals[mid]], ["walks", walks]],
    banner="Two passes: 3 is the middle")

# ============ Act 1: name the waste ============
add(act=1, vals=vals, edges=E, code="slow", line=6,
    intro="the fast version never needs the length — one pointer measures it live.",
    invariant="fast is always twice as far along as slow.",
    note="The waste: pass one only existed to learn the length. If one pointer moved "
    "twice as fast, it would reach the end exactly when a slower one reached the middle "
    "— length learned for free.",
    pointers={"slow": 0, "fast": 0}, state=[["idea", "fast = 2x slow"]])

# ============ Act 2: fast/slow one pass ============
add(act=2, vals=vals, edges=E, code="fast", line=1,
    intro="slow moves 1, fast moves 2; when fast runs out, slow is halfway.",
    invariant="distance(head, slow) is always half distance(head, fast).",
    note="Both start at the head. Each turn slow takes one step, fast takes two.",
    pointers={"slow": 0, "fast": 0}, state=[["slow", vals[0]], ["fast", vals[0]]])

slow = 0
fast = 0
while fast + 1 < len(vals):  # mirror: fast and fast.next
    slow += 1
    fast += 2
    fast_shown = fast if fast < len(vals) else None
    add(act=2, code="fast", line=4, edges=E,
        note=f"slow -> {vals[slow]}, fast -> "
             f"{vals[fast] if fast < len(vals) else 'null'}.",
        pointers={"slow": slow, "fast": fast_shown},
        marks={str(slow): "active"},
        state=[["slow", vals[slow]],
               ["fast", vals[fast] if fast < len(vals) else "null"]])

add(act=2, code="fast", line=5, edges=E,
    note=f"fast ran off the end after one pass. slow sits on {vals[slow]} — the middle.",
    pointers={"slow": slow}, marks={str(slow): "good"},
    state=[["middle", vals[slow]], ["passes", 1]],
    banner="One pass: 3 is the middle")

# ============ Act 3: even length edge ============
vals2 = [1, 2, 3, 4, 5, 6]
E2 = fwd_edges(vals2)
add(act=3, vals=vals2, edges=E2, code="fast", line=0,
    intro="with an even count there are two middles — this returns the second.",
    invariant="fast lands exactly on null; slow lands on the second middle.",
    note="Edge case: an even-length list. There are two middle nodes (3 and 4); the "
    "problem wants the second one.",
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

add(act=3, code="fast", line=5, edges=E2,
    note=f"fast is null and slow rests on {vals2[slow]} — the second of the two middles, "
    f"exactly as asked.",
    pointers={"slow": slow}, marks={str(slow): "good"},
    state=[["middle", vals2[slow]]],
    banner="Even length: 4 is the (second) middle")

trace = {
    "player": "linkedlist",
    "title": "Middle of the Linked List - fast/slow finds it in one pass",
    "acts": ["Brute: count then re-walk", "The waste", "Fast/slow one pass",
             "Edge: even length"],
    "code": {"slow": CODE_SLOW, "fast": CODE_FAST},
    "legend": [["good", "the middle"], ["bad", "re-walked node"],
               ["dim", "counted node"], ["active", "slow is here"]],
    "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
