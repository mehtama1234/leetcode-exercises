# 128. Longest Consecutive Sequence

**Pattern:** Hashing (set membership + run detection)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/longest-consecutive-sequence/

## The problem in plain words

You have a jumbled bag of integers. Ignoring their positions, what's the longest
chain of numbers that step up by exactly one — like `3,4,5,6` — that you can pull
out? Return the chain's length. The catch: it must run in `O(n)`.

## Start from the obvious

Sort the numbers and consecutive integers line up as neighbors; then one walk
counts the longest run of `+1` steps:

```
ordered = sorted(set(nums))
for each adjacent pair:
    if it steps up by 1: extend current run
    else: reset run
```

That's correct and easy to reason about — but sorting is `O(n log n)`, and the
problem explicitly demands `O(n)`. So the sort has to go.

## Find the waste

Sorting produces a *total order* of every element, but we don't need to know how
all the numbers relate — we only need to trace chains upward by ones. That's a
series of "is `x+1` also here?" questions, and a hash set answers each in `O(1)`
without any ordering.

Naively though, "for each `x`, walk `x, x+1, x+2, …`" can re-walk the same run
many times: starting from `3` you walk `3,4,5,6`; starting from `4` you walk
`4,5,6` again. That repeated walking is the waste — and it's what would make the
set approach `O(n^2)` if done carelessly.

## The insight

Walk each run **only once**, by starting a count exclusively from a run's true
beginning. A value `x` begins a run precisely when `x - 1` is **not** in the set —
nothing extends it downward. For those starts, walk forward while `x+1, x+2, …`
exist and measure the length:

```
present = set(nums)
for x in present:
    if x-1 in present: continue      # not a start, skip
    length = 1; y = x
    while y+1 in present: y += 1; length += 1
    best = max(best, length)
```

Because the inner `while` only ever runs from a start, each element is visited by
it at most once across the whole algorithm. That's what keeps the total linear.

## Complexity

- **Time:** `O(n)` — building the set is `O(n)`; the `x-1` guard ensures every
  element is stepped over by the inner loop at most once total.
- **Space:** `O(n)` — the set holds every distinct value.

## Pitfalls

- **The whole trick is the `if x-1 in present: continue` guard.** Without it you
  re-walk runs and silently drop to `O(n^2)`.
- Put values in a **set**, not a list — the `in` test must be `O(1)`, or the
  bound collapses.
- Duplicates must not inflate the count; the set dedupes them automatically.
- Empty input returns `0`; a single element returns `1`.

## Transfer

The reusable ideas: **dump into a set for O(1) presence tests**, and **anchor
work at the unique start of a structure so you do it once** (here, "no smaller
neighbor" marks a start). The set-membership half is the same tool from
[Contains Duplicate / 217](../0217-contains-duplicate/) and
[Two Sum / 1](../0001-two-sum/); the "count each connected piece once from its
boundary" idea reappears in grid/island problems.
