# 48. Rotate Image

**Pattern:** In-place matrix transform (transpose + reverse)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/rotate-image/

## The problem in plain words

You have a square grid of numbers. Turn the whole picture 90 degrees clockwise —
the top row becomes the right-hand column, the left column becomes the top row.
The catch: you must change the **same grid**, not build a new one.

## Start from the obvious

Where does each cell go? Rotating clockwise, the cell at `(row, col)` lands at
`(col, n-1-row)`. If you're allowed scratch space, just write every cell to its
destination in a fresh grid and copy it back.

```
result = new n x n grid
for r in range(n):
    for c in range(n):
        result[c][n-1-r] = matrix[r][c]
matrix = result
```

Correct, and it makes the target mapping explicit — which is exactly what you
need before doing it in place. But it allocates a second grid, and the problem
bans that. So the second grid is the waste to remove.

## Find the waste

The extra grid exists only because a direct 90-degree rotation moves cells in a
4-way cycle (top→right→bottom→left→top), and juggling a 4-cell cycle in place is
fiddly. The trick is to notice that the same end state is reachable by two
**pairwise swaps** that are each easy to do in place.

## The insight

A 90-degree clockwise rotation equals **transpose, then reverse each row**.

1. **Transpose** — swap `matrix[r][c]` with `matrix[c][r]`. This mirrors the grid
   over its main diagonal, so what were rows become columns.
2. **Reverse each row** — flip every row left-to-right.

```
1 2 3     transpose     1 4 7     reverse rows     7 4 1
4 5 6    ----------->    2 5 8    ------------->    8 5 2
7 8 9                    3 6 9                      9 6 3
```

Both steps only swap cells that already exist, so no extra grid is needed. When
transposing, only swap for `c > r` — otherwise you swap each pair twice and undo
your own work.

## Complexity

- **Time:** `O(n^2)` — you touch each of the `n^2` cells a constant number of
  times (once in the transpose, once in the row reversal).
- **Space:** `O(1)` — everything is done with in-place swaps; no grid allocated.

## Pitfalls

- **Transposing the whole grid** (all `r, c`) instead of just `c > r` — you swap
  each pair back to where it started and nothing changes.
- Forgetting the reverse step, or reversing **columns** instead of rows (that
  gives you a counter-clockwise rotation).
- Reassigning `matrix = result` at the end — that rebinds a local name and does
  **not** mutate the caller's grid. Copy row contents back with `matrix[r][:] = ...`.

## Transfer

The move "a hard permutation = a sequence of simple in-place swaps" carries over
to other grid transforms: transpose alone, horizontal/vertical flips, and
counter-clockwise rotation (reverse rows first, then transpose — or transpose then
reverse columns). It's the same toolkit used in
[Spiral Matrix / 54](../0054-spiral-matrix/) and
[Set Matrix Zeroes / 73](../0073-set-matrix-zeroes/), where the win is doing the
work inside the grid you were handed.
