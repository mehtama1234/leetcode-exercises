# 312. Burst Balloons

**Pattern:** 2-D dynamic programming (interval DP — split on the *last* action)
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/burst-balloons/

## The problem in plain words

Each balloon holds a number. When you burst balloon `i`, you earn
`nums[left] * nums[i] * nums[right]`, where left and right are its neighbors *at that
moment* (a missing end counts as 1). After it pops, its neighbors become adjacent.
Pop every balloon in some order to earn the most coins.

```diagram
   nums = [3, 1, 5, 8]   (pad ends with virtual 1's: [1, 3, 1, 5, 8, 1])

   burst 1: 3*1*5 = 15   -> [1, 3, 5, 8, 1]
   burst 5: 3*5*8 = 120  -> [1, 3, 8, 1]
   burst 3: 1*3*8 = 24   -> [1, 8, 1]
   burst 8: 1*8*1 = 8
   total = 167   (this order is optimal)
```

## Why this matters

The natural instinct — decide which balloon to pop *first* — is a trap. The moment
you pop one, everyone's neighbors shift, so the subproblems overlap in a tangled way
you can't cleanly separate. The fix is to think backwards: in a range of balloons,
decide which one pops **last**. When balloon `k` is last, everything else in the
range is already gone, so its neighbors are exactly the fixed walls on either side of
the range. That pins down its score and cleanly splits the range into two
independent pieces — the balloons left of `k` and the balloons right of `k`.

"Split on the last (or top-level) operation so the two sides stop interfering" is the
signature move of *interval DP*, and it recurs in matrix-chain multiplication,
optimal parenthesization, and parsing.

## Start from the obvious

Try every possible burst order. That's `n!` orders — hopeless past a handful of
balloons. Worse, popping first makes overlapping subproblems messy to reuse.

The reframing: pad the array with a `1` on each end, and think about *open* ranges
`(l, r)` — the balloons strictly between walls `l` and `r`. For that range, try each
`k` inside it as the last balloon to pop. When `k` is last, its neighbors are the
walls `l` and `r`, and the two sides `(l, k)` and `(k, r)` are solved independently.

```diagram
   range (l ......... r), pick k as the LAST to burst inside it

     l   [ ... left side ... ]   k   [ ... right side ... ]   r

   k is last, so left side and right side are already empty when k pops:
   score(k as last) = nums[l]*nums[k]*nums[r] + best(l, k) + best(k, r)
                       \_____ walls are l and r _____/   \____ two subranges ____/
```

## The insight — an interval grid

Let `dp[l][r]` = most coins from bursting every balloon strictly between walls `l`
and `r`. Fill it by **increasing gap** (the distance `r - l`), so short ranges are
solved before the longer ranges that depend on them.

```diagram
   balloons padded: index 0..5 = [1, 3, 1, 5, 8, 1]
   dp[l][r], only l < r used (upper triangle)

            r:  1    2    3    4    5
       l=0  |  0 |  3 | 30 |159 |167 |    grow along diagonals (gap = r-l)
       l=1  |    |  0 | 15 |135 |159 |
       l=2  |    |    |  0 | 40 | 48 |
       l=3  |    |    |    |  0 | 40 |
       l=4  |    |    |    |    |  0 |
   adjacent-wall ranges (gap 1) hold no balloons = 0;
   the gap grows outward toward dp[0][5] = 167.
```

Now watch cell `dp[l][r]` fill. It scans every `k` between the walls, and for each
`k` it reads two already-finished cells — one to its **left** in the row
(`dp[l][k]`) and one **below** in the column (`dp[k][r]`) — then keeps the best:

```diagram
   filling dp[l][r]: try each k in (l, r) as last

        dp[l][k]   (same row, shorter range on the left)
             \
              \         dp[k][r]   (same column, shorter range on the right)
               \       /
                v     v
        dp[l][r] = max over k of  nums[l]*nums[k]*nums[r] + dp[l][k] + dp[k][r]

   both dp[l][k] and dp[k][r] are shorter ranges, already filled -> safe to read
```

The bottom-line answer is `dp[0][n-1]` over the padded array — the whole span
between the two virtual walls.

## Complexity

- **Time: about n³ steps.** There are about n² ranges, and each scans up to n choices
  of `k`. Doubling n multiplies the work by roughly eight.
- **Extra memory: about n²** for the range grid.

## Pitfalls

- Splitting on the *first* balloon to pop. Then neighbors keep shifting and the two
  sides aren't independent. Split on the *last* one.
- Forgetting the padding `1`s. They give the edge balloons a well-defined neighbor
  and let you use fixed walls `l` and `r`.
- Filling in the wrong order. A range needs its sub-ranges done first, so iterate by
  increasing gap, not by row.

## Transfer

The reusable skeleton is *interval DP: `dp[l][r]` over a range, split on the last (or
top-level) operation `k` so the two sides become independent, fill by increasing
length.* Siblings: [Matrix Chain Multiplication](https://en.wikipedia.org/wiki/Matrix_chain_multiplication)
(the canonical form), [Minimum Cost to Merge Stones / 1000](https://leetcode.com/problems/minimum-cost-to-merge-stones/),
[Remove Boxes / 546](https://leetcode.com/problems/remove-boxes/), and
[Guess Number Higher or Lower II / 375](https://leetcode.com/problems/guess-number-higher-or-lower-ii/).
