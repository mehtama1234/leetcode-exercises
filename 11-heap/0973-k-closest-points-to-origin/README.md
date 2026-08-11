# 973. K Closest Points to Origin

**Pattern:** Fixed-size max-heap (keep the k smallest by a score)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/k-closest-points-to-origin/

## The problem in plain words

You're given points on a flat plane and a number `k`. Return the `k` points
closest to the origin `(0, 0)`, measured by straight-line distance. The order of
your answer doesn't matter, and the k closest are guaranteed to be unique.

```diagram
   points, distance to origin measured by x*x + y*y:

     (3,3)  -> 18
     (5,-1) -> 26
     (-2,4) -> 20

   k = 2 nearest -> the two smallest scores -> (3,3) and (-2,4)
```

## Why this matters

The real operation is *partial selection*: pick the k best items by some score
without producing a full ranking of everything. Sorting answers a question you
didn't ask ("what's the exact order of all n?") when you only need a smaller one
("which k are on top?").

This is the engine behind nearest-neighbor and top-k retrieval. Search and
recommendation systems score a huge candidate set and return only the k best
matches; a "find the nearest 5 stores / drivers" feature ranks by distance and
keeps a handful; vector search keeps the k closest embeddings to a query. In every
case the far-away items are computed against but never returned.

What you buy is time and bounded memory when `k` is small next to `n`. Sorting
everything is about `n log n`; a heap capped at `k` is about `n log k` and holds
only `k` items — the difference between paying to order a million far points and
paying only to track the few near ones.

## Start from the obvious

"the k closest" sounds like "sort, take the front," so the honest first move is
exactly that:

```
sort points by distance to origin
return the first k
```

Correct and short. One refinement: compare **squared** distance `x*x + y*y`
instead of `sqrt(x*x + y*y)`. Squaring keeps the same order, avoids floating-point
error, and stays in exact integers.

## Find the waste

Sorting orders *all* `n` points from nearest to farthest. But we return only the
first `k` — the entire ordering among the far points is computed and then thrown
straight in the bin. When `k` is much smaller than `n`, that's almost all of the
work wasted.

```diagram
   sorted by distance (k = 2):

   [ (3,3)  (-2,4) ] (1,3) (5,-1) (7,7) (-6,-6) ...
     ^^^^^^^^^^^^^^   ^^^^^^^^^^^^^^^^^^^^^^^^^^
     kept             fully ordered, then discarded
```

So the real requirement is narrower:

> Keep the `k` nearest points; ignore the exact arrangement of the rest.

## The insight

To hold the k nearest, watch the **farthest of the ones you're currently
keeping**. When a new point is nearer than that farthest keeper, swap it in;
otherwise ignore it. "Farthest of the current keepers" is the top of a **max-heap**
(biggest on top) of size `k`.

```diagram
   k = 2. max-heap keyed by distance, FARTHEST on top.
   points arrive: (3,3)=18, (5,-1)=26, (-2,4)=20

   push (3,3):   heap { 18 }                 top = 18
   push (5,-1):  heap { 26, 18 }             top = 26
                 size 2 = k, keep both
   push (-2,4):  heap { 26, 20, 18 } size 3 > 2
                 pop farthest (26 = (5,-1))  -> it can't be in the 2 nearest
                 heap { 20, 18 } = (-2,4),(3,3)   <- answer
```

The heap never grows past `k`. A near point bumps out the current farthest; a far
point becomes the new max and is popped right back. Python's `heapq` is a
**min**-heap, so store **negated** squared distance: the smallest negation is the
largest real distance, putting the current farthest keeper on top.

## Complexity

- **Time:** about `n log k` — one pass over `n` points, each doing a `log k` push
  and maybe a `log k` pop on a heap of size at most k.
- **Space:** `k` — the heap holds at most k points.

When `k` is close to `n` this is no better than sorting; the heap wins precisely
when you want a small slice of a large set.

## Pitfalls

- **Using real `sqrt`.** Unnecessary and it invites floating-point ties/errors.
  Rank by `x*x + y*y` and keep everything integer.
- **Wrong heap direction.** To keep the k *smallest* distances, you need a **max**
  heap (evict the largest). A min-heap of size k would evict the nearest points —
  exactly backwards. Hence the negation with `heapq`.
- **Tie-breaking on the heap.** If two negated distances are equal, Python next
  compares the following tuple field. A raw `list` compares fine, but if your
  point type isn't orderable, add a unique counter as a middle field to avoid a
  `TypeError`.
- **Off-by-one on k.** Cap when the size *exceeds* k (pop only after it hits
  k+1), so you end with exactly k.
- **Quickselect alternative.** Partitioning around the kth distance gives the k
  closest in about `n` steps on average and doesn't keep them ordered — better
  when you need the k best *once* and `k` is large; the heap is better for
  streaming or when you also want them roughly ranked.

## Transfer

The move is: **to pick the k best by a score, keep a size-k heap oriented so its
top is the *worst* of your current keepers, and evict on each insert.** The exact
same structure solves
[Kth Largest Element in a Stream / 703](../0703-kth-largest-element-in-a-stream/)
and [Kth Largest Element in an Array / 215](../0215-kth-largest-element-in-an-array/)
(where Quickselect is the linear-time cousin), and it generalizes to any "top-k by
weight" query. Whenever a brute force sorts everything just to read a small slice,
reach for a capped heap or Quickselect.
