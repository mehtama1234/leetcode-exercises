# 57. Insert Interval

**Pattern:** Intervals (spend the already-sorted, disjoint input)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/insert-interval/

## The problem in plain words

You already have a tidy list of ranges: sorted by start, none overlapping. Someone
hands you one more range and asks you to slot it in so the list stays tidy — still
sorted, still non-overlapping. The new range might overlap several existing ones,
which then all fuse together.

```diagram
   number line:  1  2  3  4  5  6  7  8  9 10 ...
   existing:     [1,2]  [3,5]  [6,7]  [8,10]      [12,16]
   new [4,8]:            [4=========8]
                     absorbs 3,5 / 6,7 / 8,10  ->  [3========10]
   result:       [1,2]  [3==========10]           [12,16]
```

## Why this matters

The deeper lesson is **keeping a sorted, non-overlapping set of ranges as items come
in one at a time**. You already paid to keep the structure tidy, so a single new
item should cost a linear splice, not a full rebuild. The operation is finding the
affected run (before / overlapping / after) and fusing just that.

This is how live systems handle ranges. Calendars insert a new event without
re-sorting the day. Databases and allocators keep sorted, non-overlapping extents and
merge a freed block into place. Diff tools splice a changed line range into existing
hunks. Booking systems slot a new reservation into an already-ordered schedule.

What you buy is about n work with no sort: because the input is already ordered and
disjoint, you spend that fact instead of throwing it away — one pass to copy, merge,
and copy.

## Start from the obvious

The lazy correct answer: throw the new interval onto the list and re-run the full
Merge Intervals procedure.

```
intervals.append(new_interval)
return merge(intervals)   # sort + sweep, about n log n
```

Completely correct. But it *ignores a gift* — the list was already sorted and already
merged. You paid for a full sort to fix a list that was one interval out of place.

## Find the waste

Sorting from scratch is the waste. Since the existing intervals are sorted and
disjoint, each one falls into exactly one of three buckets relative to the new
interval `[s, e]`, and you meet the buckets in this exact order as you scan left to
right:

```diagram
   new [s,e]:              [s========e]
                    BEFORE      OVERLAP        AFTER
   existing:  [..] [..]   |  [..][.][..]  |   [..]  [..]
              ends < s    | touches [s,e] |   starts > e
              copy as-is  | absorb these  |   copy as-is
```

No sorting needed — just walk once.

## The insight

Three short loops over the list, in order:

1. **Copy the "before" intervals** straight through while `interval.end < s`.
2. **Merge the overlapping ones** while `interval.start <= e`: widen the new interval
   with `s = min(s, interval.start)` and `e = max(e, interval.end)`. Then append the
   grown `[s, e]` once.
3. **Copy the rest** ("after") straight through.

```diagram
   existing: [1,2] [3,5] [6,7] [8,10] [12,16]      new = [4,8]

   phase 1  [1,2].end=2 < 4   -> copy [1,2]
   phase 2  [3,5].start=3 <= 8  -> grow: s=min(4,3)=3  e=max(8,5)=8   [3,8]
            [6,7].start=6 <= 8  -> grow: e=max(8,7)=8                 [3,8]
            [8,10].start=8 <= 8 -> grow: e=max(8,10)=10               [3,10]
            append [3,10]
   phase 3  [12,16].start=12 > 10  -> copy [12,16]
   result:  [1,2] [3,10] [12,16]
```

Growing `[s, e]` as you go is what lets one new interval swallow a whole run of
existing ones.

## Complexity

- **Time: about n.** A single pass; each interval is touched once. No sort, because
  the input already is sorted.
- **Extra memory: about n.** The output list.

## Pitfalls

- **Off-by-one on the phase boundaries.** Phase 1 uses `end < s` (strictly before);
  phase 2 uses `start <= e` so that *touching* intervals like `[3,4]` and a new
  `[4, ...]` still merge.
- **Forgetting to append the merged interval** after phase 2 — it is easy to fall
  straight into phase 3 and drop it.
- **Empty input**, or a new interval that lands entirely before or after everything —
  the three-phase structure handles these for free; test them anyway.

## Transfer

The reusable idea is "when the input is already sorted or structured, do not re-sort
— sweep once and split into before / overlapping / after." Same shape as
[Merge Intervals / 56](../0056-merge-intervals/) but cheaper, because you spend the
sortedness instead of rebuilding it. The three-bucket split also shows up in
range-update problems and interval scheduling.
