# 435. Non-overlapping Intervals

**Pattern:** Greedy interval scheduling (sort by end time)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/non-overlapping-intervals/

## The problem in plain words

You have a set of ranges, some of which overlap. Delete as few as possible so
that none of the survivors overlap. Return *how many* you had to delete.

## Why this matters

This is **activity selection** — keep the largest set of non-overlapping
intervals (removing the fewest is the mirror of keeping the most). The
fundamental operation is a greedy scan sorted *by end time*: always keep the
interval that finishes soonest, because it leaves the most room for the rest,
and an exchange argument proves that's optimal.

It's the core of maximizing throughput on a single resource. Schedulers pick the
most jobs one machine or one CPU can run without conflict. Broadcast and
advertising systems select the most non-conflicting slots to air. Meeting and
room booking maximizes how many requests one room can honor. Compilers use the
same idea in register allocation — fitting the most live ranges into limited
registers. Bandwidth and reservation systems admit the most non-overlapping
requests a channel can serve.

What we buy is `O(n log n)`: one end-sorted pass replaces an exponential search
over subsets, and the greedy is provably optimal, not just a heuristic — so we
get the true best packing under a tight time budget.

## Start from the obvious

"Delete the fewest" invites a brute force: try every subset of intervals, check
which subsets are overlap-free, and keep the biggest one. The answer is
`total - biggest_overlap_free_subset`.

```
best = 0
for each subset S of intervals:
    if no two intervals in S overlap:
        best = max(best, len(S))
return len(intervals) - best
```

That's `O(2^n)` — hopeless. But it names the real goal precisely: **removing the
fewest is the same as keeping the most non-overlapping intervals.**

## Find the waste / The insight

That reframing — "keep the most" — is the classic *activity selection* problem,
and it has a clean greedy answer. The trick is choosing which interval to keep
when two clash.

Sort the intervals **by end time**. Then repeatedly keep the interval that
finishes earliest among those that still fit:

> The interval that ends soonest is always safe to keep, because it leaves the
> most of the timeline free for everything after it.

Why is greedy *optimal* and not just a reasonable guess? Exchange argument: take
any optimal set of kept intervals. Look at whichever of them ends earliest. If
it's not the globally-earliest-ending interval, you can swap that one in without
creating any new overlap (it ends even sooner, so it can only free up room). So
some optimal solution always includes the earliest-finishing interval — keep it,
then recurse on what's left. The greedy is following exactly that optimal choice
at every step.

Concretely: walk the end-sorted list tracking `kept_end`, the finish time of the
last interval we kept. The next interval fits if `start >= kept_end` — keep it
and advance `kept_end`. Otherwise it overlaps something we're keeping, so it's a
removal.

## Complexity

- **Time:** `O(n log n)` — the sort dominates; the sweep is one `O(n)` pass.
- **Space:** `O(1)` beyond the sort (we only track a count and one boundary).

## Pitfalls

- **Touching is not overlapping.** `[1, 2]` and `[2, 3]` share only the endpoint
  `2`; they can both stay. Use `start >= kept_end`, so equality means "fits."
- **Sorting by start instead of end** is the common wrong instinct. It can be
  made to work if, on a clash, you keep the interval that *ends* earlier (see
  `erase_overlap_intervals_brute` in the solution) — but sort-by-end is the
  cleaner, canonical form and makes the optimality argument obvious.
- Returning the kept count instead of the removed count (`n - kept`).

## Transfer

Sort-by-end greedy is the template for scheduling the maximum number of
non-conflicting tasks: meeting-room selection, the "maximum number of events you
can attend," and any "pick the most compatible intervals" problem. It's the
mirror image of [Meeting Rooms II / 253](../0253-meeting-rooms-ii/) (which asks
how many rooms you'd need if you *couldn't* drop any). Contrast with
[Merge Intervals / 56](../0056-merge-intervals/), where you sort by **start**
because you're fusing overlaps rather than choosing among them.
