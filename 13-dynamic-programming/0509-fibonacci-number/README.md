# 509. Fibonacci Number

**Pattern:** Dynamic programming (1-D, look back two steps)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/fibonacci-number/

## The problem in plain words

The Fibonacci numbers start `0, 1` and every number after that is the sum of the
two before it: `0, 1, 1, 2, 3, 5, 8, ...`. Given `n`, return `F(n)`.

This problem is the "hello world" of dynamic programming — it's the smallest
place where you can watch the whole DP idea appear.

## Why this matters

Fibonacci itself is a toy, but the operation it teaches is the whole of dynamic programming: **find the repeated subproblem, solve it once, reuse the answer.** The recurrence "each value depends on a fixed number of earlier values" is the smallest possible instance of memoization and of look-back rolling state.

Where the *method* (and this exact look-back-a-few-steps shape) really shows up:

- **Any DP-solved system** — build tools memoizing recomputed results, incremental compilers, spreadsheet recalculation, and query planners all rest on "cache the subproblem."
- **Linear recurrences** — population/growth models, signal filters (IIR), and amortization schedules that reference the last few states.
- **Counting problems** — tilings and constrained-string counts share Fibonacci's recurrence exactly.

The good solution buys the canonical DP win: **exponential recomputation → `O(n)` time** by solving each subproblem once, and then the rolling-two-variables squeeze buys **`O(1)` memory** because the recurrence never reaches back more than two steps. Learn it here and you carry it to every harder DP.

## Start from the obvious

The definition *is* an algorithm. Turn it straight into recursion:

```
F(n) = n                    if n < 2
F(n) = F(n-1) + F(n-2)      otherwise
```

That's correct. It's also the honest first thing to write. But run it for `n=40`
and it crawls.

## Find the waste

Draw the call tree for `F(5)`:

```
                F(5)
             /        \
          F(4)         F(3)
         /    \       /    \
      F(3)   F(2)  F(2)   F(1)
      ...
```

`F(3)` gets computed twice. `F(2)` three times. `F(1)` five times. Every branch
re-derives values that some other branch already found. The number of calls
itself grows like Fibonacci — exponential. The waste is obvious: **we keep
solving the same subproblem from scratch.**

## The insight

There are only `n + 1` distinct subproblems here: `F(0)` through `F(n)`. If we
solve each one *once* and remember the answer, the exponential tree collapses to
a line. Two equivalent ways to do it:

**Top-down (memoized recursion):** keep the recursion, but cache each answer the
first time you compute it. Later requests are a dictionary lookup.

**Bottom-up (tabulation):** fill the answers in order, smallest first, so every
value you need is already known when you reach it.

And here's the last squeeze: the recurrence only ever reaches back **two** steps.
So you don't need the whole table — just the last two numbers. Slide a window
forward:

```
prev, curr = 0, 1
repeat n-1 times:
    prev, curr = curr, prev + curr
```

That's `O(1)` space.

## Complexity

- **Naive recursion:** `O(phi^n)` time (exponential), `O(n)` stack space.
- **Memoized:** `O(n)` time (each of n subproblems solved once), `O(n)` space.
- **Rolling loop:** `O(n)` time, `O(1)` space — the natural endpoint.

## Pitfalls

- Off-by-one in the base cases: `F(0)=0`, `F(1)=1`. Getting these wrong shifts the
  whole sequence.
- The naive version is genuinely too slow for large `n` on LeetCode — don't submit
  it.
- In the swap `prev, curr = curr, prev + curr`, both right-hand values are read
  *before* either assignment happens; doing it in two separate statements without a
  temp would corrupt one of them.

## Transfer

"Only look back a fixed number of steps, so keep a few rolling variables" is the
core of many easy DP problems:
[Climbing Stairs / 70](../0070-climbing-stairs/) (same recurrence, different
story), [House Robber / 198](../0198-house-robber/) (look back two with a choice).
The bigger transfer is the DP method itself: *find the repeated subproblem, solve
it once, reuse it.*
