# 70. Climbing Stairs

**Pattern:** Dynamic programming (1-D, look back two steps)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/climbing-stairs/

## The problem in plain words

A staircase has `n` steps. Each move climbs either 1 step or 2 steps. How many
different sequences of moves land you exactly on top?

```diagram
   n = 3, three ways:

   1 + 1 + 1     step -> step -> step
   1 + 2         step -> hop
   2 + 1         hop  -> step

   the answer counts ORDERINGS of moves, so 1+2 and 2+1 are two different ways
```

## Why this matters

Take the staircase away and this is: **count the sequences that reach a target,
when each spot is reachable from a small fixed set of earlier spots.** The move to
learn is a recurrence — the number of ways to reach step `n` is the sum of the
ways to reach the steps one legal move behind it.

That "count the arrangements built from a fixed move set" shape is everywhere. The
number of ways to tile a `2 × n` strip with dominoes obeys this exact recurrence.
Counting valid bit strings under a rule like "no two 1s in a row" is the same
look-back sum. So is counting distinct action sequences that end in a given state.

The fast version collapses an exponential call tree into a single pass, and the
rolling-variable trick keeps only the two states the recurrence actually reads.
That's the whole DP lesson in its smallest honest form.

## Start from the obvious

Think about the *very last* move that lands you on step `n`. There are only two
ways it could have gone:

- the last move was a **1-step**, so a moment ago you stood on step `n-1`, or
- the last move was a **2-step**, so a moment ago you stood on step `n-2`.

Those two cases don't overlap and cover everything, so the counts just add:

```
ways(n) = ways(n-1) + ways(n-2)
ways(1) = 1
ways(2) = 2
```

Turn that into recursion. Correct — but run it for `n = 40` and it crawls.

## Find the waste

That recurrence is Fibonacci's exact shape, and it has Fibonacci's problem: the
tree branches, and the same subproblem shows up on many branches.

```diagram
                ways(5)
               /       \
         ways(4)        ways(3)     <- ways(3) here...
         /    \         /    \
    ways(3) ways(2)  ways(2) ways(1)   <- ...and again here, recomputed
      ...

   ways(3) recomputed, ways(2) several times, calls grow exponentially
```

The number of calls itself grows like Fibonacci. The waste: **the same step count
gets re-solved from scratch.**

## The insight

There are only `n` distinct subproblems, `ways(1)` through `ways(n)`. Solve each
once. Top-down, cache the recursion. Bottom-up, fill the counts in order, smallest
first, so each cell reads answers already sitting to its left:

```diagram
   fill left to right; each cell = the two cells before it

   step:   1   2   3   4   5
   ways: [ 1 ][ 2 ][ . ][   ][   ]
                    ^
        ways(3) = ways(2) + ways(1) = 2 + 1 = 3
                     |    \____ reads step 1
                     \_________ reads step 2

   ways: [ 1 ][ 2 ][ 3 ][ . ][   ]
                         ^
        ways(4) = ways(3) + ways(2) = 3 + 2 = 5
```

Then the final squeeze: the recurrence reaches back only **two** steps, so keep
just the last two counts and slide the window forward:

```diagram
   keep (prev, curr); step from 3 up to n

   prev curr
   [ 1 ][ 2 ]              start: ways(1), ways(2)
        \____ +
   [ 2 ][ 3 ]              curr = 1+2 = 3   -> ways(3)
        \____ +
   [ 3 ][ 5 ]              curr = 2+3 = 5   -> ways(4)
        \____ +
   [ 5 ][ 8 ]              curr = 3+5 = 8   -> ways(5)
```

Constant memory.

## Complexity

- **Naive recursion:** exponential time (the tree branches every level), `O(n)`
  stack.
- **Memoized:** about `n` steps (n subproblems, each solved once), about `n`
  memory.
- **Rolling loop:** about `n` steps, constant memory — the natural endpoint.

## Pitfalls

- The base cases differ from raw Fibonacci: here `ways(1) = 1` and `ways(2) = 2`.
  This is Fibonacci shifted by one index, not Fibonacci itself.
- It's easy to think you're counting *sets* of moves. You're counting *ordered*
  sequences — that's why `1+2` and `2+1` both count.
- The naive recursion times out for large `n` — don't submit it.

## Transfer

Same recurrence and same rolling-variable trick as
[Fibonacci / 509](../0509-fibonacci-number/). Once "the last move was one of a few
choices, sum over them" clicks, it stretches: allow 3-step moves and you'd sum
three terms. The same look-back idea, with a choice bolted on, drives
[House Robber / 198](../0198-house-robber/) and
[Min Cost Climbing Stairs / 746](https://leetcode.com/problems/min-cost-climbing-stairs/).
