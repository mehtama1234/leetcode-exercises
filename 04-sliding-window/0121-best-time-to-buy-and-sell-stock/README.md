# 121. Best Time to Buy and Sell Stock

**Pattern:** Sliding window / running minimum (compress the past into one number)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/best-time-to-buy-and-sell-stock/

## The problem in plain words

You get a price for each day. Pick one day to buy and a **later** day to sell.
What's the most profit you can make? If prices only ever fall, you don't trade at
all and the answer is `0`.

The "buy before you sell" rule is the whole game. For any day you sell on, the buy
day has to come from the days *before* it.

```diagram
   day:     0    1    2    3    4    5
   price: [ 7 ,  1 ,  5 ,  3 ,  6 ,  4 ]

   buy on day 1 (price 1), sell on day 4 (price 6)
                 buy ^                ^ sell
   profit = 6 - 1 = 5    (best possible)
```

## Why this matters

Underneath the trading story the question is: **what's the best gap between two
points where one must come before the other?** The reusable move is to squeeze
everything you've seen so far into one summary number — the cheapest price yet —
and answer each new day against it in a single step. You never re-scan the past.

This "carry a running best over a stream" move is everywhere in monitoring and
analytics. The largest peak-to-trough drop of a metric is computed online as data
arrives. Running min, max, and best-so-far over a price, sensor, or latency feed
are kept the same way, on data you often can't store or re-read. The biggest rise
between a valley and a later peak in a time series is this exact shape.

What the good version buys you is one pass and constant memory over data you may
only see once. The slow version re-searches the whole past for the cheapest earlier
day; the running minimum collapses that history into a single number.

## Start from the obvious

Try every valid pair — every buy day with every later sell day — and keep the best
difference.

```
best = 0
for buy i:
    for sell j after i:
        best = max(best, prices[j] - prices[i])
return best
```

That's about `n × n` steps. It's correct and it's the honest first thought. Now
stare at what it wastes.

## Find the waste

Fix a sell day `j`. The inner loop is really asking one thing: *what is the
cheapest price on any day before `j`?* Because to make `prices[j] - buy` as large
as possible, you want the smallest `buy` you can find. The slow version re-discovers
that cheapest earlier price from scratch for every `j`.

```diagram
   price: [ 7 ,  1 ,  5 ,  3 ,  6 ,  4 ]

   sell on day 3 (price 3): rescans days 0..2 to find cheapest -> 1
   sell on day 4 (price 6): rescans days 0..3 to find cheapest -> 1  (again!)
   sell on day 5 (price 4): rescans days 0..4 to find cheapest -> 1  (again!)

   the "cheapest so far" only ever updates -- it never needs recomputing
```

As you walk day by day, the cheapest price so far only ever gets lower or stays
put. Recomputing it every time is the waste.

## The insight

Walk left to right carrying one number: `min_price`, the lowest price seen so far.
On each day, either this is a new cheapest day to have bought, or you pretend to
sell today against that minimum and keep the best profit.

```diagram
   price: [ 7 ,  1 ,  5 ,  3 ,  6 ,  4 ]

   day 0  p=7   new min -> min_price = 7        best = 0
   day 1  p=1   new min -> min_price = 1        best = 0
   day 2  p=5   sell: 5-1 = 4                   best = 4
   day 3  p=3   sell: 3-1 = 2                   best = 4
   day 4  p=6   sell: 6-1 = 5                   best = 5   <- best profit
   day 5  p=4   sell: 4-1 = 3                   best = 5
```

The entire past is compressed into a single number — the best buy price so far —
so one pass is enough.

## Complexity

- **Time: about n steps.** One pass, constant work per day.
- **Extra memory: constant.** Just `min_price` and `best`.

## Pitfalls

- Selling **before** buying. The "later day" rule is easy to drop; tracking a
  *running* minimum enforces it for free — you only ever sell against a price from
  an earlier day.
- Returning a negative number when no trade is profitable. Clamp `best` at `0`.
- Confusing this with "biggest difference between any two numbers." Order matters
  here; the smaller value must come first.
- Empty or single-day input: profit is `0`, since you can't buy and sell.

## Transfer

The reusable move is the running extremum: **sweep once, keep the best "so far"
value you need, and answer each new position against it.** The same shape solves
Maximum Subarray (carry the best sum ending here), the harder buy/sell variants,
and any "best pair where one index must precede the other" question. Whenever a
slow solution re-searches the prefix for a min or max, carry it as you go instead.
