# 304. Range Sum Query 2D - Immutable

**Pattern:** 2D prefix sum (running area + add-and-subtract corners)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/range-sum-query-2d-immutable/

## The problem in plain words

You get a grid of numbers that never changes. Then you're asked, over and over, for
the sum of a rectangle: everything from corner `(row1, col1)` to corner
`(row2, col2)`. Each answer should be fast, even for large rectangles and many
questions.

```diagram
   matrix                 want the sum of the boxed rectangle
                          (row1,col1)=(2,1)  (row2,col2)=(4,3)
       3 0 1 4 2
       5 6 3 2 1
       1[2 0 1]5
       4[1 0 1]7
       1[0 3 0]5

   2 + 0 + 1 + 1 + 0 + 1 + 0 + 3 + 0 = 8   ->  answer 8
```

## Why this matters

This is the 1D prefix-sum idea lifted into two dimensions, and it turns a question
about an *area* into four lookups. The idea is to precompute, for every cell, the
sum of the whole top-left rectangle ending there. Any inner rectangle is then
recoverable by adding and subtracting a few of those corner totals.

The technique is famous in computer vision as the *integral image* (a grid of
running sums): it lets face detectors and box-blur filters read the brightness of
any window in constant time, so their cost doesn't grow with window size. Image
processing, heatmap and map tools ("total activity in this region"), and data cubes
that answer "sum over this multi-dimensional box" all lean on the same precomputed
running grid.

What the good solution buys is queries whose cost doesn't depend on rectangle size.
Building the table is about `rows·cols` once; after that, a `2×2` rectangle and a
`1000×1000` rectangle both cost the same four reads.

## Start from the obvious

Sum the rectangle by looping over it.

```diagram
   def sumRegion(r1, c1, r2, c2):
       total = 0
       for r in r1 .. r2:
           for c in c1 .. c2:
               total += matrix[r][c]
       return total
```

Correct. But a large rectangle touches many cells, and overlapping queries re-add
the same cells again and again. That repetition is the waste.

## Find the waste

A lot of rectangles share the same *anchor* at the top-left corner `(0,0)`. If we
knew, for every bottom-right corner, the sum of the block from `(0,0)` to that
corner, we could describe any inner rectangle as a combination of those blocks. In
1D we did `sum(0..right) - sum(0..left-1)`. In 2D we do the same along both axes at
once — which means adding and subtracting overlapping blocks.

## The insight

Define `prefix[r][c]` = sum of all cells in the top-left rectangle from `(0,0)` to
`(r-1, c-1)`. A zero border on top and left keeps the formulas clean. Build it by
adding the cell to the block above and the block to the left, then removing the
part they both counted.

```diagram
   building prefix[r+1][c+1]:

       +-----------+-----+
       |           |     |
       |  above    |     |   above = prefix[r][c+1]
       |  block    |     |   left  = prefix[r+1][c]
       +-----------+-----+   the two blocks OVERLAP on the small
       |   left    |cell |   top-left square = prefix[r][c],
       |   block   |r,c  |   counted twice -> subtract it once
       +-----------+-----+

   prefix[r+1][c+1] = matrix[r][c]
                    + prefix[r][c+1]    # block above
                    + prefix[r+1][c]    # block to the left
                    - prefix[r][c]      # overlap removed once
```

Then any rectangle is four corner totals, again with one overlap to add back.

```diagram
   rectangle (row1,col1)..(row2,col2):

       big   = prefix[row2+1][col2+1]   whole top-left block ending bottom-right
       - top = prefix[row1][col2+1]     strip ABOVE the rectangle
       - left= prefix[row2+1][col1]     strip LEFT of the rectangle
       + corner = prefix[row1][col1]    top-left corner, removed by BOTH strips

   sum = big - top - left + corner

   subtracting top and left removes their shared corner twice,
   so add it back once.  four reads, done.
```

## Complexity

- **Time: about rows·cols to build once, then four reads per query.** Always four
  reads and three plus/minus operations, whatever the rectangle size.
- **Extra memory: about rows·cols** for the `(rows+1)×(cols+1)` prefix grid.

## Pitfalls

- Getting the add/subtract signs wrong. The mnemonic: **big − top − left +
  corner**. Forgetting the `+ corner` under-counts by exactly the overlap.
- Off-by-one on the `+1` shift. The zero border means query corners map to
  `prefix[row+1][col+1]`; the "remove" terms use the un-shifted `row1`/`col1`.
- Empty matrix: guard `cols = len(matrix[0]) if rows else 0` so the constructor
  doesn't crash.

## Transfer

This is the 2D sibling of [Range Sum Query / 303](../0303-range-sum-query-immutable/).
The add-and-subtract-corners idea (also called a summed-area table) reappears
anywhere you need constant-time box totals: integral images, 2D "count points in a
rectangle" problems, and DP tables where a state depends on a rectangular sum of
earlier states.
