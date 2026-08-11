# 21. Merge Two Sorted Lists

**Pattern:** Two-pointer merge with a dummy head
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/merge-two-sorted-lists/

## The problem in plain words

You have two linked lists, each already sorted from small to large. Weave them
into one sorted list and return its head. Reuse the nodes you already have — don't
build a fresh list out of copied numbers.

```diagram
   a:  1 -> 2 -> 4
   b:  1 -> 3 -> 4

   merged:  1 -> 1 -> 2 -> 3 -> 4 -> 4
```

## Why this matters

The word "sorted" hands you a gift. The smallest number you haven't used yet is
always sitting at the front of one of the two lists — never buried in the middle.
So you never search. You compare two heads, take the smaller, and step that list
forward. That is the whole operation.

This *merge step* is the workhorse of external merge sort — the way databases and
tools like Unix `sort` handle data bigger than memory: split into sorted chunks,
then fold the chunks back together. It is how `git merge` walks two sorted commit
histories, how a search engine combines two sorted lists of matching documents,
and how time-series systems fold two ordered event streams into one timeline.
Anywhere data is kept sorted and two ordered feeds need to become one, this is the
core.

What you are buying is one pass, no re-sorting, and no second copy — you relink the
nodes you already have, so memory stays flat. You never pay to sort data that
arrived in order. That "cheap because both sides are already sorted" property is
why merge-based designs scale.

## Start from the obvious

Repeatedly take the smaller of the two front nodes, attach it, and advance that
list.

```diagram
   a: [1] 2  4     b: [1] 3  4     take smaller head (tie -> take a)
   a:  1 [2] 4     b: [1] 3  4  -> took a's 1
   a:  1 [2] 4     b:  1 [3] 4  -> took b's 1
   ...
   result so far:  1 -> 1 -> 2 -> ...
```

There is no cleverer idea to find here — the difficulty is doing the pointer
bookkeeping cleanly, without special cases.

## The insight

Two small tricks make the bookkeeping disappear.

**A dummy head.** Start the result with one throwaway node. Now attaching the next
node is always the same two moves — `tail.next = chosen; tail = tail.next` — with
no special case for the very first node. At the end you return `dummy.next`, the
real head.

**Splice the leftover in one move.** When one list runs out, the other is still
sorted and still linked together. So `tail.next = whichever_remains` hooks up all
of it at once — no per-node loop.

```diagram
   dummy -> (nothing yet)      a: 1 2 4     b: 1 3 4
   tail=dummy

   1<=1:  dummy -> 1(a)                 tail moves ->  a: 2 4
   1<=2:  dummy -> 1 -> 1(b)            tail moves ->  b: 3 4
   2<=3:  dummy -> 1 -> 1 -> 2(a)       tail moves ->  a: 4
   3<=4:  dummy -> ... -> 3(b)          tail moves ->  b: 4
   4<=4:  dummy -> ... -> 4(a)          tail moves ->  a: empty

   a empty -> splice all of b's rest at once:
   dummy -> 1 -> 1 -> 2 -> 3 -> 4 -> [4]   return dummy.next
```

## Complexity

- **Time: about n + m steps.** Every node from both lists is visited once.
- **Extra memory: fixed.** No new nodes; only pointers move. The dummy is one
  constant node.

## Pitfalls

- Compare with `<=`, not `<`. Both give a correct sorted result, but `<=` keeps
  the merge *stable* (equal values keep their original order) — which matters when
  this is a subroutine inside a sort.
- Forgetting the final splice cuts the answer short the instant one list empties.
- Either input can be empty, or both. The dummy plus the final splice handle those
  with no extra branches.

## Transfer

This merge is the "combine" step of merge sort — it's exactly what Sort List / 148
calls, and it's the piece you call over and over (in balanced pairs) to solve
[merge k sorted lists / 23](../0023-merge-k-sorted-lists/). The dummy-head trick
comes back in almost every list-building problem, like
[remove nth node / 19](../0019-remove-nth-node-from-end-of-list/) and Add Two
Numbers / 2.
