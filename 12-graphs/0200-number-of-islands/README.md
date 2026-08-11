# 200. Number of Islands

**Pattern:** Grid as a graph / flood fill (paint every connected blob at once)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/number-of-islands/

## The problem in plain words

You have a rectangle of `1`s (land) and `0`s (water). Land cells that touch
side-by-side — up, down, left, right, never diagonally — belong to the same
island. Count how many separate islands there are.

```diagram
   grid:        1 1 0 0 0
                1 1 0 0 0
                0 0 1 0 0
                0 0 0 1 1

   the top-left 1s all touch  -> island A
   the lone 1 in the middle   -> island B
   the two 1s at bottom-right -> island C
                                          answer: 3
```

## Why this matters

A grid like this is a graph in disguise. Each land cell is a dot, and it has a
line to each land cell right next to it. "How many islands?" is really "how many
separate clumps does this graph split into?"

The reusable move is **flood fill**: pick a starting cell, then spread out to
everything connected to it, marking each cell as you go so you never touch it
twice. This is the paint-bucket tool in an image editor — click one pixel and the
whole matching region fills. It counts blobs under a microscope, defects on a
factory line, and the empty area that opens up when you click a blank square in
Minesweeper. Same spreading, different clothes.

What you are solving for is doing it in **one pass with no double-counting**. Get
that right and the work grows in step with the grid instead of exploding.

## Start from the obvious

The honest first thought: an island is a clump of connected land, so go find the
clumps. Walk the grid cell by cell. Most cells you skip — they are water, or a
clump you already dealt with. But the moment you step onto a `1` you have not seen
yet, that has to be a **brand-new** island. If it belonged to an island you
already counted, that island's fill would have reached it and marked it.

```diagram
   count = 0
   for each cell:
       if cell is land AND not yet visited:
           count += 1              <- a fresh clump starts here
           flood-fill the whole clump so we never recount it
```

The only real work is that last line: visit the whole clump.

## The insight

Here is the neat part. You do not need a separate "visited" notebook. When you
step onto a land cell, **sink it** — overwrite the `1` with a `0`. A sunk cell is
now water, so it can never start a new island or get pulled into another one. The
grid itself becomes your record of what you have seen.

```diagram
   land at (0,0)?  yes -> count=1, start sinking

   1 1 0        0 1 0        0 0 0        0 0 0
   1 1 0   ->   1 1 0   ->   0 0 0   ->   0 0 0
   0 0 0        0 0 0        0 0 0        0 0 0
   ^sink here   spread to    neighbors    whole clump
                touching 1s  sink too     is now water

   the outer scan moves on; every cell here is 0, so nothing restarts
```

The spread itself is a walk through connected land. You can use a stack (go deep
first) or a queue (spread in rings) — both reach the same cells. The moment the
walk runs dry, that island is fully sunk.

## Find the waste

One trap sits in the spread. If you write it as a plain recursive function that
calls itself for each neighbor, a single huge island — picture a 300×300 grid of
all land — nests 90,000 calls deep and blows Python's recursion limit. Swap the
recursion for an **explicit stack** (a list you push neighbors onto and pop from)
and the ceiling is gone. Same algorithm, no crash.

## Complexity

- **Time: about rows × cols steps.** The outer scan touches each cell once. The
  flood fill also touches each cell at most once total, because a sunk cell is
  never re-entered. So the whole thing grows in step with the number of cells.
- **Extra memory: about rows × cols in the worst case.** The stack can hold most
  of the grid when it is one big snake-shaped island.

## Pitfalls

- **Diagonals don't connect.** `[["1","0"],["0","1"]]` is *two* islands. Only the
  4 straight neighbors count as edges.
- **Recursion depth.** Recursive flood fill overflows on one large island — use an
  explicit stack (or a queue).
- **Mutating the caller's grid.** Sinking edits the input in place. In tests we
  pass a copy so the original survives for the next check.
- **Empty input.** An empty grid, or an empty first row, must return `0` — check
  before you index.

## Transfer

"Scan the grid, and every time you hit an unvisited region, flood-fill it and
count or measure it" is the reusable move. It powers
[Max Area of Island / 695](https://leetcode.com/problems/max-area-of-island/),
[Surrounded Regions / 130](https://leetcode.com/problems/surrounded-regions/),
and [Number of Connected Components / 323](../0323-number-of-connected-components-in-an-undirected-graph/)
— the same connected-clump idea on an explicit graph instead of a grid.
