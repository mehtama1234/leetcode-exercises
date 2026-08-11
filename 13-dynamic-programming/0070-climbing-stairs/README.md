# 70. Climbing Stairs

**Pattern:** Dynamic programming (1-D, look back two steps)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/climbing-stairs/

## The problem in plain words

There's a staircase with `n` steps. Each move you make climbs either 1 step or 2
steps. How many different sequences of moves get you exactly to the top?

For `n = 3` there are three ways: `1+1+1`, `1+2`, `2+1`. Notice the answer counts
*orderings* of moves, not sets of moves.

## Start from the obvious

Think about the very last move that lands you on step `n`. There are only two
possibilities:

- your last move was a **1-step**, so just before it you were on step `n-1`, or
- your last move was a **2-step**, so just before it you were on step `n-2`.

Those two cases don't overlap and cover everything, so:

```
ways(n) = ways(n-1) + ways(n-2)
ways(1) = 1
ways(2) = 2
```

Turn that straight into recursion. Correct — but run it for `n = 40` and it
crawls.

## Find the waste

That recurrence is *exactly* Fibonacci's shape, and it has Fibonacci's problem:
the call tree branches, and the same subproblem shows up in many branches.

```
             ways(5)
            /        \
      ways(4)         ways(3)
       /   \           /   \
  ways(3) ways(2)  ways(2) ways(1)
   ...
```

`ways(3)` gets recomputed, `ways(2)` several times, and so on. The number of
calls itself grows like Fibonacci — exponential. The waste: **we keep re-solving
the same step count from scratch.**

## The insight

There are only `n` distinct subproblems, `ways(1)` through `ways(n)`. Solve each
once and reuse it. Top-down: memoize the recursion. Bottom-up: fill the counts in
order, smallest first.

Then the final squeeze — the recurrence only reaches back **two** steps, so you
never need the whole table, just the last two counts. Slide a window forward:

```
prev, curr = 1, 2          # ways(1), ways(2)
repeat for step 3..n:
    prev, curr = curr, prev + curr
```

`O(1)` space.

## Complexity

- **Naive recursion:** `O(2^n)` time (the tree branches every level), `O(n)` stack.
- **Memoized:** `O(n)` time (n subproblems, each solved once), `O(n)` space.
- **Rolling loop:** `O(n)` time, `O(1)` space — the natural endpoint.

## Pitfalls

- The base cases differ from raw Fibonacci: here `ways(1) = 1` and `ways(2) = 2`.
  This is Fibonacci shifted by one index, not Fibonacci itself.
- It's easy to think you're counting *sets* of moves; you're counting *ordered*
  sequences, which is why `1+2` and `2+1` both count.
- The naive recursion times out for large `n` — don't submit it.

## Transfer

Same recurrence, same rolling-variable trick as
[Fibonacci / 509](../0509-fibonacci-number/). Once "the last move was one of a few
choices, sum over them" clicks, it generalizes: if you could also take 3-step
moves, you'd sum three terms. The look-back-a-fixed-number-of-steps idea also
drives [House Robber / 198](../0198-house-robber/) and
[Min Cost Climbing Stairs / 746](https://leetcode.com/problems/min-cost-climbing-stairs/).
