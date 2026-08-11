# 739. Daily Temperatures

**Pattern:** Monotonic stack (next warmer day)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/daily-temperatures/

## The problem in plain words

You have a list of daily temperatures. For each day, answer: how many days until it
gets warmer than today? If it never gets warmer, the answer is `0`.

```diagram
   day:      0   1   2   3   4   5   6   7
   temp:    73  74  75  71  69  72  76  73
   answer:   1   1   4   2   1   1   0   0
                     ^ day 2 (75) waits until day 6 (76): 6 - 2 = 4
```

## Why this matters

The one reusable idea is the *next-greater-element* query: for each item, find the
next one that beats it, in one pass, using a stack that holds only the still-waiting
items in order. You flip "each day searches forward" into "each new day resolves the
earlier days it beats."

This is a workhorse in real analysis. Stock and time-series work asks "how long until
the next higher peak?" — the same stack. Layout engines use the monotonic-stack
cousin (largest rectangle under a skyline). Terrain and visibility calculations use
the same "nearest taller thing on each side" idea.

What you're solving for is collapsing a repeated forward scan into a single pass. Each
day is pushed and popped at most once, so a stretch the brute force re-walks over and
over is touched a constant number of times total.

## Start from the obvious

For each day, walk forward until you hit a hotter day, and count the steps.

```diagram
   for each i:
     for j from i+1 onward:
       if temp[j] > temp[i]: answer[i] = j - i; stop
```

Correct, worth writing first. But watch a long cooling stretch: day 0 scans the whole
tail, day 1 scans almost the same tail, and so on. Every early day re-walks the same
future days — about n × n work, and that repetition is the thing to kill.

## Find the waste

Flip the question. Instead of each day searching forward, ask: **when a warm day
arrives, which earlier days was it waiting to answer?** A hot day today answers every
earlier day that is still waiting *and* cooler than today.

And the days still waiting must form a **decreasing** run of temperatures — if an
earlier waiting day were cooler than a later one, the later day would already have
answered it.

```diagram
   still-waiting days always read hottest-first, coolest on top:

     temps waiting: 75  71  69       (bottom -> top)
                            ^ top = coolest, most recent
   a new day of 72 arrives:
     top 69 < 72 ? yes -> 69 found its warmer day -> pop
     top 71 < 72 ? yes -> 71 found its warmer day -> pop
     top 75 < 72 ? no  -> stop; push 72
```

"Keep the still-waiting days, newest on top, temperatures decreasing" is a
**monotonic stack** (a stack whose values always go one direction).

## The insight

Keep a stack of the *indices* of days that haven't found a warmer day yet. Walk once.
For each new day `i` with temperature `t`: while the day on top is cooler than `t`, it
just found its warmer day (today) — pop it and set its answer to `i - poppedIndex`.
Then push `i`.

```diagram
   temp:  73  74  75  71  69  72  76  73     stack holds INDICES
   i=0 (73)  push 0                 stack:[0]
   i=1 (74)  73<74 pop0 ans[0]=1-0=1  push1  stack:[1]
   i=2 (75)  74<75 pop1 ans[1]=2-1=1  push2  stack:[2]
   i=3 (71)  75<71? no  push3         stack:[2,3]
   i=4 (69)  71<69? no  push4         stack:[2,3,4]
   i=5 (72)  69<72 pop4 ans[4]=5-4=1
             71<72 pop3 ans[3]=5-3=2
             75<72? no  push5         stack:[2,5]
   i=6 (76)  72<76 pop5 ans[5]=6-5=1
             75<76 pop2 ans[2]=6-2=4
             push6                    stack:[6]
   i=7 (73)  76<73? no  push7         stack:[6,7]
   end -> days 6 and 7 never warmed -> stay 0
   answer: [1,1,4,2,1,1,0,0]
```

Every index is pushed once and popped at most once, so even with the inner loop the
total work stays linear — about n steps overall.

## Complexity

- **Time: about n steps.** Each index enters and leaves the stack exactly once; the
  total pops across the whole run is at most n.
- **Extra memory: up to n.** A strictly cooling input like `[90, 80, 70]` keeps every
  day on the stack. The answer array is size n too.

## Pitfalls

- **Strict vs. non-strict:** "warmer" means strictly greater. Pop only when the top is
  *cooler*, so equal temperatures like `[50, 50, 50]` don't count and stay `0`.
- **Store indices, not temperatures:** the answer is a day gap `i - prev`, so the
  stack must hold indices.
- **Leftovers stay 0:** days still on the stack at the end never warmed up — leave
  their `0`.
- Don't reset or re-scan; the point is a single pass.

## Transfer

This is the **next-greater-element** template, and the monotonic stack behind it
recurs widely: [Next Greater Element I / 496](../../22-monotonic-stack/0496-next-greater-element-i/),
[Largest Rectangle in Histogram / 84](../../22-monotonic-stack/0084-largest-rectangle-in-histogram/),
[Trapping Rain Water / 42](../../22-monotonic-stack/0042-trapping-rain-water/),
[Car Fleet / 853](../../22-monotonic-stack/0853-car-fleet/). Whenever you need, for each item, the next item
that beats it, keep a stack that stays sorted and pop as each new item resolves the
ones it dominates.
