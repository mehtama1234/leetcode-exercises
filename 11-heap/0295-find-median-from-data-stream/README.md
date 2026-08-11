# 295. Find Median from Data Stream

**Pattern:** Two heaps (keep the middle reachable, not the whole order)
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/find-median-from-data-stream/

## The problem in plain words

Numbers arrive one at a time, forever. At any moment someone can ask "what's the
median of everything so far?" The median is the middle value once the numbers are
sorted — and if the count is even, it's the average of the two middle values.

So you need two operations, both fast, both callable any number of times:
`addNum(x)` to feed in a number, and `findMedian()` to answer.

```diagram
   sorted so far:  1  2  4  7  9
                         ^ middle -> median = 4

   sorted so far:  1  2  4  7        (even count)
                      ^  ^ two middles -> median = (2+4)/2 = 3
```

## Why this matters

The real problem is keeping a *running middle value* over an endless stream
without ever holding the whole thing in sorted form. The move that makes it work:
keep just the boundary reachable — split the data at the point you care about and
store each side so its edge is always on top.

This is what streaming systems need. Monitoring tools report running medians and
percentiles (p50/p95/p99) of latency as requests pour in, and can't re-sort
millions of samples per second. Load balancers watch a moving-median signal to
smooth out spikes; finance systems track rolling medians of prices.

What you buy is speed under a single-pass constraint: the stream never stops and
you can't rewind it, so each insert must be cheap. The two-heap trick drops
per-add cost from about `n` (re-sorting) to about `log n`, and answers in one step
— keeping only the middle ordered instead of everything.

## Start from the obvious

The median is defined by sorted order, so the honest first move is to keep the
numbers sorted:

```
addNum(x):     insert x into a sorted list   # find spot, then shift the tail
findMedian():  return the middle element(s) by index
```

`findMedian` is now one step. The trouble is `addNum`: finding *where* x goes is a
fast binary search, but actually making room shifts every element after it. That's
about `n` per insert, so a stream of `n` numbers costs about `n·n` overall.

## Find the waste

To answer `findMedian` we only ever touch the one or two values sitting at the
**center**. Everything to the left of the middle and everything to the right is
just... there. Keeping the entire stream in perfect sorted order is far more work
than the question needs.

```diagram
   sorted:  1  2  4 | 7  9        we only ever read around the cut
            left half  right half
                    ^ ^
                    the median lives here; the rest is dead weight
```

So the real requirement is narrower:

> Keep the value(s) **at the middle** reachable — nothing more.

## The insight

Split the numbers into two halves and store each half in a heap so its boundary
value is instantly available:

- **`low`** — the smaller half, stored as a **max-heap** (biggest on top) so its
  *largest* value (the top of the lower half) is on top.
- **`high`** — the larger half, stored as a **min-heap** (smallest on top) so its
  *smallest* value (the bottom of the upper half) is on top.

Picture the sorted stream cut down the middle: `low`'s max and `high`'s min are
the two numbers straddling that cut — the ones the median is made of.

```diagram
   stream 1,2,3,4,5 split at the middle:

        low (max-heap)        high (min-heap)
        biggest on top        smallest on top

              3                     4
             / \                     \
            1   2                     5

   low.max = 3, high.min = 4
   odd total (5 numbers) -> low holds the extra -> median = low.max = 3
```

Keep two invariants (rules held true after every add):

1. **Everything in `low` <= everything in `high`.** The cut sits at the median.
2. **Sizes differ by at most 1**, and when they differ `low` holds the extra one.

Then answering is one step:

```
if low is bigger:  median = low.max                # odd count -> the true middle
else:              median = (low.max + high.min)/2  # even count -> average the two
```

Adding is where the care goes. A neat trick keeps invariant 1 automatic — push the
new number onto `low`, immediately move `low`'s max over to `high`, then if `high`
grew too big hand its min back:

```diagram
   addNum(x):
     1. push x onto low
     2. move low.max  ->  high     (forces low <= high)
     3. if high larger than low:
           move high.min -> low    (fix the sizes)

   trace, adding 1 then 2:
     add 1: low={1}, move max 1 -> high={1}, high bigger -> move back low={1} high={}
            -> low={1} high={}          median = 1
     add 2: low={1,2}, move max 2 -> high={2}, sizes 1/1 ok
            -> low={1} high={2}          median = (1+2)/2 = 1.5
```

The middle round-trip guarantees the value ending up in `high` is at least as big
as everything left in `low`, so the halves never overlap. (Python's `heapq` is
min-only, so `low` stores **negated** numbers — the smallest negation is the
largest real value.)

## Complexity

- **`addNum`:** about `log n` — a constant number of heap pushes/pops, each about
  `log n`.
- **`findMedian`:** one step — read the one or two heap tops.
- **Space:** `n` — every number is held in one of the two heaps.

Compared to the sorted list's `n` insert, we traded "keep everything ordered" for
"keep only the boundary ordered", and the per-add cost drops from about `n` to
about `log n`.

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

The move is: **when you only need the extreme(s) of a set, hold it in a heap; and
when you need a value at a *moving boundary*, hold each side in its own heap so the
boundary is always at a top.** This "balanced two-heap" idea shows up in
[Sliding Window Median / 480](https://leetcode.com/problems/sliding-window-median/)
and [IPO / 502](https://leetcode.com/problems/ipo/), and the single-heap version
powers [Kth Largest Element in a Stream / 703](../0703-kth-largest-element-in-a-stream/)
and [Last Stone Weight / 1046](../1046-last-stone-weight/). Whenever a brute force
keeps re-sorting or re-scanning for "the top / the middle", reach for a heap first.
