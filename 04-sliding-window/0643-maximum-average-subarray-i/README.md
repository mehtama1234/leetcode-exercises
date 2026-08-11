# 643. Maximum Average Subarray I

**Pattern:** Sliding window (fixed size — keep a running total, add one and drop one)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/maximum-average-subarray-i/

## The problem in plain words

You get a list of numbers and a size `k`. Look at every block of `k`
numbers-in-a-row and find the block with the biggest average. Give back that
average.

One thing to notice before you write anything: every block has the *same* length
`k`, so dividing by `k` never changes which block wins. Biggest average is the
same as biggest sum. So you only ever compare sums, and divide once at the very
end.

```diagram
   nums:  [ 1 , 12 , -5 , -6 , 50 ,  3 ]      k = 4

   block at 0:  [ 1  12  -5  -6 ]              sum = 2
   block at 1:      [ 12  -5  -6  50 ]         sum = 51   <- winner
   block at 2:          [ -5  -6  50   3 ]     sum = 42

   answer = 51 / 4 = 12.75
```

## Why this matters

Strip the story away and the job is: **compute a summary over every block of a
fixed width, without redoing the whole block each time.** The reusable move is the
*add-one, drop-one* update. As the block slides one step right, exactly one number
walks in on the right and exactly one walks out on the left. Everything in between
is shared, so touching it again is wasted work.

That move is how real systems compute windowed numbers over a stream. A moving
average of stock prices or sensor readings is a rolling sum, not a re-sum.
Requests-per-last-`k`-seconds for a rate limiter is kept the same way, bumped as
events tick by. Box filters and running loudness in audio are the same slide over
a sample feed.

What the good version buys you is per-block work that stays constant instead of
growing with `k`. For a long feed or a wide window that is the line between a
computation that keeps up in real time and one that falls behind.

## Start from the obvious

The definition hands you an algorithm: for each starting spot, add up the `k`
numbers there, and remember the best sum.

```
best = -infinity
for each start i:
    s = sum(nums[i .. i+k-1])
    best = max(best, s)
return best / k
```

There are about `n` blocks and each one costs `k` additions, so this is about
`n × k` steps. It's correct, and it's the honest first thought. Now look at *why*
it's slow.

## Find the waste

Put two neighboring blocks on top of each other and watch what actually changes.

```diagram
   nums:  [ 1 , 12 , -5 , -6 , 50 ,  3 ]      k = 4

   block A:  [ 1  12  -5  -6 ]                 sum = 2
   block B:      [ 12  -5  -6  50 ]

              shared:  12  -5  -6   (k-1 = 3 numbers, added TWICE)
              leaves:   1           (the old left edge)
              enters:  50           (the new right edge)
```

Blocks A and B share `k-1` of their `k` numbers. The slow version re-adds those
shared numbers from scratch every single step. The only *real* change from A to B
is that `1` leaves on the left and `50` joins on the right. That re-adding of the
shared middle is the waste.

## The insight

Keep a **running sum** of the current block. To slide one step right, don't re-add
anything — add the number entering on the right and subtract the number leaving on
the left.

```diagram
   k = 4        running sum carried across the slide

   start:  sum = 1 + 12 + (-5) + (-6) = 2        best = 2

   slide:  sum = 2  + 50  -  1  = 51             best = 51
                     ^in    ^out
   slide:  sum = 51 +  3  - 12  = 42             best = 51

   answer = best / k = 51 / 4 = 12.75
```

Each number is added exactly once and subtracted at most once over the whole scan,
so the total work is about `n` steps — one pass, not `n × k`.

## Complexity

- **Time: about n steps.** One pass; each slide is two arithmetic operations.
- **Extra memory: constant.** Only the running sum and the best-so-far.

## Pitfalls

- Re-summing the whole block each step — the accidental `n × k` trap the running
  sum exists to remove.
- Returning the **sum** instead of the average. Divide by `k` once at the end.
- Integer division: divide by `float(k)` (or use `/` in Python 3), or you'll floor
  the answer.
- Starting `best` at `0` instead of `-infinity` (or the first block's sum). An
  all-negative array would wrongly report `0`.
- Comparing averages with `==` in tests — they're floating point, so compare
  within a tiny tolerance.

## Transfer

The reusable move is: **carry a running total and update it as the window slides —
one in, one out.** That's the whole fixed-size sliding-window pattern. It shows up
anywhere you're asked about every block of a set length: maximum sum of `k`
consecutive numbers, counting vowels or distinct values in each window, moving
averages over a stream. Whenever a slow solution re-scans overlapping blocks, reach
for add-one / drop-one first.
