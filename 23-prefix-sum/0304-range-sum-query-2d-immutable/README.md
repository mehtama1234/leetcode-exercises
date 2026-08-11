# 304. Range Sum Query 2D - Immutable

**Pattern:** 2D prefix sum (cumulative area + inclusion-exclusion)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/range-sum-query-2d-immutable/

## The problem in plain words

You get a grid of numbers that never changes. Then you're asked, repeatedly, for
the sum of a rectangle: everything from corner `(row1, col1)` to corner
`(row2, col2)`. Each answer should be fast, even for large rectangles and many
queries.

## Why this matters

This is the 1D prefix-sum idea lifted into two dimensions, and it turns a
question about an *area* into four lookups. The trick is to precompute, for every
cell, the sum of the whole top-left rectangle ending there. Any inner rectangle
is then recoverable by adding and subtracting a few of those corner totals.

The technique is famous in computer vision as the *integral image* (summed-area
table): it lets face detectors and blur/box filters read the brightness of any
window in constant time, so their cost doesn't grow with window size. Image
processing, heatmap and geospatial tools ("total activity in this map region"),
and OLAP data cubes that answer "sum over this multi-dimensional box" all lean on
the same precomputed cumulative grid.

What the good solution buys is scale-independent queries. Building the table is
`O(rows·cols)` once; after that, a `2×2` rectangle and a `1000×1000` rectangle
both cost the same four reads. When you fire many region queries over fixed data,
that flat per-query cost is the whole game.

## Start from the obvious

Sum the rectangle by looping over it.

```
def sumRegion(r1, c1, r2, c2):
    total = 0
    for r in range(r1, r2 + 1):
        for c in range(c1, c2 + 1):
            total += matrix[r][c]
    return total
```

Correct. But a large rectangle touches many cells, and overlapping queries re-add
the same cells again and again. That repetition is the waste.

## Find the waste

Notice that a lot of rectangles share the same *anchor* at the top-left corner
`(0,0)`. If we knew, for every bottom-right corner, the sum of the block from
`(0,0)` to that corner, we could describe any inner rectangle as a combination of
those blocks. In 1D we did `sum(0..right) - sum(0..left-1)`. In 2D we do the same
along both axes at once.

## The insight

Define `prefix[r][c]` = sum of all cells in the top-left rectangle from `(0,0)`
to `(r-1, c-1)` (a zero border on top and left makes the formulas clean). Build it
with inclusion-exclusion:

```
prefix[r+1][c+1] = matrix[r][c]
                 + prefix[r][c+1]   # block above
                 + prefix[r+1][c]   # block to the left
                 - prefix[r][c]     # overlap counted twice, remove once
```

Then the rectangle `(row1,col1)..(row2,col2)` is:

```
big  = prefix[row2+1][col2+1]   # whole top-left block ending at (row2,col2)
top  = prefix[row1][col2+1]     # strip above the rectangle
left = prefix[row2+1][col1]     # strip to the left of the rectangle
sum  = big - top - left + prefix[row1][col1]   # add corner back (removed twice)
```

Subtracting the top strip and the left strip removes their shared corner twice,
so you add it back once. Four reads, done.

## Complexity

- **Time:** `O(rows·cols)` to build the table once, then `O(1)` per query — always
  four array reads and three `±` operations, whatever the rectangle size.
- **Space:** `O(rows·cols)` for the `(rows+1)×(cols+1)` prefix grid.

## Pitfalls

- Getting inclusion-exclusion signs wrong. The mnemonic: **big − top − left +
  corner**. Forgetting the `+ corner` under-counts by exactly the overlap.
- Off-by-one on the `+1` shift. The zero border means query corners map to
  `prefix[row+1][col+1]`; the "remove" terms use the un-shifted `row1`/`col1`.
- Empty matrix: guard `cols = len(matrix[0]) if rows else 0` so the constructor
  doesn't crash.

## Transfer

This is the 2D sibling of [Range Sum Query / 303](../0303-range-sum-query-immutable/).
The inclusion-exclusion / summed-area idea reappears anywhere you need constant-time
box aggregates: integral images, 2D "count points in a rectangle" problems, and
DP tables where a state depends on a rectangular sum of earlier states.
