# 901. Online Stock Span

**Pattern:** Monotonic stack (decreasing), streaming
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/online-stock-span/

## The problem in plain words

Prices arrive one day at a time — you can't see the future and you can't rewind.
For each new day's price, report its **span**: how many days in a row ending today
(today included) had a price **less than or equal to** today's, stopping the count
the moment you hit an earlier day that was strictly higher.

Implement a `StockSpanner` object whose `next(price)` returns that span each call.

## Why this matters

The core operation is *nearest greater element to the left*, computed **online**:
for the newest item, how far back can you go before something taller blocks you?
Because the data is a stream, you must answer with only what you've stored — no
second pass.

Concrete places this shows up: live trading and monitoring dashboards that show
"days since a higher price / longest current run"; alerting systems computing "how
long has this metric stayed at or below its current level" as samples arrive; and
any streaming analytics where each event needs a look-back that can't re-read the
whole history. The "online, un-rewindable" constraint is what makes it more than
a textbook scan.

What the good solution buys is a strict per-event budget. A naive look-back is
O(n) per day and O(n²) over the stream — unacceptable for a live feed. The
monotonic stack makes each `next` **amortized O(1)**: every price is touched a
constant number of times across the entire stream, so the feed keeps up no matter
how long it runs.

## Start from the obvious

Store every price. On each new day, walk backward counting days `<=` today until
one is strictly higher:

```
next(price):
    span = 1
    walk i backward from yesterday:
        if prices[i] <= price: span += 1
        else: stop
    return span
```

Honest and correct. But a long gentle climb makes each new day re-walk the whole
history — O(n²) total, and it re-counts days that earlier, taller prices already
resolved.

## Find the waste

Notice what a tall day does to the days behind it: once today's price is `>=` some
earlier day, that earlier day is now standing behind a bar at least as tall as
itself. It can **never again** be the blocker for any future day — today shadows
it. So we should never look at it again. The naive walk keeps re-examining these
already-dominated days.

## The insight

Keep a stack of `(price, span)` blocks whose prices strictly **decrease** from
bottom to top. On each new price, pop every block whose price is `<= today` and
**absorb its span** — that block's whole run is now part of today's run — then
push today with the accumulated span.

```
next(price):
    span = 1
    while stack and stack[-1].price <= price:
        span += stack.pop().span      # absorb a dominated run
    stack.push((price, span))
    return span
```

Why monotonic gives amortized O(1): each price is pushed exactly once and popped
at most once over the entire lifetime of the stream. A single `next` can pop many
blocks, but those pops are "paid for" by earlier pushes — total work across `m`
calls is `O(m)`. Each pop **resolves** a contiguous run of days that this price
now dominates, collapsing it into one block so it's never re-walked.

## Complexity

- **Time:** amortized `O(1)` per `next`; `O(m)` for `m` total calls.
- **Space:** `O(m)` worst case (strictly decreasing prices never pop), but the
  stack is usually far smaller because equal-or-lower days collapse.

## Pitfalls

- The comparison is `<=`, not `<`: equal prices are part of the span and must be
  absorbed (see the `[30,30,30] -> 1,2,3` case).
- Storing the running **span** in each block, not just the price — that's what
  lets a pop absorb a whole run in one step instead of re-counting.
- Thinking a single slow `next` (many pops) breaks the bound; it's *amortized*
  O(1) — those pops were bought by prior pushes.
- Every span is at least `1` (today counts itself); forgetting that undercounts.

## Transfer

This is the streaming, look-**left** version of the next-greater-element stack.
Siblings: [Next Greater Element I / 496](../0496-next-greater-element-i/) (look
right, batch), [Daily Temperatures / 739](https://leetcode.com/problems/daily-temperatures/)
(distance to next warmer day), and the resolve-on-pop core of
[Largest Rectangle in Histogram / 84](../0084-largest-rectangle-in-histogram/).
Whenever a stream needs a bounded-cost "how far back until something bigger,"
reach for a monotonic stack that stores collapsed runs.
