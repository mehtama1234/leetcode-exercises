# 901. Online Stock Span

**Pattern:** Monotonic stack (decreasing), on a live stream
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/online-stock-span/

## The problem in plain words

Prices arrive one day at a time. You can't see the future and you can't rewind.
For each new price, report its **span**: how many days in a row ending today
(today counts) had a price **less than or equal to** today's — stopping the count
the moment you hit an earlier day that was strictly higher.

You build a `StockSpanner` object whose `next(price)` returns that span each call.

```diagram
   prices coming in:  100  80  60  70  60  75  85
   span reported:       1   1   1   2   1   4   6

   day of 75:  ... 60  70  60 [75]     count back while <= 75
                    ^^^^^^^^^^^ 60,70,60,75 -> span 4, then 100 blocks
   day of 85:  80 60 70 60 75 [85]     everything back to 100 is <= 85 -> span 6
```

## Why this matters

Underneath is one operation: *for the newest item, how far back can you go before
something taller blocks you?* — the nearest bigger value to the **left**. And it's
**live**: the data is a stream, so you answer using only what you've already stored.
No second pass over history.

Concrete places this shows up: trading dashboards showing "longest current run at or
below today's price"; alerting that computes "how long has this metric stayed at or
under its current level" as samples arrive; any streaming analytics where each event
needs a look-back but you can't re-read the whole past. The "live, can't rewind"
constraint is what makes it more than a textbook scan.

What the good solution buys: a strict per-event budget. A plain look-back is slow on
a long gentle climb, and over a whole stream it degrades to about `m × m` work. The
stack makes each `next` cost a constant amount **on average** — every price is
touched a fixed number of times across the entire stream, so the feed keeps up no
matter how long it runs.

## Start from the obvious

Store every price. On each new day, walk backward counting days `<=` today until one
is strictly higher.

```diagram
   history: 100 80 60 70 60      new price = 75

   walk back:  60 <=75 yes | 70 <=75 yes | 60 <=75 yes | 80 <=75 no STOP
               (we re-check every single old day, one at a time)
   span = 4
```

Honest and correct. But a long, slow climb makes each new day re-walk the whole
history — about `m × m` steps total. Worse, it keeps re-counting days that an
earlier, taller price already swallowed.

## Find the waste

Watch what a tall day does to the days behind it. Once today's price is `>=` some
earlier day, that earlier day now stands behind a bar at least as tall as itself. It
can **never again** be the blocker for any future day — today shadows it. So we
should never look at it individually again. The slow walk keeps re-examining these
already-shadowed days one by one.

The fix: when today swallows a run of shorter days, collapse that whole run into a
single block, so future days skip past it in one step.

## The insight

Keep a stack of `(price, span)` blocks whose prices strictly **decrease** from bottom
to top. On each new price, pop every block whose price is `<=` today and **absorb its
span** — that block's whole run is now part of today's run — then push today with the
total span collected.

```diagram
   stack holds (price, span), prices decreasing bottom -> top

   next(100): stack empty         push (100,1)   stack: (100,1)                 -> 1
   next(80):  80 < 100, no pop    push (80,1)    stack: (100,1)(80,1)           -> 1
   next(60):  60 < 80,  no pop    push (60,1)    stack: (100,1)(80,1)(60,1)     -> 1
   next(70):  70 >= 60 pop(60,1)  span=1+1=2     stack: (100,1)(80,1)
              70 < 80, stop       push (70,2)    stack: (100,1)(80,1)(70,2)     -> 2
   next(60):  60 < 70, no pop     push (60,1)                                    -> 1
   next(75):  75>=60 pop(60,1) span=1+1=2 | 75>=70 pop(70,2) span=2+2=4
              75 < 80 -> STOP before 80.  span = 4
              push (75,4)   stack: (100,1)(80,1)(75,4)                           -> 4
```

Why each `next` is cheap on average: each price is pushed exactly once and popped at
most once over the entire life of the stream. A single `next` can pop many blocks,
but those pops were paid for by earlier pushes — so across `m` calls the total work
is about `m` steps. Each pop collapses a run of days into one block that is never
re-walked.

## Complexity

- **Time:** about one step per call on average; about `m` steps for `m` total calls.
- **Extra memory:** up to `m` in the worst case (strictly decreasing prices never
  pop), but usually far smaller because equal-or-lower days collapse into blocks.

## Pitfalls

- The comparison is `<=`, not `<`: equal prices are part of the span and must be
  absorbed (see `[30,30,30] -> 1,2,3`).
- Store the running **span** in each block, not just the price — that's what lets a
  pop swallow a whole run in one step instead of re-counting it.
- One slow `next` (many pops) does not break the bound. The cost is spread out: those
  pops were bought by earlier pushes.
- Every span is at least `1` (today counts itself); forgetting that undercounts.

## Transfer

This is the live, look-**left** version of the next-greater-element stack. Siblings:
[Next Greater Element I / 496](../0496-next-greater-element-i/) (look right, all at
once), [Daily Temperatures / 739](https://leetcode.com/problems/daily-temperatures/)
(distance to the next warmer day), and the resolve-on-pop core of
[Largest Rectangle in Histogram / 84](../0084-largest-rectangle-in-histogram/).
Whenever a stream needs a bounded-cost "how far back until something bigger," reach
for a monotonic stack that stores collapsed runs.
