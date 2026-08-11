# 309. Best Time to Buy and Sell Stock with Cooldown

**Pattern:** 2-D dynamic programming (state machine over time)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-cooldown/

## The problem in plain words

Prices for a stock, one per day. You can buy and sell any number of times but hold
at most one share, and after you **sell** you must wait one day before buying
again. Find the largest total profit.

## Why this matters

The real skill here is *modeling a decision process as a small set of states with
rules for moving between them, then finding the best path through time.* The stock
is a prop — what you're building is a finite state machine (hold / just-sold /
free) and letting DP pick the highest-value walk. The cooldown is a constraint on
which transitions are legal, and encoding a rule as "you can only reach this state
through that state" is the transferable trick.

That modeling shows up any time an action forces a temporary lockout: a rate
limiter that blocks the next request after one fires, a machine that needs a
cool-off between jobs, a retry policy with a mandatory backoff, an ad system that
can't re-show a creative for N slots. Each is "take an action, then you're barred
from a class of actions for a window."

What the good solution buys is `O(n)` time and — after rolling the table — `O(1)`
memory: you decide the entire trading strategy in a single pass with three running
numbers, no lookahead, no re-simulating.

## Start from the obvious

The only things that matter on a given day are the day itself and whether you hold
a share. Recurse on `(day, holding)`:

```
def best(day, holding):
    if day >= n: return 0
    rest = best(day+1, holding)              # do nothing
    if holding: return max(rest, prices[day] + best(day+2, False))  # sell, then cooldown
    else:       return max(rest, -prices[day] + best(day+1, True))  # buy
```

The cooldown is simply the `day+2` on the sell branch — selling skips the very
next day. Without memoization this branches exponentially.

## Find the waste

There are only `2n` distinct `(day, holding)` states, but the raw recursion revisits
them through countless different action histories. Cache on `(day, holding)` and it's
`O(n)`. That's already an accepted solution.

## The insight

Read it bottom-up and name the states after each day:

- **hold** — best profit while holding a share.
- **sold** — best profit having sold *today* (tomorrow is a forced cooldown).
- **rest** — best profit holding nothing and free to buy.

```
sold' = hold + p               # sell today
hold' = max(hold, rest - p)    # keep holding, or buy today from a free day
rest' = max(rest, sold)        # stay free, or yesterday's sale's cooldown is over
```

The cooldown is enforced structurally: a fresh **buy** is only reachable from
**rest**, and you only *enter* **rest** the day after being in **sold**. So there is
no way to buy on the day right after selling — the wall between `sold` and `rest`
is the one-day wait. Three scalars replace the whole table.

## Complexity

- **Time:** `O(n)` — one pass, constant work per day.
- **Space:** `O(1)` for the rolled version (`O(n)` for the plain memo). Only the
  previous day's three numbers are needed.

## Pitfalls

- Ordering the three updates wrong within a day: compute `sold` from the *old*
  `hold`, and `rest` from the *old* `sold` (stash `prev_sold` first), or you'll
  let a sale and a re-buy happen on the same day.
- Initializing `hold = 0`: before any day you cannot be holding, so it must be
  `-inf`.
- Forgetting the answer is `max(sold, rest)` — ending while still holding a share
  is never optimal (you'd have unrealized cost, not profit).
- Empty price list should return 0.

## Transfer

The reusable pattern is *DP as a state machine: enumerate a handful of states, write
each legal transition, take the max, then roll the table to scalars.* Siblings:
[Best Time to Buy and Sell Stock II / 122](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-ii/)
(no cooldown, greedy collapses it),
[with Transaction Fee / 714](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-transaction-fee/)
(same machine, a fee on the sell edge), and
[III / 123](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iii/)
(add a "transactions used" dimension).
