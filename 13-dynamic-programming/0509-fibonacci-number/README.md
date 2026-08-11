# 509. Fibonacci Number

**Pattern:** Dynamic programming (1-D, look back two steps)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/fibonacci-number/

## The problem in plain words

The Fibonacci numbers start `0, 1`, and every number after that is the sum of the
two before it. Given `n`, hand back `F(n)`.

```diagram
   index:   0   1   2   3   4   5   6   7
   F:       0   1   1   2   3   5   8  13
                        ^
              F(4) = F(3) + F(2) = 2 + 1 = 3
              each number is fed by the two on its left
```

This is the smallest place where the whole dynamic-programming idea shows up, so
it's worth slowing down here — the move you learn carries to every harder DP.

## Why this matters

Fibonacci itself is a toy. The move it teaches is not: **find the subproblem you
keep re-solving, solve it once, reuse the answer.** The recurrence "each value
depends on a fixed number of earlier values" is the smallest possible case of
remembering-instead-of-recomputing.

The same shape runs real systems. Build tools cache compiled results instead of
rebuilding from scratch; a spreadsheet recomputes only the cells that changed;
population and growth models, and audio filters, all reference the last few states
to produce the next one. Counting problems — tilings, constrained-string counts —
obey this exact recurrence too.

What the fast version buys you is the jump from redoing exponential amounts of
work to touching each value once. That is the line between a program that answers
for `n = 50` and one that hangs.

## Start from the obvious

The definition *is* an algorithm. Write it as recursion:

```
F(n) = n                    if n < 2
F(n) = F(n-1) + F(n-2)      otherwise
```

Correct, and the honest first thing to reach for. But run it for `n = 40` and it
crawls. Look at *why*.

## Find the waste

Draw the call tree for `F(5)` and watch the same values reappear:

```diagram
                 F(5)
              /        \
           F(4)         F(3)      <- F(3) shows up here...
          /    \        /   \
       F(3)   F(2)   F(2)  F(1)   <- ...and again here, from scratch
       / \
    F(2) F(1)

   F(3) computed twice.  F(2) three times.  F(1) five times.
```

Every branch re-derives values another branch already found. The number of calls
grows like Fibonacci itself — exponential. The waste is plain: **the same
subproblem gets solved from scratch again and again.**

## The insight

There are only `n + 1` distinct subproblems in the whole tree: `F(0)` through
`F(n)`. Solve each *once*, remember it, and the branching tree collapses into a
straight line.

**Top-down (memoized — cache each answer once):** keep the recursion, but the
first time you compute a value, write it down. Later requests are a lookup.

**Bottom-up (fill a table in order):** compute `F(0)`, `F(1)`, `F(2)`, ... in
sequence, so every value you need is already sitting there when you reach it.

```diagram
   fill left to right; each new cell reads the two before it

   idx:   0   1   2   3   4   5
   F:   [ 0 ][ 1 ][ . ][   ][   ][   ]
                    ^
          F(2) = F(1) + F(0) = 1 + 0 = 1
                    |    \____ reads idx 0
                    \_________ reads idx 1

   F:   [ 0 ][ 1 ][ 1 ][ . ][   ][   ]
                         ^
          F(3) = F(2) + F(1) = 1 + 1 = 2
```

Now the last squeeze. The recurrence only ever reaches back **two** steps, so you
never need the whole row — only the last two numbers. Slide a two-cell window
forward:

```diagram
   keep just (prev, curr); step it n-1 times

   prev curr
   [ 0 ][ 1 ]                start: F(0), F(1)
        \____ +
   [ 1 ][ 1 ]                curr becomes 0+1 = 1  -> F(2)
        \____ +
   [ 1 ][ 2 ]                curr becomes 1+1 = 2  -> F(3)
        \____ +
   [ 2 ][ 3 ]                curr becomes 1+2 = 3  -> F(4)
```

That's `O(1)` space — constant memory, no table at all.

## Complexity

- **Naive recursion:** exponential time (calls grow like Fibonacci), `O(n)` stack
  from the recursion depth.
- **Memoized:** about `n` steps (each of `n + 1` subproblems solved once), about
  `n` memory for the cache.
- **Rolling loop:** about `n` steps, constant memory — the natural endpoint.

## Pitfalls

- Off-by-one in the base cases: `F(0) = 0`, `F(1) = 1`. Get these wrong and the
  whole sequence shifts.
- The naive version is genuinely too slow for large `n` — don't submit it.
- In `prev, curr = curr, prev + curr`, both right-hand values are read *before*
  either assignment lands. Splitting it into two statements without a temp would
  overwrite one value before the other could use it.

## Transfer

"Only look back a fixed number of steps, so keep a few rolling variables" is the
core of many easy DPs:
[Climbing Stairs / 70](../0070-climbing-stairs/) (same recurrence, different
story) and [House Robber / 198](../0198-house-robber/) (look back with a choice
attached). The bigger transfer is the method itself: *find the repeated
subproblem, solve it once, reuse it.*
