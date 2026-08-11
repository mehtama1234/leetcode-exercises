# 1046. Last Stone Weight

**Pattern:** Max-heap (repeatedly pull the two largest from a changing pile)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/last-stone-weight/

## The problem in plain words

You have a pile of stones with weights. Each round you take the two *heaviest*
stones and smash them together:

- Equal weight? Both are destroyed.
- Different? The lighter one is destroyed and the heavier is replaced by a new
  stone whose weight is the difference.

Repeat until one stone or none remains. Return the last stone's weight, or `0` if
the pile is empty.

```diagram
   [2, 7, 4, 1, 8, 1]

   smash 8,7 -> diff 1 back:   [2, 4, 1, 1, 1]
   smash 4,2 -> diff 2 back:   [2, 1, 1, 1]
   smash 2,1 -> diff 1 back:   [1, 1, 1]
   smash 1,1 -> equal, gone:   [1]
   one stone left -> answer 1
```

## Why this matters

The real operation is a *priority-driven reduction*: repeatedly pull the
highest-priority items out of a changing collection, do something with them, and
feed a result back in — where each step changes what the next "highest" is. The
set is not static; it shrinks and gains new members as you go, so you can't sort
once and walk the list.

This shape is everywhere schedulers and simulators live. A task scheduler
repeatedly runs the highest-priority job, which may spawn new jobs. Huffman coding
builds a compression tree by repeatedly merging the two *least* frequent symbols
and reinserting the merged one. Event simulations pull the next-soonest event,
which schedules future events.

What you buy is avoiding a full re-sort on every step. Because only the top one or
two items matter each round, a heap makes "give me the largest and remove it" cost
about `log n` instead of re-sorting the whole pile.

## Start from the obvious

The rules say "take the two heaviest," and heaviest is defined by sorted order, so
the honest first move is to sort each round and grab the last two:

```
while more than one stone:
    sort the pile
    y = pop the heaviest
    x = pop the second heaviest
    if y != x: push (y - x) back
return the last stone (or 0)
```

Correct and easy to read. But it sorts the *entire* pile every round just to look
at the top two.

## Find the waste

A round touches only two stones — the two heaviest — and maybe pushes one back.
Everything else in the pile stays exactly where it was. Re-sorting all of it every
single round is work you immediately throw away. With up to `n` rounds and a full
sort each round, that's about `n · n log n`.

```diagram
   pile: 1 1 2 4 7 8       one round needs only:  8  and  7
                                                   ^^     ^^
                                                   top two
   sorting also orders  1 1 2 4  again... untouched, re-sorted for nothing
```

The requirement is much narrower:

> Give me the two largest quickly, remove them, and let me push a new value in —
> without re-sorting the rest.

## The insight

That is a **max-heap** (a tree where every parent is larger than its children, so
the biggest sits on top): the largest is always on top and comes off in about
`log n`; inserting a new value is also about `log n`. So each round is two pops
and at most one push.

```diagram
   max-heap of [2,7,4,1,8,1], biggest on top:

              8
            /   \
           7     4
          / \   /
         1   2 1

   pop 8, pop 7 -> diff 1 -> push 1:

              4
            /   \
           2     1
          / \
         1   1

   pop 4, pop 2 -> diff 2 -> push 2  -> ... -> down to one stone
```

Python's `heapq` is a **min**-heap only, so store **negated** weights: the
smallest negation is the largest real weight, so popping the min gives the
heaviest stone. Negate again on the way out, and negate the leftover on the way
back in.

## Complexity

- **Time:** about `n log n` — building the heap is about `n`; then up to `n`
  rounds, each doing a constant number of `log n` pushes/pops.
- **Space:** `n` — the heap holds the stones.

Against the re-sort version's `n · n log n`, keeping the pile as a heap replaces
"re-order everything each round" with "touch only the top."

## Pitfalls

- **Min-heap in a min-heap language.** `heapq` gives the *smallest*; to get the
  heaviest, negate on push and negate again on pop. Forgetting a negation smashes
  the two *lightest* stones instead.
- **The equal case.** When `y == x`, both vanish — push *nothing*. Pushing `0`
  back is a bug: stones have weight at least 1, and a phantom `0` can change the
  count and even the answer.
- **Empty result.** If every stone is destroyed, return `0`, not a crash on an
  empty heap. Guard the final read.
- **Loop condition.** Stop when one or zero stones remain; peeling two off needs
  at least two present, and the survivor (if any) is the answer.

## Transfer

The move is: **when a process repeatedly consumes the extreme item(s) of a
changing set and may feed new items back, keep the set in a heap instead of
re-sorting.** The same repeated-extract shape drives
[Kth Largest Element in a Stream / 703](../0703-kth-largest-element-in-a-stream/),
the greedy simulation in
[Task Scheduler / 621](../0621-task-scheduler/), and the classic Huffman-tree and
k-way-merge algorithms. Whenever a loop keeps re-sorting to find "the current
biggest/smallest," reach for a heap.
