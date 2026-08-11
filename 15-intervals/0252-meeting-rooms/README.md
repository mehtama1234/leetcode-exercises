# 252. Meeting Rooms

**Pattern:** Intervals (sort by start, check neighbors)
**Difficulty:** Easy (LeetCode premium)
**Link:** https://leetcode.com/problems/meeting-rooms/

## The problem in plain words

You are given a list of meetings, each with a start and end time. Can one person sit
through all of them? They can exactly when no two meetings overlap in time.

Standard signature: `can_attend_all(intervals) -> bool`.

```diagram
   time:  0  5  10 15 20 25 30
   [0,30]  [==================]
   [5,10]     [==]
   [15,20]           [==]
                ^         ^
   [0,30] covers both -> overlaps -> can't attend all -> false
```

## Why this matters

The core operation is a **double-booking check**: given reservations on one shared
resource, can they all coexist without any two overlapping? Sorting by start reduces
"compare every pair" to "compare each item to its neighbor," because in sorted order
any overlap forces an *adjacent* overlap.

This is the yes/no gate behind a lot of real scheduling. Booking systems check
whether one room, one doctor, or one rental car can honor a set of reservations.
Operating systems verify that tasks on one core do not overlap. Databases detect
conflicting locks or transaction time-ranges on the same row. Any "is this single
resource over-committed?" question is this check.

What you buy is about n·log n: a sort plus one neighbor-only pass, with an early exit
the moment a conflict appears — instead of the n × n cost of comparing every pair.

## Start from the obvious

Overlap is a pairwise thing, so the honest brute force checks every pair:

```
for each pair (a, b):
    if a and b overlap: return False
return True
```

Two meetings overlap when one starts before the other ends. That is about n × n
comparisons — correct, but wasteful.

## Find the waste

You are comparing meetings that are nowhere near each other in time. If you sort by
start time, the meetings line up chronologically and a strong fact drops out:

> If any two meetings overlap at all, then two *adjacent* meetings (in start order)
> overlap.

Why? Sort by start. Suppose meeting `j` overlaps an earlier meeting `i`. Every
meeting *between* them started before `j` too, and since `i` reaches into `j`'s time,
it reaches into theirs as well — so a neighboring pair already conflicts. You never
have to look further than the previous meeting.

```diagram
   sorted by start:   i        k          j
   time:            [i===========]
                         [k==]                 k starts inside i -> i,k already clash
                              [j========]
   if i reaches j, it reaches k (which sits between) -> neighbors conflict first
```

## The insight

Sort by start, then sweep once and compare each meeting to the one right before it.
If the current meeting starts *before* the previous one ends, that is a conflict —
return `False`. Survive the whole list, return `True`.

```
sort by start
for i in 1..n-1:
    if intervals[i].start < intervals[i-1].end: return False
return True
```

```diagram
   input:  [[7,10], [2,4]]   ->  sorted:  [2,4]  [7,10]
   time:  2  4        7   10
          [==]        [====]
   check:  [7,10].start = 7  >=  [2,4].end = 4   -> no conflict
   result: true

   back-to-back is allowed:  [1,5] [5,10]
   time:  1        5        10
          [========|========]
          [5,10].start = 5  <  [1,5].end = 5 ?  5 < 5 is false -> OK, true
```

Use strict `<`: a meeting starting exactly when the previous ends (`[1,5]` then
`[5,10]`) is back-to-back, which is allowed.

## Complexity

- **Time: about n·log n** — the sort; the neighbor check is one pass.
- **Extra memory: a fixed amount** beyond sorting (only adjacent pairs are compared).

## Pitfalls

- **Boundary equality.** `[1,5]` and `[5,10]` do **not** overlap. Comparing with
  `<=` would wrongly reject them; use `<`.
- **Forgetting to sort** — the "only neighbors matter" shortcut is only valid after
  sorting by start.
- Empty list and single meeting both return `True` with no work to do.

## Transfer

This is the cheapest member of the interval family: sort by start, then a single
"does this overlap its neighbor?" check. The moment you need to know *how many* rooms
conflicting meetings require rather than just yes/no, it becomes
[Meeting Rooms II / 253](../0253-meeting-rooms-ii/). The same sort-then-scan skeleton
underlies [Merge Intervals / 56](../0056-merge-intervals/).
