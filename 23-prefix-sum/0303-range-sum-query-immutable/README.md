# 303. Range Sum Query - Immutable

**Pattern:** Prefix sum (precompute running totals)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/range-sum-query-immutable/

## The problem in plain words

You get an array that never changes. Then you're asked, over and over, "what is the
sum of the slice from index `left` to index `right`?" Each answer should be fast,
even if there are thousands of questions.

```diagram
   index:  0    1    2    3    4    5
   nums: [-2 ,  0 ,  3 , -5 ,  2 , -1 ]

   sumRange(2, 5) = 3 + (-5) + 2 + (-1) = -1
                     \________________/
                     answer -1
```

## Why this matters

The real operation here is turning a *range* question into a *point* question. A
sum over `[left, right]` looks like it must touch every element in that range — but
if you have already recorded a running total up to each position, the range sum is
the difference of two of those totals. You trade one scan per query for one
subtraction.

This is the workhorse behind analytics and reporting. A dashboard showing "revenue
between two dates" precomputes daily running revenue so any date range is two
lookups, not a re-scan of the ledger. Integral images in computer vision store
running pixel sums so a box's brightness is four array reads, whatever its size.
Time-series databases keep rolling totals for the same reason.

What the good solution buys is a cheap, repeatable query. You pay about `n` steps
once to build the table, and then every question — no matter how many — is a single
step. When queries far outnumber the one-time setup, that is the line between a
report that renders instantly and one that recomputes from scratch each time.

## Start from the obvious

The definition hands you the code: to sum a range, add up the range.

```diagram
   def sumRange(left, right):
       return sum(nums[left .. right])
```

Correct, and fine if you ask one question. But if you ask `q` questions each
covering most of the array, you re-add the same numbers `q` times. That repeated
adding is the waste.

## Find the waste

Every query starts adding from `left`. But adding "from the start up to `right`"
and "from the start up to `left-1`" are things you could have computed once. The
picture:

```diagram
   want sum(2..5)         [ ==== the range we want ==== ]
   index:  0    1    2    3    4    5
   nums: [-2 ,  0 ,  3 , -5 ,  2 , -1 ]

   sum(0..5) = -3    ( everything up to and including index 5 )
   sum(0..1) = -2    ( everything strictly before index 2 )

   sum(2..5) = sum(0..5) - sum(0..1) = -3 - (-2) = -1

   both pieces start at index 0  ->  they are PREFIXES, precomputable
```

There are only `n+1` distinct prefixes, so compute them all a single time and
store them.

## The insight

Build `prefix[i] = nums[0] + ... + nums[i-1]`, with `prefix[0] = 0` (the sum of
zero elements). Then a range sum is one subtraction.

```diagram
   nums:      -2    0    3   -5    2   -1
   prefix:  0   -2   -2    1   -4   -2   -3
            ^                          ^
          prefix[0]=0            prefix[6]=-3  (sum of all 6)

   sumRange(2,5) = prefix[5+1] - prefix[2] = prefix[6] - prefix[2]
                 = -3 - (-2) = -1

   the +1 on the right end INCLUDES index 5;
   subtracting prefix[2] chops off everything before index 2.
```

The `+1` is because `prefix[k]` counts the first `k` elements, so to *include* index
`right` you need `prefix[right + 1]`. Subtracting `prefix[left]` removes everything
before `left`. One subtraction, no loop.

## Complexity

- **Time: about n to build once, then one step per query.** The answer is a single
  subtraction regardless of range width.
- **Extra memory: about n** for the prefix array of length `n+1`.

If you serve `q` queries, brute force is about `n·q`, while prefix sums are about
`n + q`.

## Pitfalls

- Off-by-one on the `+1`. Using a prefix array of length `n+1` with a leading zero
  makes the formula `prefix[right+1] - prefix[left]` clean and avoids special-casing
  `left == 0`.
- Building the prefix inside `sumRange` instead of the constructor — that throws
  away the whole point and makes every query `O(n)` again.
- Assuming the array can be updated. It can't here; if it could, you'd need a
  Fenwick tree or segment tree (a structure built for range sums that also change).

## Transfer

The move "precompute running totals so a range is a subtraction" generalizes to 2D
as [Range Sum Query 2D / 304](../0304-range-sum-query-2d-immutable/), and the same
prefix array unlocks "count subarrays with a property" problems like
[Subarray Sum Equals K / 560](../0560-subarray-sum-equals-k/) and
[Contiguous Array / 525](../0525-contiguous-array/). Whenever you see repeated range
totals over fixed data, reach for a prefix table first.
