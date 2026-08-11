# 518. Coin Change II

**Pattern:** 2-D dynamic programming (unbounded knapsack — counting)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/coin-change-ii/

## The problem in plain words

You have coin denominations (e.g. 1, 2, 5) and a target amount. Count how many
*different combinations* of coins add up to that amount. A combination is a
multiset — how many of each coin — so 1+2 and 2+1 are the **same** answer, not
two. You can use each denomination as many times as you like.

## Why this matters

The underlying operation is *counting the ways to hit a total from repeatable
parts, without double-counting reorderings.* That "order doesn't matter" clause
is the whole difficulty: the moment you count arrangements instead of
combinations you have a different (and usually easier) problem, and getting the
distinction right is a recurring source of real bugs.

This shape shows up wherever you tally the ways to compose a fixed quantity from
reusable units. Making exact change at a vending machine or a bank teller drawer
is the literal case. A billing or pricing engine asking "how many ways can these
plan tiers sum to this invoice total?" is the same count. Scoring systems (how
many ways to reach N points from moves worth fixed values) and certain
resource-packing quotes reduce to it too.

What the good solution buys is turning an exponential enumeration of every
possible pile of coins into an `O(coins × amount)` table — and a one-dimensional
version that uses only `O(amount)` memory, small enough to run inside a tight
request budget.

## Start from the obvious

Recurse on two things: which coin type you're allowed to start using, and how
much amount is left. At each coin you either skip it forever or take one more of
it.

```
def count(i, remaining):
    if remaining == 0: return 1          # made exact change
    if remaining < 0 or i == len(coins): return 0
    return count(i + 1, remaining)               # skip coin i
         + count(i, remaining - coins[i])        # use coin i once more
```

Pinning a coin **index** and only ever moving it forward is the trick that stops
reordering: once you've moved past coin `i` you can never come back to it, so
each combination is generated in exactly one canonical order.

## Find the waste

That recursion re-solves the same `(i, remaining)` pair over and over — every
different path that leaves the same coins and the same amount recomputes an
identical subtree. There are only `len(coins) × (amount+1)` distinct states, so
cache them. Memoizing `count` turns exponential into `O(coins × amount)`.

## The insight

Read the memo table bottom-up and one dimension collapses. Let `dp[a]` = ways to
make amount `a` using the coins seen so far. Start with `dp[0] = 1` (one way to
make nothing: take nothing). Then fold in coins **one at a time**:

```
for coin in coins:
    for a in range(coin, amount + 1):
        dp[a] += dp[a - coin]
```

Two orderings carry all the meaning. The coin loop is *outside* — a coin's
entire contribution is absorbed before the next coin exists, so no combination
can interleave coins in two orders. The amount loop goes *upward*, so `dp[a-coin]`
may already include this same coin — that's what lets a coin repeat.

## Complexity

- **Time:** `O(coins × amount)` — each cell of the conceptual table is touched
  once.
- **Space:** `O(amount)` — one rolling row. The naive 2-D table is
  `O(coins × amount)`; the outer-coin ordering is exactly what makes the row
  reusable.

## Pitfalls

- **Swapping the loops.** Amount-outer, coin-inner counts *sequences* (permutations)
  and gives Coin Change II's evil twin, [Combination Sum IV / 377](https://leetcode.com/problems/combination-sum-iv/).
- Iterating amount **downward** would make each coin usable at most once — that's
  the 0/1 knapsack, not this unbounded one.
- Forgetting `dp[0] = 1`; the empty combination is a real way to make 0.
- `amount == 0` should return 1, not 0.

## Transfer

The pattern is *unbounded knapsack, counting variant*: outer loop over items,
inner loop upward over capacity, accumulate. Siblings:
[Coin Change / 322](https://leetcode.com/problems/coin-change/) (minimize count
instead of counting ways), [Combination Sum IV / 377](https://leetcode.com/problems/combination-sum-iv/)
(count sequences), [Target Sum / 494](../0494-target-sum/) (counting variant that
reduces to a 0/1 subset-sum count).
