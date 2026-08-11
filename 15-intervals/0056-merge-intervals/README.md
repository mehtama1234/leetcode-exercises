# 56. Merge Intervals

**Pattern:** Intervals (sort by start, then sweep)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/merge-intervals/

## The problem in plain words

You have a bunch of ranges like `[1, 3]` and `[2, 6]`. Some of them overlap or
touch. Squash every overlapping group into one range and return what's left. So
`[1, 3]` and `[2, 6]` become the single range `[1, 6]`.

## Start from the obvious

Overlap is a relationship between *pairs*, so the honest first thought is: check
every pair, and whenever two overlap, merge them and start over.

```
repeat until nothing changes:
    for each pair (a, b):
        if they overlap: replace them with their merge
```

This works but it's ugly — it's `O(n^2)` per pass and can take several passes,
because merging two intervals can create a new interval that now overlaps a third
one you already looked at. The trouble is that overlaps can hide *anywhere* in
the list.

## Find the waste

The mess comes from intervals being in random order, so a partner might be far
away. But notice what "overlap" actually means: interval B overlaps interval A
when B starts before A ends. That's a statement about **starts and ends on a
number line**, and a number line is ordered.

So sort by start. Now the intervals march left to right. The key consequence:

> Once you're building a merged interval, the only thing that can extend it is
> the **next** interval in sorted order. Everything earlier started earlier and
> is already accounted for.

That collapses the "search everywhere for a partner" into "just look at the next
one."

## The insight

Sort by start, then walk once, keeping the interval you're currently building:

1. If the next interval starts at or before your current end, they touch or
   overlap — push your end out to `max(current_end, next_end)`.
2. If it starts after your current end, there's a gap — the current interval is
   finished, so emit it and begin a fresh one from the next interval.

The `max` matters: a later interval can sit fully *inside* the current one
(`[1, 10]` then `[2, 3]`), and you must not shrink the end back to 3.

## Complexity

- **Time:** `O(n log n)` — dominated by the sort. The sweep itself is one `O(n)`
  pass.
- **Space:** `O(n)` — for the output list (and the sort). We copy the first
  interval so the caller's input isn't mutated.

## Pitfalls

- **Touching counts as overlapping** if the problem says so: `[1, 4]` and
  `[4, 5]` merge into `[1, 5]`. Use `start <= last_end`, not `<`.
- **Fully nested intervals** — take `max(end, ...)`, never blindly overwrite the
  end with the newer interval's end.
- **Sorting by end instead of start** breaks the "only the next one matters"
  guarantee.
- Mutating the caller's input in place (copy the seed interval).

## Transfer

"Sort by one endpoint, then sweep and either extend or start-new" is the spine of
almost every interval problem: [Insert Interval / 57](../0057-insert-interval/),
[Non-overlapping Intervals / 435](../0435-non-overlapping-intervals/), and
[Meeting Rooms / 252](../0252-meeting-rooms/). Whenever ranges on a line need to
be combined or checked for conflict, sort first — order turns a global search
into a local decision.
