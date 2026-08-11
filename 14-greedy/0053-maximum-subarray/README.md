# 53. Maximum Subarray

**Pattern:** Greedy (Kadane's — carry the best run ending right here)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/maximum-subarray/

## The problem in plain words

You have a row of numbers, some positive, some negative. Pick a run of them that
sits next to each other — no skipping around — with at least one number in it, so
the run adds up to as much as possible. Return that best sum.

```diagram
   index:   0    1    2    3    4    5    6    7    8
   nums:  [-2 ,  1 , -3 ,  4 , -1 ,  2 ,  1 , -5 ,  4 ]
                             └──────────────┘
                             4 + -1 + 2 + 1 = 6   <- best run, sum 6
```

## Why this matters

Strip the story away and one shape is left: sweep a stream of values once and keep
a **running best** that needs only the current number plus one carried number. You
never store the past or rescan it. You answer "best run ending here?" as you go.

That is the core of *online* processing — data arrives and you cannot rewind it.
Trading code uses this to find the most profitable buy/sell stretch or the worst
drawdown. Sensor pipelines find the strongest burst in a noisy signal. Genomics
scans DNA for the highest-scoring contiguous segment. Anywhere you watch a live
metric and want the peak sustained stretch, this is the shape.

What you buy is one linear pass and constant memory instead of re-summing every
possible window. As the input grows, that is the line between a program that
answers and one that crawls.

## Start from the obvious

A run is fixed by where it starts and where it ends, so try all of them. For each
start, extend the end and keep the running total:

```
best = nums[0]
for each start i:
    running = 0
    for each end j >= i:
        running += nums[j]
        best = max(best, running)
```

That is about n × n steps — double the input and the work roughly quadruples. It
is correct, and it is the honest first move. But look at what it keeps repeating.

## Find the waste

For start `i` you add up `nums[i..j]`. Then for start `i+1` you add up
`nums[i+1..j]` from scratch, re-touching almost the same numbers.

```diagram
   start 0: 2 + 7 + 11 + 15 ...
   start 1:     7 + 11 + 15 ...      <- re-adds 7,11,15 you already summed
   start 2:         11 + 15 ...      <- re-adds 11,15 again
                    ^^^^^^^^ the same tails, summed over and over
```

The fix: stop thinking "for each start, scan forward." Sweep left to right **once**
and keep a single fact up to date.

## The insight

Ask a smaller question at each spot: *what is the best run that ends exactly here?*
Call it `cur`. Standing on number `x`, a run ending at `x` is either

- `x` alone, or
- `x` glued onto the best run that ended at the number just before it.

So `cur = max(x, cur + x)`. The answer to the whole problem is the largest `cur`
you ever see, because the best run has to end *somewhere*, and you check every
somewhere.

```diagram
   nums:  [-2 ,  1 , -3 ,  4 , -1 ,  2 ,  1 , -5 ,  4 ]

   x=-2   cur = -2                       best = -2
   x= 1   cur = max(1, -2+1)= 1          best =  1   <- drop the -2, it only hurts
   x=-3   cur = max(-3, 1-3)= -2         best =  1
   x= 4   cur = max(4, -2+4)= 4          best =  4   <- fresh start beats carrying -2
   x=-1   cur = max(-1, 4-1)= 3          best =  4
   x= 2   cur = max(2, 3+2)= 5           best =  5
   x= 1   cur = max(1, 5+1)= 6           best =  6   <- high-water mark
   x=-5   cur = max(-5, 6-5)= 1          best =  6
   x= 4   cur = max(4, 1+4)= 5           best =  6
                                         answer = 6
```

**Why is the greedy choice safe?** The only decision at `x` is: extend the previous
run, or restart at `x`. Extend only when the previous sum `cur` is positive, because
then it *adds* to `x`. If `cur` is negative, carrying it forward only shrinks every
future sum, so dropping it is never worse. `max(x, cur + x)` encodes exactly that:
when `cur < 0`, `x` wins; when `cur >= 0`, extending wins. Hauling a negative prefix
along never helps, so discarding it loses nothing.

If you never reset — if you just kept accumulating — one bad early stretch would
poison every later sum, and you would report less than the real best. Resetting at
the right moment is the whole idea.

## Complexity

- **Time: about n steps.** One pass, constant work per number.
- **Extra memory: about a fixed amount.** Two running numbers, `cur` and `best`.
  Nothing that grows with the input.

## Pitfalls

- **Seeding `best` at 0.** If every number is negative (`[-3, -1, -2]`), the answer
  is `-1`, not `0` — you must take at least one number. Seed both `cur` and `best`
  from `nums[0]`.
- **Confusing `cur` and `best`.** `cur` is "best ending here" and can dip; `best` is
  the high-water mark and never drops. You need both.
- **Allowing an empty run.** The run must have length at least 1. Seeding from
  `nums[0]` and looping over the rest guarantees at least one number is used.
- **Reaching for divide-and-conquer.** There is a clever split solution, but this
  one-pass version is simpler and faster. Do not over-build.

## Transfer

The reusable move is **"best-ending-here": carry one rolling quantity that answers a
per-position subproblem, and throw it away the moment it turns into deadweight.**
Siblings:
[Maximum Product Subarray / 152](https://leetcode.com/problems/maximum-product-subarray/)
(same shape, but track best *and* worst, since a negative flips them),
[Best Time to Buy and Sell Stock / 121](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/)
(track the running minimum instead of a running sum),
[Maximum Circular Subarray / 918](https://leetcode.com/problems/maximum-sum-circular-subarray/).
Whenever the answer is "best contiguous window," ask "what's the best one ending
right here?" first.
