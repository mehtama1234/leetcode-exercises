# 295. Find Median from Data Stream

**Pattern:** Two heaps (keep the middle reachable, not the whole order)
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/find-median-from-data-stream/

## The problem in plain words

Numbers arrive one at a time, forever. At any moment someone can ask "what's the
median of everything so far?" The median is the middle value once the numbers are
sorted — and if there's an even count, it's the average of the two middle values.

So you need two operations, both fast, and both can be called any number of times:
`addNum(x)` to feed in a number, and `findMedian()` to answer.

## Start from the obvious

The median is defined in terms of sorted order, so the honest first move is to
just keep the numbers sorted:

```
addNum(x):     insert x into a sorted list   # find spot, then shift the tail
findMedian():  return the middle element(s) by index
```

`findMedian` is now trivial and O(1). The trouble is `addNum`: finding *where* x
goes is a fast binary search, but actually making room shifts every element after
it. That's `O(n)` per insert, so a stream of `n` numbers costs `O(n^2)` overall.

That's correct — and staring at *what it does too much* points straight at the fix.

## Find the waste

To answer `findMedian` we only ever touch the one or two values sitting at the
**center**. Everything to the left of the middle and everything to the right is
just... there. Keeping the entire stream in perfect sorted order is far more work
than the question needs. We are paying `O(n)` per insert to maintain order we
never read.

So the real requirement is narrower:

> Keep the value(s) **at the middle** reachable — nothing more.

## The insight

Split the numbers into two halves and store each half in a heap so its boundary
value is instantly available:

- **`low`** — the smaller half, stored as a **max-heap** so its *largest* value
  (the top of the lower half) is at the top.
- **`high`** — the larger half, stored as a **min-heap** so its *smallest* value
  (the bottom of the upper half) is at the top.

Picture the sorted stream cut down the middle: `low`'s max and `high`'s min are
exactly the two numbers straddling that cut — the ones the median is made of.

Keep two invariants after every add:

1. **Everything in `low` <= everything in `high`.** The cut sits at the median.
2. **Sizes differ by at most 1**, and when they differ `low` holds the extra one.

Then answering is O(1):

```
if low is bigger:  median = low.max                # odd count -> the true middle
else:              median = (low.max + high.min)/2  # even count -> average the two
```

Adding is where the cleverness lives. A neat trick keeps invariant 1 automatic —
push the new number onto `low`, immediately move `low`'s max over to `high`, then
if `high` grew too big hand its min back:

```
addNum(x):
    push x onto low
    move low.max -> high        # forces "low <= high"
    if high larger than low:
        move high.min -> low    # fix the sizes
```

The middle round-trip guarantees the value ending up in `high` is at least as big
as everything left in `low`, so the two halves never overlap. (Python's `heapq`
is min-only, so `low` stores **negated** numbers — the smallest negation is the
largest real value.)

## Complexity

- **`addNum`:** `O(log n)` — a constant number of heap pushes/pops, each `O(log n)`.
- **`findMedian`:** `O(1)` — just read the one or two heap tops.
- **Space:** `O(n)` — every number is held in one of the two heaps.

Compared to the sorted list's `O(n)` insert, we traded "keep everything ordered"
for "keep only the boundary ordered", and the per-add cost drops from `O(n)` to
`O(log n)`.

## Pitfalls

- **Max-heap in a min-heap language.** `heapq` only does min-heaps; negate on the
  way in and negate again on the way out for `low`. Forgetting one negation flips
  the whole split.
- **Which heap holds the extra element.** Pick a rule (here: `low` >= `high` in
  size) and apply it *identically* in both `addNum`'s rebalance and `findMedian`,
  or the odd-count case reads the wrong heap.
- **Even-count division.** Return a float — `(a + b) / 2`, not integer `//` — or
  `[2, 3]` reports `2` instead of `2.5`.
- **Skipping the cross-over push in `addNum`.** Just pushing x onto whichever heap
  "looks right" by value can break invariant 1 on later inserts; routing every new
  number through `low -> high` is what keeps the two halves cleanly separated.

## Transfer

The move is: **when you only need the extreme(s) of a set, don't sort it — hold it
in a heap; and when you need a value at a *moving boundary*, hold each side in its
own heap so the boundary is always at a top.** This "balanced two-heap" idea shows
up in [Sliding Window Median / 480](https://leetcode.com/problems/sliding-window-median/)
and [IPO / 502](https://leetcode.com/problems/ipo/), and the plain single-heap
version powers [Kth Largest Element in a Stream / 703](https://leetcode.com/problems/kth-largest-element-in-a-stream/)
and [Last Stone Weight / 1046](https://leetcode.com/problems/last-stone-weight/).
Whenever a brute force keeps re-sorting or re-scanning for "the top / the middle",
reach for a heap first.
