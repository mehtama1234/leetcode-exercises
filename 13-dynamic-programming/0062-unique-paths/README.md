# 62. Unique Paths

**Pattern:** Dynamic programming (grid, a cell's count is the sum of two neighbors)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/unique-paths/

## The problem in plain words

A robot starts in the top-left cell of an `m × n` grid and wants the bottom-right
cell. It can only step **right** or **down**. How many different paths get it
there?

```diagram
   3 x 3 grid, one sample path (R = right, D = down):

     S -> . -> .
               |
     .    .    v
               .
               |
     .    .    v
               G

   this is ONE of the paths;  the answer counts all of them
```

## Why this matters

The move to keep is **count the ways to reach a state by adding up the ways to
reach the states that lead into it.** You don't walk paths one at a time; you
build the count into each cell from the cells feeding it, and reuse it. That's the
additive core of dynamic programming.

The same "sum over the ways in" appears when you total weighted paths through a
lattice to get reaching probabilities in a random walk, in the come-from-up-or-left
grid under DNA alignment scoring, and in counting monotone routes on a chip or map
(swap `+` for `min` and it becomes cheapest-path planning).

## Start from the obvious

The honest first idea: walk every possibility. From each cell try going right and
try going down, and count the times you land on the goal.

```
def count(i, j):
    if i == m-1 and j == n-1: return 1   # arrived
    if i >= m or j >= n:       return 0   # walked off the grid
    return count(i+1, j) + count(i, j+1)  # down, then right
```

Correct — but it explores a branching tree of moves, and the same cell gets
recounted from countless partial paths. That's exponential.

## Find the waste

The recursion keeps asking "how many paths from `(i, j)` to the end?" for the
*same* `(i, j)` again and again. There are only `m × n` cells, so only `m × n`
distinct subproblems. Solve each once.

Flip it to count paths *into* a cell instead of out of it:

> `dp[i][j]` = the number of distinct paths from the start to cell `(i, j)`.

How can the robot arrive at `(i, j)`? Its last move was a step **down** from
`(i-1, j)` or a step **right** from `(i, j-1)`. Those are the only two doors in,
and no path uses both as its final step, so the counts add:

```
dp[i][j] = dp[i-1][j] + dp[i][j-1]
```

The edges are the base cases: the whole top row and left column are `1` — one way
to reach any top-edge cell (all rights) and one way to reach any left-edge cell
(all downs).

```diagram
   3 x 3 grid, filled top-to-bottom, left-to-right:

         c0  c1  c2
     r0   1   1   1
     r1   1   2   3
     r2   1   3   6   <- answer

   how the cell (r1,c1)=2 was built:

           above = dp[r0][c1] = 1
                       |
                       v
     left=1  ------> [ 1 + 1 = 2 ]

   dp[i][j] = (cell above) + (cell to the left)
```

## The space optimization

`dp[i][j]` reads only the cell **above** and the cell **to its left** — never two
rows back. So the full grid is overkill; one row is enough.

Keep a single array `row`, start it all `1`s (the top row), then sweep it left to
right, `m-1` times. At the instant you touch column `j`:

- `row[j]` still holds its value from the previous pass = the cell **above**, and
- `row[j-1]` was already updated this pass = the cell **to the left**.

```diagram
   one rolling row, sweeping left to right:

   start (top row):   row = [ 1 , 1 , 1 ]

   pass 1 (row r1):
     j=1:  row[1] += row[0]   -> 1 + 1 = 2    row = [1, 2, 1]
     j=2:  row[2] += row[1]   -> 1 + 2 = 3    row = [1, 2, 3]

   pass 2 (row r2):
     j=1:  row[1] += row[0]   -> 2 + 1 = 3    row = [1, 3, 3]
     j=2:  row[2] += row[1]   -> 3 + 3 = 6    row = [1, 3, 6]

   answer = row[n-1] = 6

   at column j:   row[j]  = old value = cell ABOVE
                  row[j-1]= new value = cell to the LEFT
```

So `row[j] += row[j-1]` quietly computes `dp[i-1][j] + dp[i][j-1]` in place, and
memory drops from `m × n` down to about `n`.

## Complexity

- **Brute-force recursion:** exponential, about `2^(m+n)`.
- **2-D DP:** about m × n steps and m × n memory.
- **Rolling row:** about m × n steps, about `n` memory.

(There's also a pure-math answer: the robot makes `m-1` downs and `n-1` rights in
some order, so the count is the binomial `C(m+n-2, m-1)`. The DP is the more
transferable lesson.)

## Pitfalls

- Getting the base cases wrong: the top row and left column are `1`, not `0`. Set
  them to `0` and every cell stays `0`.
- Grid dimensions: `m` is rows, `n` is columns; the answer is `dp[m-1][n-1]`.
- In the rolling version, sweeping **left to right** is essential — that order is
  what keeps `row[j-1]` already-new while `row[j]` is still-old.

## Transfer

The "sum the ways in from the neighbors you're allowed to come from" idea extends
straight to [Unique Paths II / 63](https://leetcode.com/problems/unique-paths-ii/)
(set blocked cells to `0`) and
[Minimum Path Sum / 64](https://leetcode.com/problems/minimum-path-sum/) (swap `+`
for a `min` over the same two neighbors, plus the cell's cost). Any grid where you
move in a fixed set of directions and combine sub-results from adjacent cells is
this same pattern.
