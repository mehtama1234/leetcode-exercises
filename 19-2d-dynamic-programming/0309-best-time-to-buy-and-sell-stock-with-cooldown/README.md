# 309. Best Time to Buy and Sell Stock with Cooldown

**Pattern:** 2-D dynamic programming (state machine over time)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-cooldown/

## The problem in plain words

You have a list of daily stock prices. You can buy and sell as many times as you
want, but the day after you sell you must sit out — no buying. You can't hold two
shares at once. Find the most profit you can make.

```diagram
   prices = [1, 2, 3, 0, 2]

   day:      0  1  2  3  4
   price:    1  2  3  0  2
   action:  buy    sell  X  buy sell   (X = forced cooldown after selling)
            -1     +3          -0  +2
   profit = (3 - 1) + (2 - 0) = 3
```

## Why this matters

The clean way to think about this isn't "when do I trade?" — it's "what situation am
I in at the end of each day?" There are only a few situations: holding a share, just
sold today, or free and idle. Each day you move between them by a fixed set of legal
moves. That reframing — a small set of states, a fixed set of transitions, march
forward one day at a time — is a *state machine*, and it makes the cooldown rule
almost disappear: it's just one missing arrow between states.

State machines like this run trading logic, game AI, network protocols, and UI flows
— anywhere the future depends only on which state you're in now, not the whole
history of how you got there.

## Start from the obvious

Track two things per day: the day number, and whether you currently hold a share.
From "not holding" you may rest or buy. From "holding" you may rest or sell — and
selling jumps you two days forward, because the day after is a forced cooldown. Take
the best over the choices.

```diagram
   best(day, holding):
      not holding -> rest to (day+1, no)   OR   buy to (day+1, yes),  pay price
      holding     -> rest to (day+1, yes)  OR   sell to (day+2, no),  gain price
                                                       ^^^^^ skips cooldown day
```

That's a grid of states — one row per day, two columns (holding / not) — but written
as plain recursion it re-solves the same `(day, holding)` pairs, so cache them.

## The insight — three end-of-day states

Sharpen "not holding" into two cases, because the cooldown depends on *why* you're
idle. End each day in one of three states:

- **hold** — you own a share.
- **sold** — you sold *today* (so tomorrow is a forced rest).
- **rest** — you own nothing and are free to buy (not fresh off a sale).

Draw the day-by-day grid of best profit reachable in each state:

```diagram
   prices = [1, 2, 3, 0, 2]

   day:       start   1     2     3     0     2
   hold  |    -inf   -1    -1    -1     0     0
   sold  |     0      0     1     2    -1     2
   rest  |     0      0     0     1     2     2
                                              ^ answer = max(sold, rest) = 2
```

Now fill one column (one day, price `p`) from the previous column's three cells:

```diagram
   moving from yesterday to today, price = p

   yesterday:   hold      sold      rest
                  \  \      |         / |
                   \  \     |        /  |
   today:  hold' = max(hold, rest - p)     keep holding, or buy from a free day
           sold' = hold + p                sell the share you held
           rest' = max(rest, sold)         stay free, or the cooldown just ended

   the cooldown is the WALL between sold and rest: the only door to a fresh
   buy is through rest, and you only enter rest the day AFTER a sale.
```

Since today's numbers depend only on yesterday's three, you don't need the grid at
all — carry three running values and update them each day. That's the O(1)-space
version in `solution.py`. The answer never ends in *hold* (a share you're still
holding is unsold profit), so it's `max(sold, rest)`.

## Complexity

- **Time: about n steps** — one pass over the prices, a few comparisons per day.
- **Extra memory: constant** — three running numbers. (The memoized version uses
  about n for its cache.)

## Pitfalls

- Collapsing "idle" into one state. You need *sold* and *rest* separate, or the
  cooldown wall vanishes and you'll let a buy happen the day after a sale.
- Updating the three values out of order and reading a value already overwritten.
  Stash yesterday's `sold` before recomputing (see `prev_sold` in the code).
- Ending in *hold*. A share you never sold isn't profit — answer over `sold`/`rest`.

## Transfer

The reusable pattern is *DP as a state machine: enumerate a handful of states, write
each legal transition, take the max, then roll the table to scalars.* Siblings:
[Best Time to Buy and Sell Stock II / 122](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-ii/)
(no cooldown, greedy collapses it),
[with Transaction Fee / 714](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-transaction-fee/)
(same machine, a fee on the sell edge), and
[III / 123](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iii/)
(add a "transactions used" dimension).
