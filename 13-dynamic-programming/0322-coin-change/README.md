# 322. Coin Change

**Pattern:** Dynamic programming (unbounded knapsack — fewest items)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/coin-change/

## The problem in plain words

You have coins of a few fixed sizes and an unlimited pile of each. Given a target
amount, what is the **smallest number of coins** that adds up to exactly that
amount? If you can't hit it at all, return `-1`.

```diagram
   coins = [1, 2, 5]   amount = 11

   5 + 5 + 1 = 11      -> 3 coins   (the fewest)
   2+2+2+2+2+1 = 11    -> 6 coins   (also valid, but worse)

   answer: 3
```

## Why this matters

This is the **unbounded knapsack**: reach a target using reusable items while
keeping a count as small as possible. The move to learn is "guess the last item,
recurse on what's left, and cache the answer keyed on the leftover amount." It's
the canonical optimize-over-a-target DP.

Making a target from reusable units is a real problem. Cash registers and ATMs
dispense the fewest bills. Hitting an exact quota — bandwidth, memory pages,
container fills — from unlimited unit sizes with the least count is the same
shape, as is cutting stock to length with least waste. Reaching the end of a
string using reusable dictionary words has the same skeleton.

The fast version buys time: naive recursion re-explores the same amount along
exponentially many paths, while caching by leftover amount leaves only
`amount + 1` real subproblems. The problem also teaches an honest trap — **greedy
fails** (coins `[1,3,4]`, amount `6`) — so you genuinely need the DP, not a
"grab the biggest coin" shortcut.

## Start from the obvious

Ask: "what is the fewest coins to make amount `A`?" You don't know which coin comes
*last*, so try them all. Whatever the last coin `c` is, the rest of the pile has to
make `A - c` — which is the *same question* on a smaller amount:

```
fewest(A) = 1 + min over coins c of fewest(A - c)
fewest(0) = 0
fewest(negative) = infinity   # overshot, dead end
```

Turned into recursion, this is correct. The honest first thought.

## Find the waste

That recursion branches into one child per coin, and each child branches again. The
same amount shows up on many paths — `fewest(6)` gets asked whether you reached 6
via `1 + 5`, via `2 + 4`, or any other route — and each time the naive version
re-explores the whole subtree beneath it.

```diagram
              fewest(6)          coins [1,3,4]
            /     |    \
     f(5)      f(3)     f(2)
    / | \      / | \
 f(4)f(2)f(1) ...  f(2)  <- fewest(2) recomputed on several paths
                    ^
   paths are exponential, but distinct amounts are only 0..6 (seven of them)
```

That gap — exponential recomputation over a linear set of *real* subproblems — is
exactly what DP erases.

## The insight

There are only `amount + 1` genuine subproblems: the fewest coins for `0, 1, 2,
..., amount`. Solve each **once**, smallest first, into a table `dp` where `dp[a]`
= fewest coins to make amount `a`. Start with `dp[0] = 0` and everything else
`infinity` (unknown / impossible). Then:

```
for a in 1..amount:
    for each coin c with c <= a:
        dp[a] = min(dp[a], dp[a - c] + 1)
```

`dp[a - c] + 1` means "take the best way to make `a - c`, then add one coin `c`."
Because coins are reusable, we sweep amounts **upward**, so `dp[a - c]` may itself
already use coin `c` — that's what makes the supply unlimited.

Watch the table fill for `coins = [1, 2, 5]`. Each cell reaches back to a *smaller*
cell, one per coin:

```diagram
   amount:   0    1    2    3    4    5    6
   dp:     [ 0 ][ 1 ][ 1 ][ 2 ][ 2 ][ 1 ][ 2 ]
                                          ^
   filling dp[6], try each coin, land on a smaller solved cell:
       coin 1 -> dp[6-1] + 1 = dp[5] + 1 = 1 + 1 = 2
       coin 2 -> dp[6-2] + 1 = dp[4] + 1 = 2 + 1 = 3
       coin 5 -> dp[6-5] + 1 = dp[1] + 1 = 1 + 1 = 2
                    \____ each arrow points LEFT to an already-filled cell
   dp[6] = min(2, 3, 2) = 2      (e.g. 5 + 1)
```

And `dp[5]` was itself cheap because the coin 5 reaches all the way back to
`dp[0]`:

```diagram
   dp[5]:  coin 5 -> dp[5-5] + 1 = dp[0] + 1 = 0 + 1 = 1
                                    ^
                        base case: making zero needs no coins
```

## Complexity

- **Time:** about `amount × number_of_coins` — for each of the `amount`
  subproblems we try every coin once.
- **Space:** about `amount` for the table (the top-down version also uses about
  `amount` cache plus the recursion stack).

## Pitfalls

- Returning `0` instead of `-1` when it's impossible. Keep "unreachable" as a
  sentinel (`infinity`) all the way through, and convert to `-1` only at the end.
- `amount == 0` must return `0`, not `-1` — making nothing needs no coins.
- This is **fewest coins**, not **number of ways** (that's a different loop order —
  see Coin Change II). Don't confuse the two.
- Greedy (always grab the biggest coin) is wrong: for coins `[1, 3, 4]`, amount
  `6`, greedy gives `4 + 1 + 1 = 3` coins but `3 + 3 = 2` is better. You genuinely
  need the DP.

## Transfer

This is the **unbounded knapsack** shape: "reach a target using reusable items,
optimizing a count or value." The move — *guess the last item, recurse on the
leftover, cache by leftover amount* — reappears in Coin Change II (count ways),
[Word Break / 139](../0139-word-break/) (reach the end of a string using reusable
dictionary words), and Combination Sum.
