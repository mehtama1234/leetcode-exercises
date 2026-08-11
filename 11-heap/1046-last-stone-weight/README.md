# 1046. Last Stone Weight

**Pattern:** Max-heap (repeatedly pull the two largest)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/last-stone-weight/

## The problem in plain words

You have a pile of stones with weights. Each round you take the two *heaviest*
stones and smash them together:

- If they weigh the same, both are destroyed.
- If they differ, the lighter one is destroyed and the heavier is replaced by a
  new stone whose weight is the difference.

Repeat until one stone or none remains. Return the last stone's weight, or `0` if
the pile is empty.

## Why this matters

The deeper operation is a *priority-driven reduction*: repeatedly pull the highest
(or lowest) priority items out of a changing collection, do something with them,
and feed a result back in — where each step changes what the next "highest" is.
The set is not static; it shrinks and gains new members as you go, so you can't
pre-sort once and walk the list.

This shape is everywhere schedulers and simulators live. A CPU or task scheduler
repeatedly runs the highest-priority job, which may spawn new jobs at various
priorities. Huffman coding builds a compression tree by repeatedly merging the two
*least* frequent symbols and reinserting the merged node. Event-driven simulations
pull the next-soonest event, which schedules future events. Merging k sorted
streams keeps pulling the current smallest head and pulls in its successor.

What the good solution buys is avoiding a full re-sort on every step. Because only
the top one or two items matter each round, a heap makes "give me the largest and
remove it" cost `O(log n)` instead of re-sorting at `O(n log n)`, turning an
`O(n^2 log n)` loop into `O(n log n)`.

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

This is correct and easy to read. But it sorts the *entire* pile every round just
to look at the top two.

## Find the waste

A round touches only two stones — the two heaviest — and maybe pushes one back.
Everything else in the pile stays exactly where it was. Re-establishing full
sorted order over all of it, every single round, is work we immediately throw
away. With up to `O(n)` rounds and an `O(n log n)` sort each, that's `O(n^2 log n)`.

The requirement is much narrower:

> Give me the two largest quickly, remove them, and let me push a new value in —
> without re-sorting the rest.

## The insight

That is exactly a **max-heap**: the largest element is always on top and comes off
in `O(log n)`; inserting a new value is also `O(log n)`. So each round is just two
pops and at most one push.

```
build a max-heap of the weights
while more than one stone:
    y = pop  (heaviest)
    x = pop  (second heaviest)
    if y != x: push (y - x)
return heap top, or 0 if empty
```

Python's `heapq` is a **min**-heap only, so we store **negated** weights. The
smallest negation corresponds to the largest real weight, so popping the min gives
us the heaviest stone; we negate again on the way out (and negate the leftover on
the way back in).

## Complexity

- **Time:** `O(n log n)` — building the heap is `O(n)`; then up to `O(n)` rounds,
  each doing a constant number of `O(log n)` pushes/pops.
- **Space:** `O(n)` — the heap holds the stones (in place if you negate into a new
  list, or you can heapify a copy).

Against the re-sort version's `O(n^2 log n)`, keeping the pile as a heap replaces
"re-order everything each round" with "touch only the top."

## Pitfalls

- **Min-heap in a min-heap language.** `heapq` gives the *smallest*; to get the
  heaviest, negate on push and negate again on pop. Forgetting a negation smashes
  the two *lightest* stones instead.
- **The equal case.** When `y == x`, both vanish — push *nothing*. Pushing `0`
  back is a bug: LeetCode stones have weight ≥ 1, and a phantom `0` can change the
  count and even the answer.
- **Empty result.** If every stone is destroyed, return `0`, not a crash on an
  empty heap. Guard the final read.
- **Loop condition.** Stop when `len <= 1`; peeling two off requires at least two
  present, and the survivor (if any) is the answer.

## Transfer

The move is: **when a process repeatedly consumes the extreme item(s) of a
changing set and may feed new items back, keep the set in a heap instead of
re-sorting.** The same repeated-extract shape drives
[Kth Largest Element in a Stream / 703](../0703-kth-largest-element-in-a-stream/),
the greedy merge in
[Kth Largest Element in an Array / 215](../0215-kth-largest-element-in-an-array/),
and the classic Huffman-tree and k-way-merge algorithms. Whenever a loop keeps
re-sorting to find "the current biggest/smallest," reach for a heap.
