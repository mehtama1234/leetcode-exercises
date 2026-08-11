# 152. Maximum Product Subarray

**Pattern:** Dynamic programming (carry the best *and* the worst as you walk)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/maximum-product-subarray/

## The problem in plain words

Look at every run of numbers that sit next to each other. Multiply each run out.
Return the biggest product any run can make. The list can hold negatives and
zeros, which is the whole difficulty.

```diagram
   nums:  [ 2 ,  3 , -2 ,  4 ]

   runs and their products:
     [2]        = 2
     [2,3]      = 6      <- biggest
     [2,3,-2]   = -12
     [3]        = 3
     [-2,4]     = -8
     ...
   answer = 6
```

## Why this matters

The one idea to take away: **when a future step can rescue a value you'd call
bad right now, carry that bad value too.** A negative times another negative is
a big positive. So the smallest (most negative) product you've built could turn
into the largest the moment the next negative arrives. Track one number and you
lose it; track both extremes and you keep it.

That same move shows up when you compute a running gain over a window and a later
multiplier can flip which streak is winning, or in any one-pass total over a
stream you can't rewind where the combine step isn't well-behaved. The lesson is
to keep the states that *could* win, not only the state winning today.

## Start from the obvious

The problem talks about runs, so try every run and multiply it out.

```
best = nums[0]
for i in range(n):
    prod = 1
    for j in range(i, n):     # extend the run one step at a time
        prod *= nums[j]
        best = max(best, prod)
```

This is correct. But watch the work: for every start `i` you sweep the rest of
the list again, re-multiplying the same overlapping prefixes. On a list of length
n that is about n × n steps. Double the input and the work roughly quadruples.
The repeated sweeping is the waste. We want one pass.

## Find the waste

The one-pass instinct is to carry "best product ending right here" and extend it
by one number at a time. For sums that works cleanly. Products have a trap:

> a negative number flips sign, so the *smallest* running product can suddenly
> become the *largest* when the next negative shows up.

Watch it fail if you carry only the running max on `[-2, 3, -4]`:

```diagram
   carry only the max ("best ending here"):

   x = -2   best_here = -2
   x =  3   best_here = max(3, -2*3=-6) = 3     <- we threw away -6
   x = -4   best_here = max(-4, 3*-4=-12) = -4

   reported: -2     TRUE answer: 24  =  (-2)*3*(-4)
                    the -6 we discarded was the seed of the win
```

The `-6` looked like the worst thing on the board, so a max-only walk drops it.
But `-6 * -4 = 24`. The worst became the best.

## The insight

Carry **two** running values at each index: the largest product ending here and
the smallest (most negative) product ending here. When a new number `x` arrives,
the best run ending at `x` is one of three things:

- `x` alone — start fresh (this is how a zero resets everything),
- `cur_max * x` — extend the current best run,
- `cur_min * x` — extend the current worst run, which if `x < 0` may now be best.

Compute all three from the *same* old pair, then set `cur_max` to the biggest and
`cur_min` to the smallest. Keep a global `best`.

```diagram
   nums = [-2, 3, -4]        best starts at -2, cur_max=-2, cur_min=-2

   x = 3:
     candidates = ( 3 ,  cur_max*3 = -6 ,  cur_min*3 = -6 )
                    ^new     ^from -2         ^from -2
     cur_max = max = 3      cur_min = min = -6      best = 3

   x = -4:
     candidates = ( -4 ,  cur_max*-4 = -12 ,  cur_min*-4 = 24 )
                     ^new     ^from 3            ^from -6  --> RESCUED
     cur_max = max = 24     cur_min = min = -12     best = 24
```

Because a negative `x` swaps which of max/min is larger, carrying the min is the
whole reason this is correct. You spent one extra tracked number to keep the
one-pass speed.

## Complexity

- **Brute force:** about n × n steps, `O(1)` extra memory.
- **Rolling min/max:** about n steps — one pass — and `O(1)` extra memory (two
  carried numbers).

## Pitfalls

- Tracking only the running max and dropping the min. This is *the* mistake, and
  it fails any time two negatives should combine.
- Computing `cur_max` first and then feeding the *updated* `cur_max` into the
  `cur_min` line. Read all three candidates from the same old pair before you
  assign either.
- Zeros: keeping `x` alone as a candidate lets the run restart after a zero. A
  zero makes all three candidates involve 0, and the next element starts fresh.
- Starting `best` at `0` or `1`. Start it at `nums[0]` so all-negative lists and
  single-element lists come out right.

## Transfer

This is [Maximum Subarray / 53](https://leetcode.com/problems/maximum-subarray/)
(carry the best sum ending here) with one twist: because multiply can flip sign,
you carry both extremes instead of one. The framing "pin the subproblem to the
element it ends at" also drives
[Longest Increasing Subsequence / 300](../0300-longest-increasing-subsequence/).
Whenever a future step can rescue a currently-bad running value, track every
state that could become best — not only the current best.
