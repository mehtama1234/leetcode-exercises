# 62. Unique Paths

**Pattern:** Dynamic programming (grid, sum of two neighbors)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/unique-paths/

## The problem in plain words

A robot starts in the top-left cell of an `m × n` grid and wants to reach the
bottom-right cell. It can only ever step **right** or **down**. How many different
paths get it there?

## Why this matters

The real operation here is **counting the number of ways to reach a state by summing the ways to reach the states that lead into it** — the additive core of dynamic programming. You're not walking paths one by one; you're building the count into each cell from its predecessors and reusing it.

Where "count/aggregate over paths through a grid or DAG" genuinely appears:

- **Probability and reliability** — summing weighted paths through a lattice is exactly how you compute reaching probabilities in Markov chains or grid random walks.
- **Sequence alignment** — the same "come from up/left/diagonal" grid underlies edit-distance and DNA alignment scoring.
- **Routing and layout** — counting monotone routes on a chip or map grid, and cost-minimizing variants (swap `+` for `min`) for cheapest-path planning.

What the good solution buys is a jump from **exponential recomputation to `O(m·n)` time**, and the rolling-row trick trades the full grid for **`O(n)` memory** — the resource that matters when the grid is large or you only need the final count.

## Start from the obvious

The honest first idea is to just walk every possibility: from each cell, try going
right and try going down, and count the times you land on the goal.

```
def count(i, j):
    if i == m-1 and j == n-1: return 1   # arrived
    if i >= m or j >= n:       return 0   # walked off the grid
    return count(i+1, j) + count(i, j+1)  # try down, try right
```

Correct — but it explores a branching tree of moves, and the same cell gets
recounted from countless different partial paths. That's exponential.

## Find the waste

The recursion keeps asking "how many paths from cell `(i, j)` to the end?" for the
*same* `(i, j)` over and over. There are only `m × n` cells, so there are only
`m × n` distinct subproblems. Solve each once.

Let's flip it to count paths *into* a cell instead of out of it. Define:

> `dp[i][j]` = number of distinct paths from the start to cell `(i, j)`.

How can the robot arrive at `(i, j)`? Its last move was either a step **down**
from `(i-1, j)` or a step **right** from `(i, j-1)`. Those are the only two doors
in, and no path uses both as its final step, so the counts simply add:

```
dp[i][j] = dp[i-1][j] + dp[i][j-1]
```

The edges are the base cases: the entire top row and left column are `1`. There's
exactly one way to reach any top-edge cell (keep going right the whole time) and
one way to reach any left-edge cell (keep going down). Fill the grid top-to-bottom,
left-to-right, and the answer is the bottom-right cell.

## The space optimization

`dp[i][j]` only reads the cell **above** it and the cell **to its left** — never
anything two rows back. So the whole grid is overkill; one row is enough.

Keep a single array `row`, start it as all `1`s (the top row). Then sweep it
left-to-right, `m-1` times. At the instant you update column `j`:

- `row[j]` still holds its value from the previous pass = the cell **above**, and
- `row[j-1]` was already updated this pass = the cell **to the left**.

So `row[j] += row[j-1]` quietly computes `dp[i-1][j] + dp[i][j-1]` in place. After
all passes, `row[n-1]` is the answer. Space drops from `O(m·n)` to `O(n)`.

## Complexity

- **Brute-force recursion:** `O(2^(m+n))` time.
- **2-D DP:** `O(m·n)` time, `O(m·n)` space.
- **Rolling row:** `O(m·n)` time, `O(n)` space.

(There's also a pure-math answer: the robot makes `m-1` downs and `n-1` rights in
some order, so the count is the binomial `C(m+n-2, m-1)`. The DP is the more
transferable lesson.)

## Pitfalls

- Getting the base cases wrong: the top row and left column are `1`, not `0`. If
  they were `0`, every cell would stay `0`.
- Grid dimensions: `m` is rows, `n` is columns; the answer is `dp[m-1][n-1]`.
- In the rolling version, sweeping the row **left to right** is essential — that
  order is what guarantees `row[j-1]` is already the new value while `row[j]` is
  still the old one.

## Transfer

The "sum the ways in from the neighbors you're allowed to come from" idea extends
directly to [Unique Paths II / 63](https://leetcode.com/problems/unique-paths-ii/)
(set blocked cells to `0`) and
[Minimum Path Sum / 64](https://leetcode.com/problems/minimum-path-sum/) (swap the
`+` for a `min` over the same two neighbors, plus the cell's cost). Any grid where
you move in a fixed set of directions and combine sub-results from adjacent cells
is this same pattern.
