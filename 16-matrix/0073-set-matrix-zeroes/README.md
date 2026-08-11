# 73. Set Matrix Zeroes

**Pattern:** In-place marking (use the grid itself as your notepad)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/set-matrix-zeroes/

## The problem in plain words

Scan the grid. Wherever you find a `0`, that cell's whole row and whole column
must become all zeros. Do it to the **same grid**, and ideally without adding
storage that grows with the grid's size.

```diagram
     1 1 1                1 0 1
     1 0 1     -->        0 0 0
     1 1 1                1 0 1

   the single 0 sits at (1,1), so row 1 and column 1 both go to zero
```

## Why this matters

Two ideas are hiding in this problem. First: **keep your notes inside the data
you were already handed**, so you don't pay for extra storage. Second: **write in
two separate passes — first record what's true, then act on it** — so your own
edits don't get read back in and corrupt the answer.

Reusing the input as a notepad is a real memory technique. In-place array code
encodes "have I seen this?" into the array's own indices or sign bits to avoid a
side structure — valuable on small devices and in tight number-crunching loops
where an extra allocation would blow the processor's cache. The "record, then
change" split is the same hazard-avoidance behind double-buffering and applying a
list of edits: read the old state fully before you start overwriting, or you feed
your own changes back into the work.

What you save is the **extra row-marker and column-marker storage** the easy fix
spends. Reusing row 0 and column 0 as those markers removes it, keeping the work
to a handful of straight passes with constant extra memory.

## Start from the obvious

The first trap is to zero a row the instant you see a `0`. Don't — the zeros you
write get re-read as you keep scanning, so they trigger *more* rows and columns to
blank. That chain reaction floods the whole grid.

```diagram
   BAD: zeroing on sight, scanning left to right, top to bottom

     1 0 1      see 0 at (0,1)      1 0 1      now (1,1)==0 too, so
     1 1 1  ->  zero row 0 & col 1  0 0 0  ->  it blanks row 1 as well
     1 1 1                          1 0 1      ...and it spreads

   the zeros you wrote get mistaken for original zeros
```

The honest fix is a two-pass plan with a marker for each row and column:

```diagram
   pass 1 (record from the ORIGINAL grid):
      for every cell that is 0 at (r,c):  zero_rows.add(r);  zero_cols.add(c)

   pass 2 (act):
      set cell (r,c) to 0 if r is in zero_rows OR c is in zero_cols
```

Correct — but it spends extra memory on those two sets, one entry per row and one
per column. That memory is the waste.

## Find the waste

Those two sets hold one bit per row and one bit per column: "does this row (or
column) contain a zero?" But the grid already has a spare place to keep exactly
one bit per row and one bit per column — its **first row** and its **first
column**. Repurpose those as the markers and you need no separate storage at all.

## The insight

Let **row 0** hold the column markers and **column 0** hold the row markers.

The only clash is cell `(0,0)`, which both would want to use. So pull column 0
out into a single true/false flag and treat everything else uniformly:

1. **Mark.** Scan every cell. On a `0` at `(r, c)`, set `matrix[r][0] = 0` and
   `matrix[0][c] = 0`. If that zero is in column 0, set a separate
   `first_col_zero` flag instead of leaning on the shared corner.
2. **Blank the inside** (`r >= 1, c >= 1`) using those markers.
3. **Blank the first row and first column last.** Row 0 goes to zero only if
   `matrix[0][0]` got marked; column 0 goes to zero only if `first_col_zero` was
   set.

```diagram
   markers live on the edges.  reading down col 0 and across row 0:

        c0  c1  c2  c3
   r0 [ M | *   *   * ]   <- row 0 marks which COLUMNS must zero
   r1 [ * | .   .   . ]
   r2 [ * | .   .   . ]        col 0 marks which ROWS must zero
        ^
     col 0 marks rows; corner M and a separate flag settle the (0,0) clash

   do the inner cells (.) first, then the edges (* and M) last
```

Doing the inside before the edges is what keeps the markers readable right up to
the moment you're done with them.

## Complexity

- **Time: about m times n steps.** A fixed number of passes over the grid.
- **Extra memory: constant.** One true/false flag; the markers live inside the
  grid itself.

## Pitfalls

- **Zeroing rows or columns the moment you first see them** — the chain reaction
  that blanks everything. Keep marking separate from acting.
- **The `(0,0)` overlap.** One corner cell can't be the marker for both row 0 and
  column 0. Track column 0 with its own flag.
- **Order of the final steps.** If you blank row 0 or column 0 *before* using them
  to fix the inside, you erase your own markers. Inside first, edges last.
- Assuming there's at least one zero — a grid with none must come out unchanged.

## Transfer

The reusable trick is "store your notes *inside* the data structure you were
already given, to keep extra memory constant." It shows up whenever a marker array
mirrors a dimension the input already has — for example using the array's own
indices as a seen-set in
[First Missing Positive / 41](https://leetcode.com/problems/first-missing-positive/),
and it shares the in-place-grid discipline of
[Rotate Image / 48](../0048-rotate-image/).
