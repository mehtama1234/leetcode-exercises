# 142. Linked List Cycle II

**Pattern:** Fast/slow pointers (Floyd's cycle detection, two phases)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/linked-list-cycle-ii/

## The problem in plain words

Same list-with-a-loop setup as [141](../0141-linked-list-cycle/), but now don't
just answer "is there a cycle?" — return the *node where the loop starts* (the
first node that gets revisited). No cycle → return `None`.

## Start from the obvious

The cycle's start is the first node you'd encounter twice. So remember each node
as you go; the first one already in your memory is the entrance:

```
seen = set()
node = head
while node:
    if node in seen: return node   # first repeat = loop entrance
    seen.add(node)
    node = node.next
return None
```

`O(n)` time and `O(n)` space. Correct and easy to trust.

## Find the waste

The set exists only to recognise the entrance. Floyd's algorithm already detects
*that* a cycle exists in `O(1)` space (from problem 141) — the question is
whether the meeting point can also reveal *where* the cycle begins, without any
memory.

## The insight

It can, and it falls out of a little distance arithmetic. Let:

- `L` = distance from head to the cycle start,
- `C` = length of the cycle,
- when slow and fast first meet, slow has walked `L + k` steps into the loop.

Fast moved twice as far, so `2(L + k) = L + k + (some whole number of laps)`.
Simplifying, `L` is congruent to "the distance from the meeting point back
around to the start". In plain terms:

> The distance from **head** to the cycle start equals the distance from the
> **meeting point** to the cycle start.

So do two phases:

```
# Phase 1: find a meeting point inside the loop (or return None).
slow = fast = head
while fast and fast.next:
    slow = slow.next; fast = fast.next.next
    if slow is fast: break
else:
    return None            # fast ran off -> no cycle

# Phase 2: reset one pointer to head, step both by ONE.
ptr = head
while ptr is not slow:
    ptr = ptr.next; slow = slow.next
return ptr                 # they meet at the cycle entrance
```

Both pointers now move one step at a time and are guaranteed to collide exactly
at the entrance.

## Complexity

- **Time:** `O(n)` — phase 1 meets within a lap, phase 2 walks at most `L + C`.
- **Space:** `O(1)` — three pointers, no memory of visited nodes.

## Pitfalls

- Phase 2 pointers each move **one** step. Reusing the 2× speed here breaks the
  proof and misses the entrance.
- Handle "no cycle" first: if fast reaches `None`, return `None` before starting
  phase 2.
- Compare by identity (`is`), never by `.val`.
- A self-loop (`[1]`, pos 0) must return that single node — the code handles it
  because head *is* the meeting point.

## Transfer

The two-phase idea — "detect with fast/slow, then re-walk from the start to
locate the entrance" — is the exact structure of Find the Duplicate Number / 287
(treat array values as `next` pointers). The core detection reuses
[141](../0141-linked-list-cycle/); this problem is what you build on top of it.
