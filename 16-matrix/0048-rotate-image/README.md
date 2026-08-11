# 48. Rotate Image

**Pattern:** In-place matrix transform (turn a grid by moving cells within it)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/rotate-image/

## The problem in plain words

You have a square grid of numbers. Turn the whole picture 90 degrees clockwise:
the top row becomes the right column, the right column becomes the bottom row, and
so on. The catch is you must change the **same grid** you were handed — you're not
allowed to build a fresh one on the side.

```diagram
        rotate 90 degrees clockwise

     1  2  3                7  4  1
     4  5  6      -->        8  5  2
     7  8  9                9  6  3

   the old top row 1 2 3 becomes the new right column (top to bottom)
```

## Why this matters

Once you strip the story away, the task is: **rewrite where every cell lives, but
using the grid you already have as your only workspace.** A direct rotation moves
cells in a four-way loop (top goes to right, right goes to bottom, bottom goes to
left, left goes to top), and shuffling a four-cell loop by hand without dropping a
value is fiddly. The trick is finding two *simpler* moves that add up to the same
turn.

This exact move runs graphics and image code. Rotating a photo or a scanned page
90 degrees is this operation, and libraries do it as flip-plus-flip so they never
need a second copy of the image in memory. Phones auto-rotate camera frames the
same way. Transposing a matrix is a common step in number-crunching code and in
laying data out so the processor can read it faster. Game and CAD tools rotate
selections and tiles like this too.

What you're really saving is **memory**. The easy version allocates a second
grid the same size as the first, doubling how much space you use. On a big image
(millions of pixels) or a small device, that extra copy is the cost that hurts.

## Start from the obvious

Where does each cell go? For a clockwise turn, the cell at `(row, col)` lands at
`(col, n-1-row)`. If you're allowed scratch space, write every cell to its new
home in a fresh grid, then copy that back.

```diagram
   destination rule:  (row, col)  ->  (col, n-1-row)     n = 3

   (0,0)=1 -> (0,2)      (0,1)=2 -> (1,2)      (0,2)=3 -> (2,2)
   (1,0)=4 -> (0,1)      (1,1)=5 -> (1,1)      ...

   result = fresh n x n grid;  write each cell to its destination;  copy back
```

This is correct, and it's worth writing because it pins down the exact mapping.
But it allocates a whole second grid, and the problem bans that. So the second
grid is the waste to remove.

## Find the waste

The extra grid exists only because a straight rotation moves cells in that awkward
four-way loop, and doing a four-cell loop in place is where people drop values.
But the same final picture is reachable by two **pairwise swaps** — each one just
trades two cells that already exist, which is easy to do in place.

## The insight

A 90-degree clockwise rotation equals **transpose, then reverse each row.**

- **Transpose** means swap `matrix[r][c]` with `matrix[c][r]` — mirror the grid
  across the diagonal that runs top-left to bottom-right. Rows become columns.
- **Reverse each row** means flip every row left-to-right.

```diagram
   1 2 3      transpose      1 4 7     reverse each row     7 4 1
   4 5 6    ----------->     2 5 8    ----------------->    8 5 2
   7 8 9                     3 6 9                          9 6 3

   step 1 mirrors over the \ diagonal (5 stays put; 2<->4, 3<->7, 6<->8)
   step 2 flips each row:  1 4 7 -> 7 4 1
```

Both steps only swap cells that are already there, so no extra grid is needed.
One caution on the transpose: only swap when `c > r`. If you swap every pair, you
hit each pair twice and swap it right back, undoing your own work.

```diagram
   transpose: swap only the cells ABOVE the diagonal (c > r)

        c=0 c=1 c=2
   r=0   \  swap swap        the \ cells stay
   r=1      \  swap          swap each * exactly once
   r=2         \
```

## Complexity

- **Time: about n-squared steps.** You touch each of the `n x n` cells a fixed
  number of times — once when transposing, once when reversing its row.
- **Extra memory: constant.** Everything is done with in-place swaps; no second
  grid is allocated.

## Pitfalls

- **Transposing the whole grid** (every `r, c`) instead of only `c > r`. You swap
  each pair back to where it started, and nothing changes.
- Forgetting the reverse step, or reversing **columns** instead of rows — that
  gives you a counter-clockwise turn instead.
- Writing `matrix = result` at the end. That rebinds a local name and does **not**
  change the caller's grid. Copy the row contents back with `matrix[r][:] = ...`.

## Transfer

The move "a hard rearrangement equals a short sequence of simple in-place swaps"
carries over to other grid transforms: transpose on its own, horizontal or
vertical flips, and counter-clockwise rotation (reverse the rows first, then
transpose). It's the same in-place-grid discipline behind
[Spiral Matrix / 54](../0054-spiral-matrix/) and
[Set Matrix Zeroes / 73](../0073-set-matrix-zeroes/), where the win is doing the
work inside the grid you were given instead of copying it.
