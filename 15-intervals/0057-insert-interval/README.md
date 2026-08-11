# 57. Insert Interval

**Pattern:** Intervals (exploit the already-sorted, disjoint input)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/insert-interval/

## The problem in plain words

You already have a tidy list of ranges: sorted by start, none of them overlap.
Someone hands you one more range and asks you to slot it in so the list stays
tidy — still sorted, still non-overlapping. The new range might overlap several
existing ones, which then all fuse together.

## Start from the obvious

The lazy correct answer: throw the new interval onto the list and re-run the full
Merge Intervals procedure.

```
intervals.append(new_interval)
return merge(intervals)   # sort + sweep
```

That's completely correct and gives `O(n log n)`. But it *ignores a gift* — the
list was already sorted and already merged. We paid for a full sort to fix a list
that was only one interval out of place.

## Find the waste

Sorting from scratch is the waste. Since the existing intervals are sorted and
disjoint, every one of them falls into exactly one of three buckets relative to
the new interval `[s, e]`:

- **Before:** it ends before `s` — no contact, keep as-is.
- **Overlapping:** it starts at or before `e` *and* ends at or after `s` — it
  must be absorbed.
- **After:** it starts after the merged range ends — no contact, keep as-is.

And because the list is sorted, you meet these three buckets in that exact order
as you scan left to right. No sorting needed — just walk once.

## The insight

Three short loops over the list, in order:

1. **Copy the "before" intervals** straight into the output while
   `interval.end < s`.
2. **Merge the overlapping ones** while `interval.start <= e`: widen the new
   interval with `s = min(s, interval.start)` and `e = max(e, interval.end)`.
   Then append the grown `[s, e]` once.
3. **Copy the rest** ("after") straight through.

Growing `[s, e]` as you go is what lets one new interval swallow a whole run of
existing ones (`[4,8]` eating `[3,5],[6,7],[8,10]` → `[3,10]`).

## Complexity

- **Time:** `O(n)` — a single linear pass; each interval is touched once. No
  sort, because the input already is sorted.
- **Space:** `O(n)` — the output list.

## Pitfalls

- **Off-by-one on the phase boundaries.** Phase 1 uses `end < s` (strictly
  before); phase 2 uses `start <= e` so that *touching* intervals like `[3,4]`
  and a new `[4, ...]` still merge.
- **Forgetting to append the merged interval** after phase 2 — it's easy to fall
  straight into phase 3 and drop it.
- **Empty input** or a new interval that lands entirely before/after everything —
  the three-phase structure handles these for free; test them anyway.

## Transfer

The reusable idea is "when the input is already sorted/structured, don't re-sort
— sweep once and split into before / overlapping / after." Same shape as
[Merge Intervals / 56](../0056-merge-intervals/) but cheaper because you spend the
sortedness instead of rebuilding it. The three-bucket split also shows up in
range-update problems and in interval scheduling.
