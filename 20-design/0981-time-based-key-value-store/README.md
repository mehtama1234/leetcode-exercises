# 981. Time Based Key-Value Store

**Pattern:** Sorted history + binary search (floor query)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/time-based-key-value-store/

## The problem in plain words

Store values under a key, but every write is tagged with a timestamp, so a key
can have many versions over time. When someone reads with `get(key, t)`, give
back the value that was set at the *latest* timestamp still at or before `t` —
the value that was "in effect" at time `t`. If nothing was set by then, return
`""`. Writes always arrive with increasing timestamps.

## Why this matters

The real operation is a **point-in-time / "as-of" read of versioned data**: given
a history of changes, answer "what did this look like at moment T?" The clever
part is realizing the history is *already sorted by time*, which turns the query
into a binary search for the floor of `t`.

This is the beating heart of many real systems. Multi-version concurrency control
(MVCC) in Postgres and MySQL keeps timestamped row versions so each transaction
reads a consistent snapshot. Time-series databases and monitoring stores answer
"value as of this time." Git, event-sourced systems, and configuration stores
that let you read a past revision all do this floor-by-time lookup.

What the good solution buys is a **latency win by avoiding a scan**: because each
key's versions are sorted, a `get` is O(log n) instead of walking backward
through possibly millions of historical writes. You spend a little ordered
storage to make time-travel reads fast.

## Start from the obvious

Keep a list of `(timestamp, value)` per key. To answer `get(key, t)`, scan for
the entry with the largest timestamp that is <= t.

```
best = ""
for (ts, val) in history[key]:
    if ts <= t:
        best = val          # keep the latest that qualifies
    else:
        break               # list is sorted; nothing later qualifies
return best
```

Correct, and thanks to sorted order it can stop early — but in the worst case
(large `t`) it still walks the entire history: O(n) per query.

## Find the waste

The scan visits every version even though the list is sorted. Any time you're
linearly searching a *sorted* list for a boundary ("largest value <= t"), you're
leaving a binary search on the table. We don't need to look at each version — we
need to *land on the boundary* directly.

## The insight

Store two parallel arrays per key: the timestamps and the values, appended in
order. Since timestamps arrive strictly increasing, the timestamp array is
sorted with zero extra effort.

For `get(key, t)`, do a **floor query** with binary search:

- `bisect_right(times, t)` returns the first index whose timestamp is strictly
  greater than `t`.
- The entry just *before* that index (index `i - 1`) is the largest timestamp
  <= t — our answer.
- If that index is 0, every stored time is later than `t`, so return `""`.

## Complexity

- **set:** `O(1)` — append to two lists.
- **get:** `O(log n)` — binary search over one key's `n` versions.
- **Space:** `O(total writes)` — every version is kept (that's the point; you can
  read any past moment).

## Pitfalls

- Reaching for `bisect_left` when you want `bisect_right`. For "largest timestamp
  <= t," `bisect_right` then step back one is the clean pattern; getting this
  wrong breaks exact-timestamp hits.
- Forgetting the "nothing set yet" case — index 0 means return `""`.
- Assuming timestamps are sorted when they might not be. Here the problem
  guarantees increasing timestamps; if it didn't, you'd need to insert in order
  (or sort), which changes the cost.
- Storing `(ts, value)` tuples and re-sorting on every read — unnecessary given
  the ordering guarantee.

## Transfer

The "binary-search a sorted structure for a boundary" move is broad. See
[Search Insert Position / 35](https://leetcode.com/problems/search-insert-position/),
[Find First and Last Position / 34](https://leetcode.com/problems/find-first-and-last-position-of-element-in-sorted-array/),
and [Snapshot Array / 1146](https://leetcode.com/problems/snapshot-array/),
which is nearly the same versioned-read idea. Whenever data is kept in sorted
order and you need "the last thing at or before X," reach for `bisect`.
