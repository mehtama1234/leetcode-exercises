# 494. Target Sum

**Pattern:** 2-D dynamic programming (subset-sum counting reduction)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/target-sum/

## The problem in plain words

You have a list of non-negative numbers and a target. Put a `+` or `-` in front of
each number, then add them up. Count how many of the `+/-` choices land exactly on
the target.

```diagram
   nums = [1, 1, 1, 1, 1]     target = 3

   +1+1+1+1-1 = 3      +1+1+1-1+1 = 3      +1+1-1+1+1 = 3
   +1-1+1+1+1 = 3      -1+1+1+1+1 = 3

   -> 5 ways
```

## Why this matters

There are two ideas worth taking. First: the state that matters is the *running sum*
you've reached, not the exact path you took to get there. Many different sign
choices reach the same partial sum, and from there the rest of the problem is
identical — so remember the sum, not the history. Second: a little algebra turns a
`+/-` problem into a plain "which numbers do I pick?" problem.

Split the numbers into the ones you make positive (call their total `P`) and the
ones you make negative (total `N`). Then:

```diagram
   P - N = target          (the signs must hit the target)
   P + N = total           (every number is in one group)
   -------------------- add the two lines
   2P = target + total  ->  P = (target + total) / 2
```

So the whole question becomes: *how many subsets of the numbers add up to `P`?*
That's a clean counting problem, and it drops the running-sum axis entirely.

## Start from the obvious

Branch on every sign: for each number, recurse twice — once adding it, once
subtracting it. When you run off the end, you scored a hit if the running sum equals
the target. Correct, but it's a binary tree of depth `n`, so about 2ⁿ leaves.
Doubling the count of numbers squares the work.

```diagram
   go(i, running):
              (i, s)
              /      \
        +nums[i]    -nums[i]
        (i+1, s+x)  (i+1, s-x)

   two different prefixes can reach the SAME running sum,
   yet each re-explores its whole subtree -> wasted repeats
```

## The insight — a counting grid

After the algebra, count subsets summing to `P`. Build `dp[i][sum]` = number of
subsets of the first `i` numbers that total `sum`. Each number is either left out or
put in.

```diagram
   nums = [1, 1, 1]    want subsets summing to some target sum

              sum:  0    1    2    3
        {}         | 1 |  0 |  0 |  0 |   only the empty subset makes 0
        +num1      | 1 |  1 |  0 |  0 |
        +num2      | 1 |  2 |  1 |  0 |
        +num3      | 1 |  3 |  3 |  1 |
```

Each cell reads two neighbors in the row above — the cell straight **up** (skip this
number, same sum) and the cell **up and to the left** by this number's value (put it
in, so before adding it you needed `sum - value`):

```diagram
   filling dp[i][sum], number value = x

        up = dp[i-1][sum]        up-left = dp[i-1][sum - x]
        "skip x"                 "include x"
             \                      /
              \                    /
               v                  v
                 dp[i][sum] = up + up-left

   example: dp[+num2][1] = dp[+num1][1] + dp[+num1][0] = 1 + 1 = 2
```

Because each row only needs the row above and cells to its left, roll it to one
array and sweep `sum` downward so each number is used at most once — that's the
version in `solution.py`. First, two gates: if `target + total` is odd or `|target|`
exceeds `total`, no split exists, so the answer is 0.

## Complexity

- **Time: about n × S steps**, where `S = (target + total)/2` is the needed subset
  sum. One add per grid cell.
- **Extra memory: about S** in the rolled 1-D version — one row across sums.

## Pitfalls

- Skipping the parity/range check. If `target + total` is odd, `P` isn't a whole
  number and the answer is 0; likewise if `|target| > total`.
- Sweeping `sum` upward in the 1-D roll. That reuses a number multiple times — this
  is 0/1 (each number once), so sweep downward.
- Zeros. A `0` can take `+` or `-`, so each zero doubles the count; the subset-sum
  form handles this correctly as long as you include zeros in `total`.

## Transfer

The reusable moves are *(a) state = running aggregate, not path*, and *(b) turn a
signed/partition problem into subset-sum by algebra*. Siblings:
[Partition Equal Subset Sum / 416](https://leetcode.com/problems/partition-equal-subset-sum/)
(does a subset hit total/2?), [Coin Change II / 518](../0518-coin-change-ii/)
(the unbounded counting cousin), and
[Last Stone Weight II / 1049](https://leetcode.com/problems/last-stone-weight-ii/)
(same `+/-` reduction, minimizing the leftover).
