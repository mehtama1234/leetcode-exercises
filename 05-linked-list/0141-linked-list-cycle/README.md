# 141. Linked List Cycle

**Pattern:** Fast/slow pointers (Floyd's cycle detection)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/linked-list-cycle/

## The problem in plain words

Walk a linked list by following `next`. Does it ever loop back — some node's `next`
pointing at an earlier node — so that walking forever never reaches `None`? Return
true or false.

```diagram
   no cycle:   1 -> 2 -> 3 -> 4 -> None

   cycle:      1 -> 2 -> 3 -> 4
                    ^         |
                    +---------+     (4's next points back to 2)
```

## Why this matters

The real question is whether following a chain of "next" references ever stops, or
loops forever. And the trick answers it while remembering almost nothing — instead
of a growing set of every node you've seen, you use two pointers moving at
different speeds and a fixed amount of memory.

This shows up wherever you follow references and a loop would be a bug or a hang.
Package managers, build systems, and spreadsheet formula engines must catch a
circular dependency before they recurse forever. Garbage collectors and
serializers walk object graphs that can point back at themselves. Deadlock
detection looks for a loop in a "who is waiting on whom" graph. Even chasing
pointers through corrupted or attacker-crafted `next` links needs a loop guard.

What you are solving for is catching the loop *without* a growing set of visited
nodes. On a huge or streaming structure — or inside a memory-tight runtime like a
garbage collector — you often can't afford bookkeeping that grows with the list, so
the two-pointer version that uses fixed memory is the one that ships.

## Start from the obvious

A cycle means "I came back to a node I already stood on." So remember every node
you visit and check each new one against that memory.

```diagram
   seen = {}         walk and record:
   at 1: seen? no -> add 1     seen = {1}
   at 2: seen? no -> add 2     seen = {1,2}
   at 3: seen? no -> add 3     seen = {1,2,3}
   at 4: seen? no -> add 4     seen = {1,2,3,4}
   at 2: seen? YES -> cycle!
```

Correct, and about n steps. But it spends memory that grows with the list just to
answer a yes/no question.

## Find the waste

The set is only there to notice "have I been here before?" You don't need the whole
history to detect a loop. You need two things moving through the same nodes at
different rates.

## The insight

Picture a circular running track. A fast runner (two steps per turn) and a slow
runner (one step) both start together. The fast one gains one step of lead each
turn, and the track wraps around, so the fast one *must* eventually land on the
slow one. On a straight track (no loop) the fast runner just reaches the finish
line (`None`) and never catches up.

```diagram
   list with a cycle:   1 -> 2 -> 3 -> 4 -> 5
                             ^              |
                             +--------------+   (5 -> 2)

   slow +1, fast +2 each turn:
   start:  slow=1   fast=1
   turn1:  slow=2   fast=3
   turn2:  slow=3   fast=5
   turn3:  slow=4   fast=3   (fast wrapped: 5->2->3)
   turn4:  slow=5   fast=5   <- slow is fast -> CYCLE
```

```diagram
   no cycle:   1 -> 2 -> 3 -> 4 -> None

   start:  slow=1   fast=1
   turn1:  slow=2   fast=3
   turn2:  slow=3   fast=None   (fast ran off the end)
           stop -> no cycle
```

Compare nodes by *identity* (`is`), not by value — two different nodes can hold the
same number.

## Complexity

- **Time: about n steps.** With a cycle, fast catches slow within one lap; without
  one, fast reaches the end in about n/2 turns.
- **Extra memory: fixed.** Two pointers, no visited set.

## Pitfalls

- Guard both `fast` and `fast.next` before `fast.next.next`, or you'll dereference
  `None` at the end of a list with no cycle.
- Check `slow is fast`, not `slow.val == fast.val` — value equality gives false
  positives on lists with repeated numbers.
- Check *after* moving both pointers. They start equal at `head`; checking before
  the first move reports a false cycle right away.

## Transfer

Once you can detect the cycle, the same two pointers can find *where* the loop
starts ([142](../0142-linked-list-cycle-ii/)), find the middle
([876](../0876-middle-of-the-linked-list/)), and detect loops in a numeric "jump"
sequence like Happy Number / 202. The fast/slow trick applies any time "advancing"
is deterministic and you're asking whether it ever repeats.
