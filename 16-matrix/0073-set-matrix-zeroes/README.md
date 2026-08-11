# 73. Set Matrix Zeroes

**Pattern:** In-place marking (reuse the grid as its own scratch space)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/set-matrix-zeroes/

## The problem in plain words

Scan the grid. Wherever you find a 0, that 0's whole row and whole column must
become all zeros. Do it to the **same grid**, and ideally without allocating extra
storage that grows with the grid's size.

## Start from the obvious

The first trap is to zero a row the instant you see a 0. Don't — the zeros you
write get re-read as you continue scanning, so they trigger *more* rows and columns
to blank. That chain reaction floods the whole grid.

The honest fix is a two-pass plan with a marker for each row and column:

```
zero_rows, zero_cols = set(), set()
for r, c:
    if matrix[r][c] == 0:
        zero_rows.add(r); zero_cols.add(c)
for r, c:
    if r in zero_rows or c in zero_cols:
        matrix[r][c] = 0
```

First record everything from the *original* grid, then act on it. Correct — but it
spends `O(m + n)` extra memory on those two sets. That memory is the waste.

## Find the waste

Those marker sets store one bit per row and one bit per column: "does this row/
column contain a zero?" But the grid already has a spare place to keep one bit per
row and one bit per column — its **first row** and **first column**. If we
repurpose them as the marker arrays, we need no separate storage at all.

## The insight

Let **row 0** hold the column markers and **column 0** hold the row markers.

Their only clash is cell `(0,0)`, which both would want. So pull column 0 out into
a single boolean flag and treat the rest uniformly:

1. **Mark.** Scan every cell. On a 0 at `(r, c)`, set `matrix[r][0] = 0` and
   `matrix[0][c] = 0`. If the 0 is in column 0, set a separate `first_col_zero`
   flag instead of relying on the shared corner.
2. **Blank the interior** (`r >= 1, c >= 1`) using those markers.
3. **Blank the first row and first column last.** The first row goes to zero iff
   `matrix[0][0]` was marked; the first column goes to zero iff `first_col_zero`
   was set.

Doing the interior before the border is what keeps the markers readable until the
moment you're done with them.

## Complexity

- **Time:** `O(m*n)` — a constant number of passes over the grid.
- **Space:** `O(1)` extra — one boolean; the markers live inside the grid itself.

## Pitfalls

- **Zeroing rows/columns as you first see them** — the classic chain reaction that
  blanks everything. Separate marking from acting.
- **The `(0,0)` overlap.** One corner cell can't be the marker for both row 0 and
  column 0. Track column 0 with its own flag.
- **Order of the final steps.** If you blank row 0 or column 0 *before* using them
  to fix the interior, you erase your own markers. Interior first, border last.
- Assuming there's at least one zero — a grid with none must come out unchanged.

## Transfer

The reusable trick is "store your bookkeeping *inside* the data structure you're
already given to hit O(1) space." It shows up whenever a marker array mirrors a
dimension the input already has — e.g. using the array's own indices as a seen-set
in [First Missing Positive / 41](https://leetcode.com/problems/first-missing-positive/),
and the general in-place grid work in [Rotate Image / 48](../0048-rotate-image/).
