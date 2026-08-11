# 876. Middle of the Linked List

**Pattern:** Fast/slow pointers (two cursors at different speeds)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/middle-of-the-linked-list/

## The problem in plain words

You have a singly linked list. Return the node in the middle. If the list has an
even number of nodes there are two middles — return the second one.

```diagram
   odd:   1 -> 2 -> 3 -> 4 -> 5        middle = 3
                     ^
   even:  1 -> 2 -> 3 -> 4             two middles: 2 and 3
                     ^ return the second one -> 3
```

## Why this matters

You want a spot halfway along a chain, but you don't know how long the chain is,
and you can't cheaply measure it — a singly linked list only walks forward. So
"the middle" sounds like it needs the length first.

It doesn't, and the way out is a reusable idea: run two cursors at different
speeds. Move one twice as fast as the other. When the fast one reaches the end, it
has covered the whole list while the slow one has covered exactly half — so the
slow one is standing on the middle. The length falls out for free, in a single
pass.

That "two cursors, different rates" move is a primitive you'll reuse. It's how you
split a list in half for merge sort or the reorder problem, how streaming code
bisects a feed whose size isn't known ahead of time, and it's the same two-speed
idea behind cycle detection (problems 141 and 142), aimed at a different goal.

What you are buying is one pass and a fixed amount of memory: no counting the
length and walking back, no buffering nodes to index the middle. When the list is
huge or arrives as a stream you can read only once, "be at the middle by the time
fast reaches the end" is what makes it cheap.

## Start from the obvious

You can only find the middle *index* if you know the length. So count first, then
walk halfway.

```diagram
   pass 1 (count):   1 -> 2 -> 3 -> 4 -> 5   ->  n = 5
   pass 2 (walk):    step n/2 = 2 times from head
                     head=1 -> 2 -> 3
                                    ^ stop here, return 3
```

Correct, and it touches about n nodes — but notice it walks the list essentially
twice.

## Find the waste

The two passes exist only because we insisted on knowing `n` before moving. But
"the middle" has a cheaper meaning: it's the point you reach when you've gone
*half* as far as the end. If something could measure "half the distance to the
end" while walking, the separate counting pass would never be needed.

## The insight

Move two pointers at different speeds from the head. `slow` takes one step per
turn; `fast` takes two. By the time `fast` reaches the end, it has gone twice as
far — so `slow` sits at the halfway point.

```diagram
   1 -> 2 -> 3 -> 4 -> 5 -> None
   walk fast (2 steps) and slow (1 step) together:

   start:  slow=1        fast=1
   turn1:  slow=2        fast=3
   turn2:  slow=3        fast=5
   turn3:  fast.next is None -> stop
           slow=3  <- the middle
```

For an even length, the loop stops one step earlier and leaves `slow` on the
*second* of the two middles — exactly what the problem asks for.

```diagram
   1 -> 2 -> 3 -> 4 -> None

   start:  slow=1        fast=1
   turn1:  slow=2        fast=3
   turn2:  slow=3        fast=None    (fast.next.next walked off)
           fast is None -> stop
           slow=3   <- the SECOND of the two middles
```

The loop condition `while fast and fast.next` is what picks the correct middle for
even lengths.

## Complexity

- **Time: about n steps.** One pass; `fast` covers the list once.
- **Extra memory: fixed.** Two pointers, nothing allocated.

## Pitfalls

- The loop guard must be `while fast and fast.next`. Drop the `fast.next` check and
  `fast.next.next` crashes on even-length lists.
- Off-by-one: starting both pointers at `head` (not one at `head.next`) is what
  gives the *second* middle. To get the first middle instead, start `fast` one node
  ahead.
- Empty list: the loop never runs and `slow` stays `None`, which is correct.

## Transfer

Fast/slow pointers are the backbone of many list problems: cycle detection
([141](../0141-linked-list-cycle/), [142](../0142-linked-list-cycle-ii/)),
finding the nth-from-end node ([19](../0019-remove-nth-node-from-end-of-list/)),
and splitting a list in half for [reorder / 143](../0143-reorder-list/). Whenever
you need a position defined *relative to the end* without knowing the length up
front, reach for two pointers moving at different speeds.
