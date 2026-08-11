# 518. Coin Change II

**Pattern:** 2-D dynamic programming (unbounded knapsack — counting)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/coin-change-ii/

## The problem in plain words

You have coin values and a target amount. Count how many different *combinations* of
coins add up to the amount. Order doesn't matter — 1+2 and 2+1 are the same
combination — and you can use each coin as many times as you like.

```diagram
   amount = 5     coins = [1, 2, 5]

   5           1+1+1+1+1
   2+1+1+1     2+2+1     5

   -> 4 combinations
```

## Why this matters

The subtle part is *combinations, not orderings*. The natural recursion, "at each
step pick any coin," would count 1+2 and 2+1 as two — wrong. The fix is to pin an
order: decide coins in a fixed sequence and never go back to an earlier coin. Once
you've moved past the 1-coins, you never add another 1. That single rule turns an
overcount into an exact count.

Controlling for order by processing items in a fixed sequence is the standard cure
for double-counting in any counting-by-choices problem. And "each item available in
unlimited quantity, fill a capacity" is the unbounded-knapsack shape that shows up
in change-making, cutting problems, and resource packing.

## Start from the obvious

Build a grid `dp[i][a]` = number of ways to make amount `a` using only the first `i`
coin types. Two moves for coin `i`: **skip** it (use only earlier coins for amount
`a`) or **take one more** of it (subtract its value, but stay allowed to take it
again). Add the two counts.

```diagram
   coins = [1, 2, 5]  (rows added one at a time)   amount across

              a:  0    1    2    3    4    5
        {}       | 1 |  0 |  0 |  0 |  0 |  0 |   no coins: only amount 0 works
        +1       | 1 |  1 |  1 |  1 |  1 |  1 |   all 1's
        +2       | 1 |  1 |  2 |  2 |  3 |  3 |
        +5       | 1 |  1 |  2 |  2 |  3 |  4 |   <- answer at amount 5
```

Each new row is "everything the row above could do, plus the ways that use at least
one of the new coin."

## The insight

Look at how a single cell fills. It reads two places: the cell directly **above**
(ways that skip this coin) and the cell to its **left** by exactly the coin's value
in the *current* row (ways that use this coin at least once, then still need the
rest):

```diagram
   filling dp[coin][a], coin value = c

        above = dp[prev][a]        "don't use this coin"
             |
             v
        dp[coin][a] = above  +  dp[coin][a - c]
                                    ^
                        same row, c to the left
                        "use one of this coin, keep going"

   example: dp[+2][4] = dp[+1][4]  +  dp[+2][2]
                        = 1 (1+1+1+1) + 2 (2+2, 2+1+1) = 3
```

Reading `dp[coin][a-c]` from the *same* row (not the row above) is what allows
reusing a coin many times. Because each row only needs the row above and cells to
its own left, you can collapse the grid to a single array and add coins one at a
time, sweeping amount upward — that's the version in `solution.py`.

## Complexity

- **Time: about (number of coins) × amount steps.** One add per grid cell.
- **Extra memory: about amount** in the rolled 1-D version — one row across
  amounts. The full grid uses coins × amount.

## Pitfalls

- Looping amount on the outside and coins on the inside. That counts orderings, not
  combinations (it'd return the wrong, larger number). Coins outside, amount inside.
- Sweeping amount downward. Downward forbids reusing a coin — that's the *0/1*
  knapsack. For unlimited coins, sweep upward so the just-updated cell feeds itself.
- Forgetting `dp[0] = 1`: there is exactly one way to make amount 0 — take no coins.

## Transfer

The pattern is *unbounded knapsack, counting variant*: outer loop over items,
inner loop upward over capacity, accumulate. Siblings:
[Coin Change / 322](https://leetcode.com/problems/coin-change/) (minimize count
instead of counting ways), [Combination Sum IV / 377](https://leetcode.com/problems/combination-sum-iv/)
(count sequences), [Target Sum / 494](../0494-target-sum/) (counting variant that
reduces to a 0/1 subset-sum count).
