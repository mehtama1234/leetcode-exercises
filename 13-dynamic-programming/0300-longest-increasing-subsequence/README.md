# 300. Longest Increasing Subsequence

**Pattern:** Dynamic programming (subsequence ending at index) → patience sorting
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/longest-increasing-subsequence/

## The problem in plain words

You have a list of numbers. Walk through it left to right, picking some of the
numbers (you may skip any) so that each one you pick is strictly larger than the
one you picked before. How long can you make that chain? Return only its length.

The subsequence doesn't have to be contiguous — `[10, 9, 2, 5, 3, 7, 101, 18]`
contains `[2, 3, 7, 101]`, so the answer is `4`.

## Start from the obvious

A subsequence is "pick or skip each element", so the honest brute force is: try
every subset, keep the ones that are increasing, return the longest.

```
for every subset of nums:
    if subset is strictly increasing:
        track the max length
```

That's `2^n` subsets — hopeless past ~20 elements. But it tells us the shape of
the answer: the chain is built one element at a time, and each element we add
must beat the previous one.

## Find the waste

The real question at any point is "what's the longest increasing chain I can
build?" The trouble is a chain can end anywhere, so let's pin down the ending.

Define `dp[i]` = the length of the longest increasing subsequence that **ends at
index `i`**. Fixing the last element is the move that unlocks everything: if the
chain ends at `i`, the element right before it must be some earlier `nums[j]`
with `nums[j] < nums[i]`. So:

```
dp[i] = 1 + max(dp[j] for all j < i where nums[j] < nums[i])
      = 1        if no such j exists
```

Compute `dp` left to right and every `dp[j]` you look back at is already final.
The answer is `max(dp)`, because the longest chain can end at any index.

That's `O(n^2)`: for each `i` we scan all earlier `j`.

## The insight (getting to O(n log n))

The `O(n^2)` version re-scans every predecessor for each element. What are we
actually looking for in that scan? The best chain we can *extend*. And to extend
chains, the only thing that matters about a chain of a given length is its
**smallest possible tail** — a smaller tail can be extended by more future values.

So keep an array `tails`, where `tails[k]` is the smallest value that can end an
increasing subsequence of length `k + 1`. For each new number `x`:

```
find the leftmost tail >= x       (binary search — tails stays sorted)
if there is none:  x extends the longest chain so far   -> append x
else:              x is a smaller tail for that length   -> overwrite it
```

Overwriting never hurts a future answer (a smaller tail is strictly more useful),
and appending only happens when `x` genuinely lengthens the record. The length of
`tails` at the end is the LIS length. Because `tails` is always sorted, each step
is a binary search — `O(n log n)` overall.

One honest caveat: `tails` is **not** itself a valid subsequence you can read off.
Only its *length* is meaningful. (Reconstructing the actual subsequence needs a
parent-pointer array on top.)

## Complexity

- **Brute force:** `O(2^n)` time.
- **DP:** `O(n^2)` time, `O(n)` space.
- **Patience sorting:** `O(n log n)` time, `O(n)` space.

## Pitfalls

- **Strictly** increasing: use `bisect_left` (leftmost `>= x`), which overwrites
  on ties so equal values can't both count. If the problem said non-decreasing,
  you'd use `bisect_right`.
- Empty input must return `0`; don't call `max()` on an empty `dp`.
- Thinking `tails` is the actual subsequence — it isn't. Its length is correct;
  its contents are a jumble.

## Transfer

The "smallest tail per length + binary search" trick generalizes to problems like
[Russian Doll Envelopes / 354](https://leetcode.com/problems/russian-doll-envelopes/)
(2-D LIS after sorting). The `dp[i]` = "best answer ending at index i" framing is a
workhorse across sequence DP:
[Maximum Product Subarray / 152](../0152-maximum-product-subarray/),
[Longest Common Subsequence / 1143](../1143-longest-common-subsequence/). Whenever
"can end anywhere" makes a subproblem fuzzy, pin the ending down first.
