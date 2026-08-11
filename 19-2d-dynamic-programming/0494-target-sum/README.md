# 494. Target Sum

**Pattern:** 2-D dynamic programming (subset-sum counting reduction)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/target-sum/

## The problem in plain words

You get a list of non-negative numbers. Put a `+` or a `-` in front of each one,
then add them all up. Count how many of the `2^n` ways to choose those signs make
the total equal a given target.

## Why this matters

Underneath is a two-part idea: *count assignments over a boolean choice per item*
where a huge branching space collapses because only the **running total** matters,
not the path that produced it. Two different sign prefixes that reach the same sum
are interchangeable from then on — recognizing that "the state is the sum" is the
move that tames the explosion.

The second half is a genuinely useful algebraic reduction: a `+/-` partition is
the same as splitting the numbers into two groups, and that turns the problem into
"how many subsets sum to a fixed value?" — subset-sum counting, which shows up in
budget allocation (how many ways can these line items net to zero?), reconciling
signed ledgers (which transactions cancel to a balance?), and load-balancing two
bins.

What the good solution buys is collapsing an exponential enumeration into
`O(n × sum)` work and `O(sum)` memory — the difference between a combinatorial
blow-up and a table that fits comfortably in a request handler.

## Start from the obvious

Every number gets a sign, so branch on both choices at every index and carry the
running sum:

```
def go(i, running):
    if i == n: return 1 if running == target else 0
    return go(i+1, running + nums[i]) + go(i+1, running - nums[i])
```

Correct, and clearly `O(2^n)` — it walks the full binary tree of sign choices.

## Find the waste

The tree has `2^n` leaves but the *state* at any node is just `(i, running)`, and
the running sum ranges only over `-total .. +total`. So there are at most
`n × (2·total + 1)` distinct states, and the exponential tree revisits them
constantly. Memoizing on `(i, running)` alone drops it to `O(n × sum)`.

## The insight

You can do better than caching by removing the signs with algebra. Let `P` be the
numbers you mark `+` and `N` the ones you mark `-`:

```
sum(P) - sum(N) = target
sum(P) + sum(N) = total          (every number is in exactly one group)
```

Adding the two lines: `2·sum(P) = target + total`, so
`sum(P) = (target + total) / 2`. The sign problem is now **"how many subsets of
nums sum to `need = (target + total) / 2`?"** — plain 0/1 subset-sum counting:

```
dp[0] = 1                        # empty subset makes 0
for x in nums:
    for s in range(need, x - 1, -1):
        dp[s] += dp[s - x]
```

`dp[s]` = number of subsets so far that total `s`. Iterating `s` **downward** is
what enforces "use each number at most once" — it stops `x` from being counted
into a sum that already includes `x`.

## Complexity

- **Time:** `O(n × need)` — n numbers, each sweeping the `need`-sized row once.
- **Space:** `O(need)` — a single row. The `(i, running)` memo is `O(n × sum)`;
  the reduction shrinks both dimensions and drops one.

## Pitfalls

- **Zeros.** `0` can be `+0` or `-0`, so every zero *doubles* the count. The
  subset-sum formulation handles this automatically (a 0 lets `dp[s] += dp[s]`),
  but ad-hoc solutions often miss it.
- If `target + total` is **odd**, or `|target| > total`, there's no valid split —
  return 0 before dividing.
- Iterating `s` upward instead of downward turns each number into an unbounded
  coin (Coin Change II), which is the wrong count here.

## Transfer

The reusable moves are *(a) state = running aggregate, not path*, and *(b) turn a
signed/partition problem into subset-sum by algebra*. Siblings:
[Partition Equal Subset Sum / 416](https://leetcode.com/problems/partition-equal-subset-sum/)
(does a subset hit total/2?), [Coin Change II / 518](../0518-coin-change-ii/)
(the unbounded counting cousin), and
[Last Stone Weight II / 1049](https://leetcode.com/problems/last-stone-weight-ii/)
(same `+/-` reduction, minimizing the leftover).
