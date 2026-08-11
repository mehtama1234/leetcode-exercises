# 322. Coin Change

**Pattern:** Dynamic programming (unbounded knapsack — fewest items)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/coin-change/

## The problem in plain words

You have coins of a few fixed sizes, and an unlimited pile of each. Given a
target amount, what is the **smallest number of coins** that adds up to exactly
that amount? If you can't hit it at all, return `-1`.

## Start from the obvious

Ask: "what is the fewest coins to make amount `A`?" You don't know which coin
comes last, so try them all. Whatever the last coin `c` is, the rest of the pile
has to make `A - c` — which is the *same question* on a smaller amount:

```
fewest(A) = 1 + min over coins c of fewest(A - c)
fewest(0) = 0
fewest(negative) = infinity   # overshot, dead end
```

Turned straight into recursion, this is correct. It's the honest first thought.

## Find the waste

That recursion branches into one child per coin, and those children branch again.
The same amount shows up on many different paths — `fewest(6)` gets asked whether
you reached 6 via `1+2+... ` or `2+... ` or any other route. Each time, the naive
version re-explores the whole subtree beneath it. The number of paths is
exponential, but the number of *distinct* amounts is only `A + 1`.

That gap — exponential recomputation over a linear set of real subproblems — is
exactly what DP removes.

## The insight

There are only `amount + 1` genuine subproblems: the fewest coins for `0, 1, 2,
..., amount`. Solve each **once**.

**Top-down:** keep the recursion, cache each `fewest(rem)` the first time it's
computed. Later hits are lookups.

**Bottom-up (tabulation):** fill `dp[0..amount]` in increasing order. Start with
`dp[0] = 0` and everything else `infinity` (unknown / impossible). Then:

```
for a in 1..amount:
    for each coin c with c <= a:
        dp[a] = min(dp[a], dp[a - c] + 1)
```

`dp[a - c] + 1` means "take the best way to make `a - c`, then add one coin `c`."
Because coins are reusable, we sweep amounts **upward**, so `dp[a - c]` may itself
already use coin `c` — that's what makes the supply unlimited.

## Complexity

- **Time:** `O(amount * number_of_coins)` — for each of the `amount` subproblems
  we try every coin once.
- **Space:** `O(amount)` for the table (the top-down version also uses `O(amount)`
  cache plus recursion stack).

## Pitfalls

- Returning `0` instead of `-1` when it's impossible. Keep "unreachable" as a
  sentinel (`infinity`) all the way through, and convert to `-1` only at the end.
- `amount == 0` must return `0`, not `-1` — making nothing needs no coins.
- This is **fewest coins**, not **number of ways** (that's a different loop order —
  see Coin Change II). Don't confuse the two.
- Greedy (always grab the biggest coin) is wrong: for coins `[1, 3, 4]`, amount
  `6`, greedy gives `4+1+1 = 3` coins but `3+3 = 2` is better. You genuinely need
  the DP.

## Transfer

This is the **unbounded knapsack** shape: "reach a target using reusable items,
optimizing a count or value." The move — *guess the last item, recurse on the
remainder, cache by remainder* — reappears in Coin Change II (count ways),
[Word Break / 139](../0139-word-break/) (reach the end of a string using reusable
dictionary words), and Combination Sum.
