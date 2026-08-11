# 141. Linked List Cycle

**Pattern:** Fast/slow pointers (Floyd's cycle detection)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/linked-list-cycle/

## The problem in plain words

Walk a linked list. Does it ever loop back on itself — some node's `next`
pointing to an earlier node — so that walking forever never reaches `None`?
Return true/false.

## Why this matters

The real question is: does following a chain of "next" references terminate, or
does it loop forever? The fundamental operation is *cycle detection* in a
sequence you generate one step at a time — and Floyd's slow/fast pointer answers
it using O(1) memory instead of remembering every node you've visited.

This shows up wherever you follow references and a loop would be a bug or a hang.
Dependency resolvers (package managers, build systems, spreadsheet formula
engines) must detect circular dependencies before they recurse forever. Garbage
collectors and serializers walk object graphs that can point back at themselves.
Deadlock detection looks for cycles in a "who waits on whom" graph. Even pointer
chasing that follows corrupted or attacker-crafted `next` links needs a loop guard.

What you're solving for is catching the loop without a growing set of "seen"
nodes. On a huge or streaming structure — or inside a memory-constrained runtime
like a GC — you often can't afford O(n) bookkeeping, so the two-pointer trick that
uses constant space is the one that actually ships.

## Start from the obvious

A cycle means "I returned to a node I've already stood on". So remember every
node you've visited and check each new one against that memory:

```
seen = set()
node = head
while node:
    if node in seen: return True
    seen.add(node)
    node = node.next
return False
```

Correct, and `O(n)` time. But it spends `O(n)` memory just to answer a yes/no
question.

## Find the waste

The set is only there to notice "have I been here before?". But you don't
actually need to store the whole history to detect a loop — you just need two
things moving through the same nodes at different rates.

## The insight

Picture a circular running track. A fast runner (2 steps per turn) and a slow
runner (1 step) both on the track: the fast one *must* eventually catch up to
and land on the slow one — it gains one step of distance each turn and the track
wraps around. On a straight track (no cycle), the fast runner just reaches the
finish line (`None`) and there's no catch-up.

```
slow = fast = head
while fast and fast.next:
    slow = slow.next
    fast = fast.next.next
    if slow is fast: return True   # they met -> cycle
return False                       # fast ran off the end -> no cycle
```

Compare nodes by **identity** (`is`), not value — two different nodes can hold
the same value.

## Complexity

- **Time:** `O(n)` — with a cycle, fast catches slow within one lap; without
  one, fast reaches the end in `n/2` steps.
- **Space:** `O(1)` — two pointers, no bookkeeping.

## Pitfalls

- Guard both `fast` and `fast.next` before `fast.next.next`, or you'll
  dereference `None` at the end of an acyclic list.
- Check `slow is fast`, not `slow.val == fast.val` — value equality gives false
  positives on lists with repeated values.
- Check *after* moving both pointers. They start equal at `head`; checking
  before the first move reports a false cycle immediately.

## Transfer

Once you can detect the cycle, the same two pointers find *where* the loop
starts ([142](../0142-linked-list-cycle-ii/)), find the middle
([876](../0876-middle-of-the-linked-list/)), and detect cycles in a numeric
"jump" sequence like Happy Number / 202. Floyd's trick applies any time
"advancing" is deterministic and you're asking whether it repeats.
