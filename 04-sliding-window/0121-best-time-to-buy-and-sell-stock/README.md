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
