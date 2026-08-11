# 303. Range Sum Query - Immutable

**Pattern:** Prefix sum (precompute cumulative totals)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/range-sum-query-immutable/

## The problem in plain words

You get an array that never changes. Then you're asked, over and over, "what's
the sum of the slice from index `left` to index `right`?" Each answer should be
fast, even if there are thousands of questions.

## Why this matters

The real operation here is turning a *range* question into a *point* question.
A sum over `[left, right]` looks like it needs to touch every element in that
range — but if you've already recorded a running total up to each position, the
range sum is the difference of two of those totals. You trade one scan per query
for one subtraction.

This is the workhorse behind analytics and reporting. A dashboard showing
"revenue between two dates" precomputes daily cumulative revenue so any date
range is two lookups, not a re-scan of the ledger. Integral images in computer
vision store cumulative pixel sums so a box's brightness is four array reads,
independent of box size. Time-series databases keep rolling aggregates for the
same reason.

What the good solution buys is a cheap, repeatable query. You pay `O(n)` once to
build the table, and then every question — no matter how many — is `O(1)`. When
queries vastly outnumber the one-time setup, that's the difference between a
report that renders instantly and one that recomputes from scratch each time.

## Start from the obvious

The definition hands you the code: to sum a range, add up the range.

```
def sumRange(left, right):
    return sum(nums[left : right + 1])
```

Correct, and fine if you ask one question. But if you ask `q` questions each
covering most of the array, you re-add the same numbers `q` times. That repeated
adding is the waste.

## Find the waste

Every query starts adding from `left`. But adding "from the start up to `right`"
and "from the start up to `left-1`" are things you could have computed once.
Notice:

```
sum(left..right) = sum(0..right) - sum(0..left-1)
```

Both pieces are *prefixes* — sums that begin at index 0. There are only `n+1`
distinct prefixes, so compute them all a single time and store them.

## The insight

Build `prefix[i] = nums[0] + ... + nums[i-1]`, with `prefix[0] = 0` (the sum of
zero elements). Then:

```
sumRange(left, right) = prefix[right + 1] - prefix[left]
```

The `+1` is because `prefix[k]` counts the first `k` elements, so to *include*
index `right` you need `prefix[right + 1]`. Subtracting `prefix[left]` chops off
everything before `left`. One subtraction, no loop.

## Complexity

- **Time:** `O(n)` to build the prefix table once, then `O(1)` per query — the
  answer is a single subtraction regardless of range width.
- **Space:** `O(n)` for the prefix array of length `n+1`.

If you serve `q` queries, brute force is `O(n·q)` while prefix sums are
`O(n + q)`.

## Pitfalls

- Off-by-one on the `+1`. Using a prefix array of length `n+1` with a leading
  zero makes the formula `prefix[right+1] - prefix[left]` clean and avoids
  special-casing `left == 0`.
- Building the prefix inside `sumRange` instead of the constructor — that throws
  away the whole point and makes every query `O(n)` again.
- Assuming the array can be updated. It can't here; if it could, you'd need a
  Fenwick/segment tree (see the "mutable" variant).

## Transfer

The move "precompute cumulative totals so a range is a subtraction" generalizes
to 2D as [Range Sum Query 2D / 304](../0304-range-sum-query-2d-immutable/), and
the same prefix array unlocks "count subarrays with a property" problems like
[Subarray Sum Equals K / 560](../0560-subarray-sum-equals-k/) and
[Contiguous Array / 525](../0525-contiguous-array/). Whenever you see repeated
range aggregates over fixed data, reach for a prefix table first.
