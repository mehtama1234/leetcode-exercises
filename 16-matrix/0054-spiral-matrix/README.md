# 54. Spiral Matrix

**Pattern:** Shrinking boundaries (peel the grid one ring at a time)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/spiral-matrix/

## The problem in plain words

Read out every number in the grid, but not row by row — follow a spiral. Go right
across the top, down the right side, left across the bottom, up the left side,
then tighten inward by one layer and do the same thing again, until nothing is
left.

```diagram
   spiral order of a 3x3 grid:

     1 -> 2 -> 3
               |
     4 -> 5    6      answer: 1 2 3 6 9 8 7 4 5
     ^    |    v
     7 <- 8 <- 9

   right across the top, down the right, left along the bottom,
   up the left, then the lone center cell 5
```

## Why this matters

The real task is: **walk a 2D region in an unusual order while keeping track of
what's left to visit — using only a few numbers, not a full map of every cell.**
The obvious way is to keep a grid marking where you've been. But because the
spiral always eats the outermost unvisited ring, the part you've visited is never
a ragged shape — it's always a clean rectangular frame closing in. That means
four numbers describe the whole situation exactly.

Ring-by-ring traversal is a real pattern. Image tools sometimes walk pixels in
ring orders so nearby data stays together in memory or so a picture can load
progressively from the outside in. Grid algorithms often process a matrix in
concentric layers or trim its border. The bookkeeping here — four walls closing
inward — is the same discipline behind any "spiral fill" and behind peeling a
matrix layer by layer in math code.

What you save is **the whole visited-grid and the per-step turn check.** Four
boundary numbers replace a marker for every cell, dropping the extra memory from
"one bit per cell" to "four integers" while still emitting each cell exactly once.

## Start from the obvious

The honest first thought is to walk a little robot. Keep a `(row, col)` position
and a direction, step forward each move, and turn clockwise whenever the next cell
is off the grid or already visited.

```diagram
   visited = grid of False;  heading = right

   step, mark visited, then:
      if the cell ahead is off-grid or already visited:
          turn right   (heading right -> down -> left -> up -> right)
      move forward

   turning happens exactly at the corners and edges of the spiral
```

This works and is easy to believe. But it drags a whole `visited` grid around
just to answer "have I been here?", and it re-checks the turn condition on every
single step. That bookkeeping is the waste.

## Find the waste

You never actually need a per-cell visited map. The spiral always peels the
**outermost unvisited ring** first, so the visited part is never a ragged blob —
it's always a clean rectangular frame closing in from all four sides. That means
four numbers fully describe what's left: the `top`, `bottom`, `left`, and `right`
walls.

## The insight

Bound the unvisited region with four walls and peel one ring per loop:

1. Walk the **top** wall left to right, then move `top` down by one.
2. Walk the **right** wall top to bottom, then move `right` in by one.
3. Walk the **bottom** wall right to left, then move `bottom` up by one.
4. Walk the **left** wall bottom to top, then move `left` in by one.

Repeat while `top <= bottom` and `left <= right`. No visited grid, no direction
tracking — four numbers shrinking toward each other.

```diagram
   4x4 grid, walls close in.  start: top=0 bottom=3 left=0 right=3

     [ 1  2  3  4]    walk top row 1 2 3 4,  top -> 1
     [ 5  6  7  8]    walk right col 8 12,   right -> 2
     [ 9 10 11 12]    walk bottom 11 10 9,   bottom -> 2
     [13 14 15 16]    walk left col 5,       left -> 1

   after one ring, the live region is just [ 6  7 ] with
                                            [10 11 ]  top=1 bottom=2 left=1 right=2
   next ring: 6 7, then 11, then 10 (guards stop a re-walk)
```

The two mid-loop guards, `if top <= bottom` and `if left <= right`, handle
non-square grids. After the top row and right column are consumed, a single
leftover row or column must not be walked a second time in reverse.

## Complexity

- **Time: about m times n steps.** Every cell is appended exactly once.
- **Extra memory: constant.** Only the four boundary numbers. The output list you
  return doesn't count as working space.

## Pitfalls

- **Dropping the guards.** On a single leftover row or column you'll walk it once
  forward and once backward, printing duplicates.
- Empty input: `[]` or `[[]]` must return `[]` before you ever touch `matrix[0]`.
- Off-by-one in the reverse loops: the bottom row is `range(right, left-1, -1)`
  and the left column is `range(bottom, top-1, -1)` — those `-1` endpoints are
  meant to be inclusive.
- Mixing up `m` (rows) and `n` (columns) when the grid isn't square.

## Transfer

The shrinking-boundaries idea — describe the still-active region with a few edge
numbers instead of a full visited map — comes back in
[Spiral Matrix II / 59](https://leetcode.com/problems/spiral-matrix-ii/), which
*fills* a spiral, and in layer-by-layer grid processing in general. It's a cousin
of the in-place ring reasoning in [Rotate Image / 48](../0048-rotate-image/).
