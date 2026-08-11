# 142. Linked List Cycle II

**Pattern:** Fast/slow pointers (Floyd's detection, then a second walk)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/linked-list-cycle-ii/

## The problem in plain words

Same list-with-a-loop setup as [141](../0141-linked-list-cycle/), but now don't
just answer "is there a cycle?" — return the *node where the loop starts* (the
first node that gets revisited). No cycle means return `None`.

```diagram
   1 -> 2 -> 3 -> 4 -> 5
             ^              |
             +--------------+   (5 -> 3)

   the loop starts at node 3  <- return this node
```

## Why this matters

This goes past "is there a loop?" to "*where* does the loop begin?" The detection
is the same fixed-memory fast/slow walk from 141; the new part is a little distance
arithmetic that pinpoints the exact entry node without remembering every node
you've seen.

Knowing the entry point matters when a cycle is something you have to *fix*, not
just flag. A build or dependency graph with a circular import needs to report the
specific edge that closes the loop so a human can cut it. Sequence generators —
pseudo-random streams, hashing chains, state machines — eventually repeat, and
finding where the repeat starts tells you the period. Debuggers and leak analyzers
tracing self-referential pointers want the offending node, not a yes/no.

What you are solving for is getting that precise location in one pass with fixed
memory — no set of every visited node — which is what keeps it usable on large
graphs and inside tight runtimes.

## Start from the obvious

The cycle's start is the first node you'd reach twice. So remember each node as you
go; the first one already in your memory is the entrance.

```diagram
   seen = {}
   at 1: add 1
   at 2: add 2
   at 3: add 3
   at 4: add 4
   at 5: add 5
   at 3: already seen -> 3 is the entrance
```

About n steps, but memory grows with the list.

## Find the waste

The set exists only to recognize the entrance. Floyd's walk already detects *that*
a cycle exists with fixed memory (problem 141). The question is whether the meeting
point can also reveal *where* the cycle begins, still without a visited set.

## The insight

It can, and it drops out of a little distance arithmetic. Name the distances:

```diagram
   head ...(L)... [S] ...(k)... [M] ...     S = cycle start
                   ^cycle start   ^meeting   M = where slow & fast met
                   |                     |
                   +----(C = cycle len)--+

   L = steps from head to the cycle start
   C = length of the loop
```

When slow and fast first meet, slow has walked `L + k` steps. Fast walked twice as
far, and the extra distance is some whole number of laps around the loop:
`2(L + k) = (L + k) + (whole laps)`. Cancel and it says `L` equals the distance
from the meeting point onward to the cycle start. In plain words:

> The distance from **head** to the cycle start is the same as the distance from
> the **meeting point** to the cycle start.

So walk both at the same one-step speed — one from the head, one from the meeting
point — and they collide exactly at the entrance.

```diagram
   Phase 1: fast/slow until they meet inside the loop (or fast hits None).

   Phase 2: put one pointer back at head. Step BOTH one at a time.

     ptr  = head        ->  1
     slow = meeting pt   ->  say they met at 5

     turn1: ptr=2   slow=3
     turn2: ptr=3   slow=3   <- ptr is slow -> node 3 = cycle start
```

## Complexity

- **Time: about n steps.** Phase 1 meets within a lap; phase 2 walks at most
  `L + C`.
- **Extra memory: fixed.** Three pointers, no set of visited nodes.

## Pitfalls

- In phase 2, each pointer moves **one** step. Reusing the 2x speed here breaks the
  math and misses the entrance.
- Handle "no cycle" first: if fast reaches `None`, return `None` before starting
  phase 2.
- Compare by identity (`is`), never by `.val`.
- A self-loop (`[1]` pointing at itself) must return that single node — the code
  handles it because head *is* the meeting point.

## Transfer

The two-phase shape — "detect with fast/slow, then re-walk from the start to locate
the entrance" — is exactly how you solve Find the Duplicate Number / 287 (treat
each array value as a `next` pointer). The detection half reuses
[141](../0141-linked-list-cycle/); this problem is what you build on top of it.
