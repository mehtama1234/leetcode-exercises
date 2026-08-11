# 56. Merge Intervals

**Pattern:** Intervals (sort by start, then sweep)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/merge-intervals/

## The problem in plain words

You have a bunch of ranges like `[1, 3]` and `[2, 6]`. Some overlap or touch. Squash
every overlapping group into one range and return what is left. So `[1, 3]` and
`[2, 6]` become the single range `[1, 6]`.

```diagram
   number line:  0  1  2  3  4  5  6  7  8  9 10 ...
   [1,3]            [==]
   [2,6]               [=======]
   [8,10]                             [====]
                    \_____________/
   merged:          [1========6]      [8==10]
```

## Why this matters

The core operation is **coalescing overlapping ranges into their union** —
collapsing a messy set of segments on a number line (or a time line) into the
smallest set of separate spans. Sorting by start turns "search everywhere for an
overlap" into "just look at the neighbor," which is the reusable trick.

This is everyday work in real systems. Calendars merge busy blocks to show free/busy
at a glance. Databases merge index ranges so they do not read the same rows twice.
Memory allocators coalesce adjacent freed blocks back into larger regions. Genomics
merges overlapping read alignments into coverage intervals. Firewall tooling
collapses overlapping IP or port ranges into compact rules.

What you buy is one sort plus one linear sweep — about n·log n — and a smaller,
non-overlapping output that every later step can process without re-checking for
hidden overlaps.

## Start from the obvious

Overlap is a relationship between *pairs*, so the honest first thought is: check
every pair, and whenever two overlap, merge them and start over.

```
repeat until nothing changes:
    for each pair (a, b):
        if they overlap: replace them with their merge
```

This works but it is ugly — it is about n × n per pass and can take several passes,
because merging two intervals can create a new one that now overlaps a third you
already looked at. The trouble is that overlaps can hide *anywhere* in the list.

## Find the waste

The mess comes from the intervals being in random order, so a partner might be far
away. But look at what "overlap" means: interval B overlaps interval A when B starts
before A ends. That is a fact about **starts and ends on a number line**, and a
number line is ordered.

So sort by start. Now the intervals march left to right, and the key consequence:

> Once you are building a merged interval, the only thing that can extend it is the
> **next** interval in sorted order. Everything earlier started earlier and is
> already accounted for.

That collapses "search everywhere for a partner" into "just look at the next one."

## The insight

Sort by start, then walk once, keeping the interval you are currently building:

1. If the next interval starts at or before your current end, they touch or overlap —
   push your end out to `max(current_end, next_end)`.
2. If it starts after your current end, there is a gap — the current interval is
   finished, so emit it and begin a fresh one.

```diagram
   input (unsorted):  [1,3] [8,10] [2,6] [15,18]
   sort by start   :  [1,3] [2,6] [8,10] [15,18]

   number line: 1  2  3  4  5  6 ... 8  9 10 ... 15 16 17 18
   build [1,3]  [==]
   see  [2,6]      [==]  2 <= 3  -> extend end to max(3,6)=6   [1====6]
   see  [8,10]                    8 > 6   -> gap, emit [1,6], start [8,10]
   see  [15,18]                          15 > 10 -> gap, emit [8,10], start [15,18]
   result: [1,6] [8,10] [15,18]
```

The `max` matters: a later interval can sit fully *inside* the current one (`[1,10]`
then `[2,3]`), and you must not shrink the end back to 3.

```diagram
   [1,10]  [1==============10]
   [2,3]      [2=3]                 fully inside
   end = max(10, 3) = 10            keep 10, do NOT drop to 3
```

## Complexity

- **Time: about n·log n.** The sort dominates; the sweep itself is one pass.
- **Extra memory: about n.** For the output list (and the sort). Copy the first
  interval so the caller's input is not changed.

## Pitfalls

- **Touching counts as overlapping** if the problem says so: `[1, 4]` and `[4, 5]`
  merge into `[1, 5]`. Use `start <= last_end`, not `<`.
- **Fully nested intervals** — take `max(end, ...)`, never blindly overwrite the end
  with the newer interval's end.
- **Sorting by end instead of start** breaks the "only the next one matters"
  guarantee.
- Changing the caller's input in place — copy the seed interval.

## Transfer

"Sort by one endpoint, then sweep and either extend or start-new" is the spine of
almost every interval problem: [Insert Interval / 57](../0057-insert-interval/),
[Non-overlapping Intervals / 435](../0435-non-overlapping-intervals/), and
[Meeting Rooms / 252](../0252-meeting-rooms/). Whenever ranges on a line need to be
combined or checked for conflict, sort first — order turns a global search into a
local decision.
