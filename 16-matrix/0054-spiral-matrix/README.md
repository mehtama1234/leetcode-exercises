# 54. Spiral Matrix

**Pattern:** Boundary shrinking (peel the grid ring by ring)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/spiral-matrix/

## The problem in plain words

Read out every number in the grid, but not row by row — follow a spiral. Go right
across the top, down the right side, left across the bottom, up the left side, then
tighten inward one layer and do it again, until nothing is left.

## Start from the obvious

The honest first thought is to literally simulate a walker. Keep a `(row, col)`
position and a direction, step forward, and turn clockwise whenever the next cell
is off the grid or already visited.

```
visited = grid of False
dr, dc = 0, 1            # start heading right
for _ in range(m*n):
    record current cell, mark visited
    if next cell is out of bounds or visited:
        turn right      # (dr, dc) = (dc, -dr)
    step forward
```

This works and is easy to believe. But it carries a whole `visited` grid just to
answer "have I been here?", and it re-checks a turn condition on every single step.
That bookkeeping is the waste.

## Find the waste

You never actually need a per-cell `visited` map. The spiral always peels the
**outermost unvisited ring** first, so the visited region is never ragged — it's
always a clean rectangular frame closing in from all four sides. That means four
numbers fully describe what's left: the `top`, `bottom`, `left`, and `right` walls.

## The insight

Bound the unvisited region with four walls and peel one ring per loop:

1. Walk the **top** wall left→right, then move `top` down.
2. Walk the **right** wall top→bottom, then move `right` in.
3. Walk the **bottom** wall right→left, then move `bottom` up.
4. Walk the **left** wall bottom→top, then move `left` in.

Repeat while `top <= bottom and left <= right`. No visited grid, no direction
vector — just four integers shrinking toward each other.

The two mid-loop guards `if top <= bottom` and `if left <= right` handle
non-square grids: after the top row and right column are consumed, a lone
remaining row or column must not be traversed a second time in reverse.

## Complexity

- **Time:** `O(m*n)` — every cell is appended exactly once.
- **Space:** `O(1)` extra — only four boundary integers (the output list itself
  doesn't count as working space).

## Pitfalls

- **Omitting the guards** — on a single leftover row or column you'll walk it once
  forward and once backward, emitting duplicates.
- Empty input: `[]` or `[[]]` must return `[]` before touching `matrix[0]`.
- Off-by-one in the reverse loops: bottom row is `range(right, left-1, -1)` and
  left column is `range(bottom, top-1, -1)` — the `-1` endpoints are inclusive.
- Confusing `m` (rows) and `n` (columns) when the grid isn't square.

## Transfer

The "shrinking boundaries" idea — describe the still-active region with a few
edge indices instead of a full visited map — reappears in
[Spiral Matrix II / 59](https://leetcode.com/problems/spiral-matrix-ii/) (fill a
spiral) and in layer-by-layer grid processing generally. It's a cousin of the
in-place ring reasoning in [Rotate Image / 48](../0048-rotate-image/).
