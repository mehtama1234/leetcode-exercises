# 981. Time Based Key-Value Store

**Pattern:** Sorted history + binary search (floor query)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/time-based-key-value-store/

## The problem in plain words

Store values under a key, but every write is tagged with a timestamp, so one key
can have many versions over time. When someone reads with `get(key, t)`, hand back
the value that was set at the *latest* timestamp still at or before `t` — the value
that was "in effect" at time `t`. If nothing was set by then, return `""`. Writes
always arrive with increasing timestamps.

```diagram
   set("k","v1",10)  set("k","v2",20)  set("k","v3",30)

   get("k", 25) -> "v2"   (v2 set at 20 is the latest at-or-before 25)
   get("k", 20) -> "v2"   (exact hit)
   get("k",  9) -> ""     (nothing was set by time 9)
```

## Why this matters

The real operation is a **point-in-time, "as-of" read of versioned data**: given a
history of changes, answer "what did this look like at moment T?" The turn is
noticing the history is *already sorted by time*, which makes the query a binary
search for the floor of `t` — the last timestamp not past it.

This is the beating heart of many real systems. Multi-version concurrency control
in Postgres and MySQL keeps timestamped row versions so each transaction reads a
consistent snapshot. Time-series databases and monitoring stores answer "value as
of this time." Git, event-sourced systems, and config stores that let you read a
past revision all do this floor-by-time lookup.

What the good solution buys is speed by skipping a scan: because each key's versions
are sorted, a `get` costs about log-n steps instead of walking backward through
possibly millions of historical writes. You spend a little ordered storage to make
time-travel reads fast.

## Start from the obvious

Keep a list of `(timestamp, value)` per key. To answer `get(key, t)`, scan for the
entry with the largest timestamp that is at or before `t`.

```diagram
   history["k"] = [ (10,v1), (20,v2), (30,v3) ]   sorted by time

   get("k", 25): walk left to right, keep the last that qualifies
       (10,v1) ok -> best=v1
       (20,v2) ok -> best=v2
       (30,v3) too late -> stop
       ^ still touched most of the list to land on one entry
```

Correct, and thanks to the sorted order it can stop early — but in the worst case
(a large `t`) it still walks the entire history: a full pass per query.

## Find the waste

The scan visits every version even though the list is sorted. Any time you're
walking a *sorted* list to find a boundary — "largest value at or before `t`" —
you're leaving a binary search on the table. You don't need to look at each version;
you need to *land on the boundary* directly.

## The insight

Store two parallel arrays per key: the timestamps and the values, appended in order.
Since timestamps arrive strictly increasing, the timestamp array is sorted for free.

For `get(key, t)`, do a **floor query** with binary search — repeatedly halve the
range instead of walking it:

```diagram
   times = [ 10, 20, 30, 40, 50 ]     t = 35

   bisect_right finds the first timestamp strictly greater than 35:
       low                       high
       [ 10, 20, 30, 40, 50 ]
                     ^ mid=30, <=35 -> go right
       [ 40, 50 ]
         ^ mid=40, >35 -> go left
       lands at index 3 (the 40)
   answer is the entry just before -> index 2 -> the value set at time 30
```

- `bisect_right(times, t)` returns the first index whose timestamp is strictly
  greater than `t`.
- The entry just *before* that index (index `i - 1`) holds the largest timestamp at
  or before `t` — the answer.
- If that index is 0, every stored time is later than `t`, so return `""`.

## Complexity

- **set: one step.** Append to two lists.
- **get: about log-n steps.** Binary search over one key's `n` versions — each step
  halves the range.
- **Space: proportional to total writes.** Every version is kept (that's the point;
  you can read any past moment).

## Pitfalls

- Reaching for `bisect_left` when you want `bisect_right`. For "largest timestamp at
  or before `t`," use `bisect_right` then step back one; getting this wrong breaks
  exact-timestamp hits.
- Forgetting the "nothing set yet" case — index 0 means return `""`.
- Assuming timestamps are sorted when they might not be. Here the problem guarantees
  increasing timestamps; without that you'd need to insert in order (or sort), which
  changes the cost.
- Storing `(ts, value)` tuples and re-sorting on every read — needless given the
  ordering guarantee.

## Transfer

The "binary-search a sorted structure for a boundary" move is broad. See
[Search Insert Position / 35](https://leetcode.com/problems/search-insert-position/),
[Find First and Last Position / 34](https://leetcode.com/problems/find-first-and-last-position-of-element-in-sorted-array/),
and [Snapshot Array / 1146](https://leetcode.com/problems/snapshot-array/), which is
nearly the same versioned-read idea. Whenever data is kept in sorted order and you
need "the last thing at or before X," reach for a binary search.
