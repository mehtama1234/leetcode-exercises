# 200. Number of Islands

**Pattern:** Grid as a graph / flood fill (connected components)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/number-of-islands/

## The problem in plain words

You have a rectangle of `1`s (land) and `0`s (water). Land cells that touch
side-by-side (up/down/left/right — never diagonally) form one island. Count how
many separate islands there are.

## Why this matters

The real problem is **finding connected components in a grid** — the fundamental operation is flood fill: from a seed, reach everything transitively linked to it, mark it, and never touch it twice.

This is a workhorse, not a toy. Image editing tools use it for the paint-bucket fill and the magic-wand selection (a region of similar pixels). Image processing and computer vision use connected-component labeling to count and measure blobs — cells under a microscope, defects on a manufacturing line, segmented objects in a photo. Games use flood fill to reveal the empty area in Minesweeper and to compute reachable territory or fog-of-war. Even `mkfs`/disk tools reason about connected free regions this way.

What you're solving for is **doing it in one linear pass with no double-counting**. The key resource trick — "sink the land" by overwriting visited cells instead of keeping a separate `visited` set — buys you the visited-marker for free, keeping memory to the traversal stack. Every cell is entered once, so the whole scan is linear in the grid.

## Start from the obvious

The honest first thought: "an island is a blob of connected land, so let me find
the blobs." A grid *is* a graph in disguise — each land cell is a node, and it
has an edge to each land cell directly above, below, left, or right of it.
Counting islands is then just counting connected components of that graph.

```
count = 0
for each cell:
    if cell is land and not yet visited:
        count += 1
        visit the whole blob it belongs to   # so we don't recount it
```

The only real work is "visit the whole blob."

## The insight

Walk the grid cell by cell. Most cells you either skip (water) or have already
been swallowed by a previous blob. The moment you land on a `1` you haven't seen
before, you *know* it starts a brand-new island — if it belonged to an island you
already counted, that island's flood fill would have reached it. So:

1. Bump the island counter by one.
2. Flood-fill outward from this cell — DFS/BFS through connected land — and mark
   every cell you reach as visited.

The neat trick: instead of a separate `visited` set, just **sink the land** —
overwrite each `1` with `0` as you visit it. A sunk cell is water, so it can
never restart or rejoin an island. The grid itself becomes the visited marker.

## Find the waste

If you used a plain recursive DFS, a single giant island (say a 300×300 grid of
all land) recurses ~90,000 deep and blows Python's recursion limit. Swapping to
an **explicit stack** removes that ceiling for free — same algorithm, no crash.

## Complexity

- **Time:** `O(rows × cols)`. The outer scan touches each cell once; the flood
  fill also touches each cell at most once total (a sunk cell is never re-entered),
  so the whole thing is linear in the number of cells.
- **Space:** `O(rows × cols)` worst case — the DFS stack can hold most of the grid
  when it's one big island (e.g. a snake-shaped blob).

## Pitfalls

- **Diagonals don't connect.** `[["1","0"],["0","1"]]` is *two* islands, not one.
  Only the 4 orthogonal neighbors are edges.
- **Recursion depth.** Recursive DFS overflows on large single islands — use an
  explicit stack (or BFS with a queue).
- **Mutating the caller's grid.** Sinking edits the input in place. In tests we
  pass a deep copy so the original grid survives for the next assertion.
- **Empty input.** An empty grid, or an empty first row, must return `0` — check
  before indexing.

## Transfer

"Scan the grid, and every time you hit an unvisited region, flood-fill it and
count/measure it" is the reusable move. It powers
[Max Area of Island / 695](https://leetcode.com/problems/max-area-of-island/),
[Surrounded Regions / 130](https://leetcode.com/problems/surrounded-regions/),
and [Number of Connected Components / 323](../0323-number-of-connected-components-in-an-undirected-graph/)
— the same connected-components idea on an explicit graph instead of a grid.
