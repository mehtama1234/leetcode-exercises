# 238. Product of Array Except Self

**Pattern:** Prefix / suffix products (build running results from each side once)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/product-of-array-except-self/

## The problem in plain words

Build a new array where each slot holds the product of *all the other* numbers —
everything except the one sitting at that slot. Two hard rules: no division, and
it has to run in about n steps.

```diagram
   nums   = [ 1,  2,  3,  4 ]

   answer[0] = 2*3*4 = 24
   answer[1] = 1*3*4 = 12
   answer[2] = 1*2*4 = 8
   answer[3] = 1*2*3 = 6
   answer  = [24, 12,  8,  6]
```

## Why this matters

The move is to *precompute running results from each side*, so each position's
answer is "everything before it" times "everything after it" — looked up in one
step, not recomputed from scratch. That's prefix/suffix accumulation.

It's a workhorse in real systems. Databases and analytics engines keep running
totals (prefix sums), so a range question — revenue from March to June, rows
between two offsets — is one subtraction instead of a re-scan. The 2D version
(summed-area tables) powers fast blur and feature detection in computer vision.
Cumulative distributions in statistics, and weighted random sampling, are the
same precomputed running totals.

What you're solving for is turning a per-slot re-multiply into one lookup by
paying once up front — and dodging division, which breaks on zeros and loses
precision. Two straight passes and a couple of scalars replace the n × n brute
force.

## Start from the obvious

Definition straight to code: for each position `i`, multiply together every
element except `nums[i]`.

```diagram
   for i=2:  skip nums[2],  multiply the rest
             1 * 2 * _ * 4  = 8
             ^ every answer re-multiplies almost the whole array
```

That's about n × n: each of the n answers re-multiplies nearly the whole array.
And the tempting shortcut — multiply everything once, then divide by `nums[i]` —
is banned (and blows up on zeros anyway).

## Find the waste

The brute force recomputes overlapping products constantly. `answer[2]` and
`answer[3]` multiply almost the same numbers; nothing carries over.

Look at what "product of all except `i`" really is. It's every element to the
**left** of `i`, times every element to the **right** of `i`.

```diagram
   answer[i] = (nums[0]*...*nums[i-1]) * (nums[i+1]*...*nums[n-1])
                \___ left of i ______/   \____ right of i _______/

   neither half contains nums[i]  ->  no division ever needed
```

And those left products build up smoothly: the left product for `i` is the left
product for `i-1` times `nums[i-1]`. Same for the right side going backward.
That's the reuse the brute force threw away.

## The insight

Two sweeps, using the output array itself as scratch.

1. **Left to right.** Carry a running `prefix` (product of everything to the left,
   not including the current element). Store it in `answer[i]`, then fold
   `nums[i]` into `prefix`.
2. **Right to left.** Carry a running `suffix` the same way, and *multiply* it
   into each `answer[i]`. After this pass `answer[i]` holds left × right.

```diagram
   nums = [1, 2, 3, 4]

   pass 1 (prefix, left products):
      answer = [1,  1,  2,  6]     (1, 1, 1*2, 1*2*3)

   pass 2 (suffix, right products, multiplied in):
      suffix walks 1, 4, 12, 24 from the right
      answer = [1*24, 1*12, 2*4, 6*1]
             = [ 24,   12,   8,   6 ]
```

## Complexity

- **Time: about n steps.** Two straight passes.
- **Extra memory: a fixed small amount.** Only the two running values `prefix`
  and `suffix`; the required output array doesn't count against the space bound.

## Pitfalls

- **Zeros** are why division is banned, and this method sidesteps them: one zero
  makes every answer zero *except* at the zero's own slot (its left × right leaves
  the zero out); two or more zeros make everything zero. Both fall out for free.
- Start `answer` at `1`s and seed `prefix`/`suffix` at `1` — one is the "does
  nothing" value for multiplication.
- Watch the second loop's direction (`n-1` down to `0`) and remember it
  *multiplies into* `answer`, it doesn't overwrite.
- Negative numbers just flow through the products; no special handling.

## Transfer

The reusable idea is **prefix/suffix accumulation**: precompute running results
from one side (and sometimes the other) so each position's answer is one lookup.
The same shape solves running-total and range-sum questions, "trapping rain
water" (tallest bar to the left and right of each spot), and any "combine
everything on one side with everything on the other" task. It's the
multiplication cousin of the running-sum pattern.
