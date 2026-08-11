# 300. Longest Increasing Subsequence

**Pattern:** Dynamic programming (pin the chain to where it ends) → smallest-tail trick
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/longest-increasing-subsequence/

## The problem in plain words

Walk a list left to right and pick some of the numbers (skip any you like) so each
pick is strictly larger than the one before it. How long can that chain be? Return
only the length.

The picks don't have to sit next to each other:

```diagram
   nums:  [ 10 , 9 , 2 , 5 , 3 , 7 , 101 , 18 ]
                     ^       ^   ^    ^
                     2       3   7   101       chain: 2 < 3 < 7 < 101
   answer = 4
```

## Why this matters

The modeling move to keep is **pin the subproblem to the element it ends at.** A
best-chain can end anywhere, which makes it fuzzy; fix the last element and the
fuzz clears — the chain ending at `i` is one plus the best chain ending at some
earlier, smaller element. The faster version adds a second idea: to keep extending
chains, the only thing that matters about a chain of a given length is its
*smallest possible last value*.

Longest-increasing-chain questions show up in version and nesting problems (box or
envelope stacking after sorting), in chaining local matches into the longest
consistent order in bioinformatics, and in finding the longest improving streak in
a time series.

## Start from the obvious

A subsequence is "pick or skip each element," so the honest brute force is: try
every subset, keep the increasing ones, return the longest.

```
for every subset of nums:
    if it is strictly increasing:
        track the max length
```

That's `2^n` subsets — hopeless past ~20 elements. But it shows the answer's
shape: the chain grows one element at a time, and each element added must beat the
previous one.

## Find the waste

The trouble is a chain can end anywhere, so pin the ending down. Define `dp[i]` =
the length of the longest increasing chain that **ends at index `i`.** If the chain
ends at `i`, the element right before it is some earlier `nums[j]` with
`nums[j] < nums[i]`:

```
dp[i] = 1 + max(dp[j] for all j < i where nums[j] < nums[i])
      = 1   if no such j exists
```

Fill `dp` left to right and every `dp[j]` you look back at is already final. The
answer is `max(dp)`, since the chain can end at any index.

```diagram
   nums:  [ 10 ,  9 ,  2 ,  5 ,  3 ,  7 , 101 , 18 ]
   index:    0    1    2    3    4    5    6     7

   dp[2]=1 (2)
   dp[3]: look back for j<3 with nums[j]<5  -> only nums[2]=2, dp[2]=1
          dp[3] = 1 + 1 = 2                     (chain 2,5)
   dp[4]: nums[j]<3 -> nums[2]=2, dp[2]=1
          dp[4] = 2                             (chain 2,3)
   dp[5]: nums[j]<7 -> 2(dp1),5(dp2),3(dp2)  take max=2
          dp[5] = 1 + 2 = 3                     (chain 2,3,7 or 2,5,7)
   dp[6]: nums[j]<101 -> best earlier dp is dp[5]=3
          dp[6] = 1 + 3 = 4                     (chain 2,3,7,101)

   dp:  [ 1 , 1 , 1 , 2 , 2 , 3 , 4 , 4 ]
                                 ^max = 4

   dp[6] pulls from dp[5]:   dp[5] --+--> dp[6] = dp[5]+1
```

For each `i` we scan all earlier `j`, so this is about n × n steps.

## The insight (getting to about n·log n steps)

That scan is always hunting for the best chain we can *extend*. To extend chains,
the only thing that matters about a chain of a given length is its **smallest
possible last value** — a smaller tail leaves room for more future numbers.

So keep an array `tails`, where `tails[k]` is the smallest value that can end an
increasing chain of length `k + 1`. For each new number `x`:

```
find the leftmost tail >= x        (binary search — tails stays sorted)
if there is none:  x lengthens the record  -> append x
else:              x is a smaller tail here -> overwrite that slot
```

```diagram
   nums = [10, 9, 2, 5, 3, 7, 101, 18]

   x=10   tails = [10]
   x=9    9  replaces 10       tails = [9]
   x=2    2  replaces 9        tails = [2]
   x=5    5  > all, append     tails = [2, 5]
   x=3    3  replaces 5        tails = [2, 3]      <- smaller tail, len still 2
   x=7    7  > all, append     tails = [2, 3, 7]
   x=101  append               tails = [2, 3, 7, 101]
   x=18   18 replaces 101      tails = [2, 3, 7, 18]

   length of tails = 4  ->  LIS length = 4
```

Overwriting never hurts a future answer (a smaller tail is strictly more useful);
appending only happens when `x` truly lengthens the record. The final length of
`tails` is the LIS length, and because `tails` stays sorted each step is a binary
search — about n·log n steps overall.

One honest caveat: `tails` is **not** a real subsequence you can read off. Only its
*length* is meaningful; `[2, 3, 7, 18]` above was never an actual chain.
Reconstructing the true chain needs a separate parent-pointer array.

## Complexity

- **Brute force:** `2^n` subsets.
- **DP:** about n × n steps, about n memory.
- **Smallest-tail + binary search:** about n·log n steps, about n memory.

## Pitfalls

- **Strictly** increasing: use `bisect_left` (leftmost `>= x`), which overwrites
  on ties so equal values can't both count. Non-decreasing would use
  `bisect_right`.
- Empty input must return `0`; don't call `max()` on an empty `dp`.
- Believing `tails` is the actual subsequence — it isn't. Its length is correct;
  its contents are a jumble.

## Transfer

The "smallest tail per length + binary search" trick extends to
[Russian Doll Envelopes / 354](https://leetcode.com/problems/russian-doll-envelopes/)
(2-D LIS after sorting). The `dp[i]` = "best answer ending at index `i`" framing is
a workhorse across sequence DP:
[Maximum Product Subarray / 152](../0152-maximum-product-subarray/),
[Longest Common Subsequence / 1143](../1143-longest-common-subsequence/). Whenever
"can end anywhere" makes a subproblem fuzzy, pin the ending down first.
