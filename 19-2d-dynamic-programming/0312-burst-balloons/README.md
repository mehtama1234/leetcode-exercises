# 312. Burst Balloons

**Pattern:** 2-D dynamic programming (interval DP — split on the *last* action)
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/burst-balloons/

## The problem in plain words

A row of balloons, each with a number. When you burst balloon `i` you earn
`nums[left] × nums[i] × nums[right]`, where `left` and `right` are its neighbours
*at that moment* (a missing edge counts as 1). After bursting, the gap closes and
neighbours change. Choose an order to burst all of them that earns the most coins.

## Why this matters

The teachable idea is *interval DP with a reversal of intuition: don't ask what
happens first, ask what happens last.* The naive "which balloon do I pop first?"
framing is a trap — popping first rewires everyone's neighbours, so subproblems
overlap in a tangled, non-independent way. Flipping to "which balloon pops **last**
in this range?" is what makes the two sides independent, and that "split on the final
operation" trick is the reusable jewel here.

The pattern generalizes to any "combine a range in the best order, where each merge's
cost depends on the pieces at its edges." Matrix-chain multiplication (parenthesize
to minimize multiplications) is the classic industrial version. Optimal file/segment
merging, building an optimal binary search tree, and cost-of-joining problems in
query planners are all interval DPs with this same "pick the last/topmost split"
structure.

What the good solution buys is `O(n³)` time — polynomial — versus the `n!` of trying
every burst order, which is intractable past a dozen balloons.

## Start from the obvious

Try every possible next balloon to burst, recurse on what's left, take the max.
But "what's left" isn't two clean halves — bursting a middle balloon merges its
neighbours, so the remaining balloons don't split into independent groups. The
subproblems overlap in a way you can't cleanly memoize by "set of remaining
balloons" without exponential state. This framing fights you.

## Find the waste — flip first to last

Pad the array with virtual `1`s at both ends. Consider the open interval strictly
between walls `l` and `r`. Ask: **which balloon `k` in this interval is the *last* to
burst?** When `k` is last, every other balloon in the interval is already gone, so at
that instant `k`'s neighbours are exactly the fixed walls `l` and `r`. It earns
`nums[l] × nums[k] × nums[r]` — and, crucially, the balloons to `k`'s left and right
were burst *within their own subintervals*, `(l, k)` and `(k, r)`, which are now
**independent** because `l`, `k`, `r` are permanent walls for them.

```
best(l, r) = max over k in (l, r) of
             nums[l]*nums[k]*nums[r] + best(l, k) + best(k, r)
```

## The insight (tabulate)

`dp[l][r]` = most coins from bursting everything strictly between walls `l` and `r`.
Fill by increasing gap `r - l`, so both `dp[l][k]` and `dp[k][r]` (shorter intervals)
are ready:

```
for gap in 2..n-1:
    for l in 0..n-1-gap:
        r = l + gap
        dp[l][r] = max(nums[l]*nums[k]*nums[r] + dp[l][k] + dp[k][r]
                       for k in l+1..r-1)
```

Answer is `dp[0][n-1]` over the fully padded array.

## Complexity

- **Time:** `O(n³)` — `O(n²)` intervals, each scanning up to `n` choices of last
  balloon.
- **Space:** `O(n²)` for the interval table.

## Pitfalls

- **Thinking "first" instead of "last."** First-to-burst does not give independent
  subproblems; last-to-burst does. This single flip is the whole problem.
- The multiplication uses the **walls** `l` and `r`, not `k-1`/`k+1` — because when
  `k` is last, the walls *are* its neighbours.
- Pad with `1`s on both ends so edge balloons have a defined neighbour, and treat
  `(l, r)` as the *open* interval (base case `r - l < 2` earns 0).
- Empty input returns 0.

## Transfer

The reusable skeleton is *interval DP: `dp[l][r]` over a range, split on the last (or
top-level) operation `k` so the two sides become independent, fill by increasing
length.* Siblings: [Matrix Chain Multiplication](https://en.wikipedia.org/wiki/Matrix_chain_multiplication)
(the canonical form), [Minimum Cost to Merge Stones / 1000](https://leetcode.com/problems/minimum-cost-to-merge-stones/),
[Remove Boxes / 546](https://leetcode.com/problems/remove-boxes/), and
[Guess Number Higher or Lower II / 375](https://leetcode.com/problems/guess-number-higher-or-lower-ii/).
