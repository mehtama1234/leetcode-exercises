# 435. Non-overlapping Intervals

**Pattern:** Greedy interval scheduling (sort by end time)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/non-overlapping-intervals/

## The problem in plain words

You have a set of ranges, some overlapping. Delete as few as possible so that none of
the survivors overlap. Return *how many* you had to delete.

```diagram
   time:  1  2  3  4
   [1,2]   [==]
   [2,3]      [==]
   [3,4]         [==]
   [1,3]   [=====]
              ^ [1,3] clashes with [2,3] -> drop 1 interval -> answer 1
   keep: [1,2] [2,3] [3,4]   (all touch but none overlap)
```

## Why this matters

This is **activity selection** — keep the largest set of non-overlapping intervals
(removing the fewest is the mirror of keeping the most). The core operation is a
greedy scan sorted *by end time*: always keep the interval that finishes soonest,
because it leaves the most room for the rest, and a swap argument proves that is best.

It is the heart of squeezing the most work onto one resource. Schedulers pick the most
jobs one machine can run without conflict. Broadcasters select the most non-conflicting
ad slots. Compilers use the same idea in register allocation — fitting the most live
ranges into limited registers.

What you buy is about n·log n: one end-sorted pass replaces an exploding search over
subsets, and the greedy is provably best, not just a decent guess.

## Start from the obvious

"Delete the fewest" invites a brute force: try every subset of intervals, check which
subsets are overlap-free, keep the biggest. The answer is
`total - biggest_overlap_free_subset`.

```
best = 0
for each subset S of intervals:
    if no two intervals in S overlap:
        best = max(best, len(S))
return len(intervals) - best
```

That is about 2ⁿ subsets — hopeless. But it names the real goal precisely: **removing
the fewest is the same as keeping the most non-overlapping intervals.**

## Find the waste / The insight

That reframing — "keep the most" — is the classic *activity selection* problem, and it
has a clean greedy answer. The trick is choosing which interval to keep when two clash.

Sort the intervals **by end time**. Then repeatedly keep the interval that finishes
earliest among those that still fit:

> The interval that ends soonest is always safe to keep, because it leaves the most of
> the timeline free for everything after it.

```diagram
   sort by END:   [1,2]  [2,3]  [1,3]  [3,4]
   ends:            2      3      3      4

   time:  1  2  3  4
   [1,2]   [==]                 keep, kept_end = 2
   [2,3]      [==]  start 2 >= 2  -> keep, kept_end = 3
   [1,3]   [=====]  start 1 <  3  -> CLASH, remove  (removed = 1)
   [3,4]         [==] start 3 >= 3 -> keep, kept_end = 4
   kept 3 of 4  ->  removed = 4 - 3 = 1
```

**Why is greedy the true best, not just a reasonable guess?** Swap argument: take any
best set of kept intervals. Look at whichever of them ends earliest. If it is not the
globally-earliest-ending interval, swap that one in — it ends even sooner, so it only
frees up room and creates no new overlap. So some best solution always includes the
earliest-finishing interval. Keep it, then repeat on what is left. The greedy follows
exactly that best choice at every step.

Concretely: walk the end-sorted list tracking `kept_end`, the finish time of the last
interval you kept. The next interval fits if `start >= kept_end` — keep it and advance
`kept_end`. Otherwise it clashes with something you are keeping, so it is a removal.

## Complexity

- **Time: about n·log n** — the sort dominates; the sweep is one pass.
- **Extra memory: a fixed amount** beyond the sort (a count and one boundary).

## Pitfalls

- **Touching is not overlapping.** `[1, 2]` and `[2, 3]` share only the point `2`;
  both can stay. Use `start >= kept_end`, so equality means "fits."
- **Sorting by start instead of end** is the common wrong instinct. It can be made to
  work if, on a clash, you keep the interval that *ends* earlier (see
  `erase_overlap_intervals_brute` in the solution) — but sort-by-end is the cleaner,
  canonical form and makes the "why it's best" argument obvious.
- Returning the kept count instead of the removed count (`n - kept`).

## Transfer

Sort-by-end greedy is the template for scheduling the maximum number of
non-conflicting tasks: meeting-room selection, "maximum number of events you can
attend," and any "pick the most compatible intervals" problem. It is the mirror image
of [Meeting Rooms II / 253](../0253-meeting-rooms-ii/) (which asks how many rooms you
would need if you *could not* drop any). Contrast with
[Merge Intervals / 56](../0056-merge-intervals/), where you sort by **start** because
you are fusing overlaps rather than choosing among them.
