# 121. Best Time to Buy and Sell Stock

**Pattern:** Sliding window / running minimum
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/best-time-to-buy-and-sell-stock/

## The problem in plain words

You're given a price for each day. Pick one day to buy and a **later** day to
sell. What's the most profit you can make? If prices only ever fall, you simply
don't trade, and the answer is `0`.

The "buy before you sell" rule is the whole game: it means for any sell day, the
buy day has to come from the days *before* it.

## Why this matters

Underneath the trading story this is the **best-gap-where-one-point-must-precede-the-other** problem, solved by carrying a **running minimum of the prefix**. The fundamental operation is: compress everything you've seen so far into one summary number (the cheapest price yet), and answer each new position against it in constant time — no re-scanning the past.

This running-extremum-over-a-stream move is everywhere in real monitoring and analytics:

- **Metrics and alerting** — largest drawdown or peak-to-trough drop, computed online as data arrives.
- **Streaming aggregates** — running min/max/best-so-far over sensor, price, or latency feeds where you can't store or re-read history.
- **Signal processing** — maximum rise between a valley and a later peak in a time series.

What we're solving for is **one pass and constant memory over data you may only see once**: brute force re-searches the whole prefix for the cheapest earlier point (`O(n^2)`), while a single carried minimum collapses that history to `O(1)` state and `O(n)` time — the right shape for a live stream, not just an array.

## Start from the obvious

Try every valid pair — every buy day with every later sell day — and keep the
best difference.

```
best = 0
for buy i:
    for sell j after i:
        best = max(best, prices[j] - prices[i])
return best
```

That's `O(n^2)`. It's correct, and it's the honest first thought. Now stare at
what it wastes.

## Find the waste

Fix a sell day `j`. The inner loop is really asking one thing: *what is the
cheapest price on any day before `j`?* Because to maximize `prices[j] - buy`, you
want the smallest possible `buy`. The brute force re-discovers that cheapest
earlier price from scratch for every `j` — but as you move day by day, the
"cheapest so far" only ever gets updated, never recomputed.

## The insight

Walk left to right, carrying one number: `min_price`, the lowest price seen so
far. On each day:

1. If today is cheaper than anything before, update `min_price` (a better day to
   have bought).
2. Otherwise, pretend you sell today: `profit = price - min_price`, and keep the
   best.

```
min_price = +infinity
best = 0
for price in prices:
    if price < min_price: min_price = price
    else:                 best = max(best, price - min_price)
return best
```

The past is compressed into a single number — the best buy price so far — so one
pass is enough.

## Complexity

- **Time:** `O(n)` — one pass, constant work per day.
- **Space:** `O(1)` — just `min_price` and `best`.

The brute force is `O(n^2)`; the trick is realizing the entire history you need is
one running minimum.

## Pitfalls

- Selling **before** buying — the "later day" rule is easy to drop; tracking a
  *running* minimum enforces it automatically.
- Returning `0` when a real profit exists because you started `best` too high, or
  a negative number when no trade is profitable (clamp at `0`).
- Confusing this with "max difference between any two elements" — order matters
  here; the smaller value must come first.
- Empty or single-day input: profit is `0` (you can't buy and sell).

## Transfer

This is the running-extremum idea: sweep once, keep the best "so far" value you
need, and answer each new position against it. The same shape solves
[Maximum Subarray / 53](../../02-arrays-hashing/) (running best-ending-here),
maximum profit variants, and any "best pair where one index must precede the
other" question. Whenever a brute force re-searches the prefix for a min or max,
carry it as you go instead.
