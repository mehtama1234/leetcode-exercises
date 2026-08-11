# 252. Meeting Rooms

**Pattern:** Intervals (sort by start, check neighbors)
**Difficulty:** Easy (LeetCode premium)
**Link:** https://leetcode.com/problems/meeting-rooms/

## The problem in plain words

You're given a list of meetings, each with a start and end time. Can one person
sit through all of them? They can iff no two meetings overlap in time.

Standard signature: `can_attend_all(intervals) -> bool`.

## Why this matters

The fundamental operation is a **conflict / double-booking check**: given a set of
reservations on a single shared resource, can they all coexist without any two
overlapping. Sorting by start reduces "compare every pair" to "compare each item
to its neighbor," because in sorted order any overlap forces an adjacent overlap.

This is the yes/no gate behind a lot of real scheduling. Booking systems check
whether one room, one doctor, or one rental car can honor a set of reservations.
Operating systems and real-time schedulers verify that tasks assigned to one core
don't overlap. Databases detect conflicting locks or transaction time-ranges on
the same row. Network and radio systems check that transmissions on one channel
don't collide. Any "is this single resource over-committed?" question is this
check.

What we buy is `O(n log n)`: a sort plus one neighbor-only pass, and an early
exit the moment a conflict appears — instead of the quadratic cost of comparing
every pair of bookings.

## Start from the obvious

Overlap is a pairwise thing, so the honest brute force checks every pair:

```
for each pair (a, b):
    if a and b overlap: return False
return True
```

Two meetings overlap when one starts before the other ends. That's `O(n^2)`
comparisons — correct, but wasteful.

## Find the waste

We're comparing meetings that are nowhere near each other in time. If we sort by
start time, the meetings line up chronologically, and a strong fact drops out:

> If any two meetings overlap at all, then two *adjacent* meetings (in start
> order) overlap.

Why? Sort by start. Suppose meeting `j` overlaps an earlier meeting `i`. Then
every meeting *between* them started before `j` too, and since `i` reaches into
`j`'s time, it reaches into theirs as well — so a neighboring pair already
conflicts. That means we never have to look further than the previous meeting.

## The insight

Sort by start, then sweep once and compare each meeting to the one right before
it. If the current meeting starts *before* the previous one ends, that's a
conflict — return `False`. If we get through the whole list, return `True`.

```
sort by start
for i in 1..n-1:
    if intervals[i].start < intervals[i-1].end: return False
return True
```

Use strict `<`: a meeting starting exactly when the previous ends
(`[1,5]` then `[5,10]`) is back-to-back, which is allowed.

## Complexity

- **Time:** `O(n log n)` — the sort; the neighbor check is one `O(n)` pass.
- **Space:** `O(1)` beyond sorting (we only look at adjacent pairs).

## Pitfalls

- **Boundary equality.** `[1,5]` and `[5,10]` do **not** overlap. Comparing with
  `<=` would wrongly reject them; use `<`.
- **Forgetting to sort** — the "only neighbors matter" shortcut is only valid
  after sorting by start.
- Empty list and single meeting are both trivially `True`.

## Transfer

This is the cheapest member of the interval family: sort by start, then a single
"does this overlap its neighbor?" check. The moment you need to know *how many*
rooms conflicting meetings require rather than just yes/no, it becomes
[Meeting Rooms II / 253](../0253-meeting-rooms-ii/). The same sort-then-scan
skeleton underlies [Merge Intervals / 56](../0056-merge-intervals/).
