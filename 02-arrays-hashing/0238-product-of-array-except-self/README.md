# 238. Product of Array Except Self

**Pattern:** Prefix / suffix products (precomputed accumulation)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/product-of-array-except-self/

## The problem in plain words

Build a new array where each slot holds the product of *all the other* numbers —
everything except the one sitting at that slot. Two hard rules: no division, and
it must run in `O(n)`.

## Why this matters

The fundamental move is *precompute running results from each side so every
position's answer combines "everything before" with "everything after" in O(1),
instead of recomputing overlapping work.* That's prefix/suffix accumulation.

It's a workhorse in real systems. Databases and analytics engines keep prefix
sums (cumulative totals) so a range query — revenue from March to June, rows
between two offsets — is one subtraction instead of a re-scan. Summed-area tables
(integral images) do the 2D version and power fast box blur and feature detection
in computer vision. Cumulative distribution functions in statistics and
weighted random sampling are the same precomputed running totals.

What you're solving for is turning a per-query O(n) recompute into O(1) by paying
once up front, and here also dodging division — which matters because division
breaks on zeros and loses precision. Two linear passes and O(1) extra space
replace the O(n^2) brute force.

## Start from the obvious

Definition straight to code: for each position `i`, multiply together every
element except `nums[i]`.

```
for each i:
    answer[i] = product of nums[j] for all j != i
```

That's `O(n^2)`: every one of the `n` answers re-multiplies almost the whole
array. And the tempting `O(n)` shortcut — multiply everything once, then divide
by `nums[i]` — is banned (and blows up on zeros anyway).

## Find the waste

The brute force recomputes overlapping products constantly. `answer[2]` and
`answer[3]` both multiply almost the same set of numbers; nothing is reused.

Look at what "product of all except `i`" actually is. It's every element to the
**left** of `i`, times every element to the **right** of `i`:

```
answer[i] = (nums[0]*...*nums[i-1]) * (nums[i+1]*...*nums[n-1])
             \___ left of i ______/   \____ right of i _______/
```

Neither half contains `nums[i]` — so no division is ever needed. And those left
products build up smoothly: the left-product for `i` is just the left-product for
`i-1` times `nums[i-1]`. Same for the right side going backward. That's the reuse
the brute force threw away.

## The insight

Two sweeps, using the output array as scratch:

1. **Left to right.** Carry a running `prefix` (product of everything seen so
   far, not including the current element). Store it in `answer[i]`, then fold
   `nums[i]` into `prefix`.
2. **Right to left.** Carry a running `suffix` the same way, and *multiply* it
   into each `answer[i]`. After this pass `answer[i]` holds left × right.

```
prefix = 1
for i in 0..n-1: answer[i] = prefix; prefix *= nums[i]
suffix = 1
for i in n-1..0: answer[i] *= suffix; suffix *= nums[i]
```

## Complexity

- **Time:** `O(n)` — two linear passes.
- **Space:** `O(1)` extra — only the two scalars `prefix` and `suffix`; the
  required output array doesn't count against the space bound.

## Pitfalls

- **Zeros** are the reason division is banned. This method sidesteps them: one
  zero makes every answer zero *except* at the zero's own index (its left×right
  excludes it); two or more zeros make everything zero. The passes handle both
  for free.
- Initialize `answer` to `1`s and seed `prefix`/`suffix` at `1` — the identity
  for multiplication.
- Watch the direction of the second loop (`n-1` down to `0`) and remember it
  *multiplies into* `answer`, it doesn't overwrite.
- Negative numbers just flow through the products; no special handling.

## Transfer

The reusable idea is **prefix/suffix accumulation**: precompute running results
from one side (and sometimes the other) so each position's answer is `O(1)`. The
same shape solves running-sum / range-sum queries, "trapping rain water" (max to
the left and right of each bar), and any "combine everything on one side with
everything on the other" task. It's the multiplicative cousin of the prefix-sum
pattern.
