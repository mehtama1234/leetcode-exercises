# 417. Pacific Atlantic Water Flow

**Pattern:** Multi-source flood fill from the boundary + set intersection
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/pacific-atlantic-water-flow/

## The problem in plain words

You have a grid of heights. Rain on any cell flows to a side-neighbor only if that
neighbor is **not higher** (water goes downhill or stays level). The Pacific laps
the top and left edges of the grid; the Atlantic laps the bottom and right edges.
Find every cell whose water can reach **both** oceans.

## Why this matters

The core idea here is **reachability, computed backward from the destinations instead of forward from every source** — plus intersecting two reachable sets. The fundamental operation is multi-source flood fill seeded from a whole boundary at once.

The "search from the goal, not from every start" reversal is a real optimization pattern. Terrain and hydrology tools compute watersheds and drainage basins exactly this way — which cells drain to which outlet. Multi-source BFS from many seeds at once powers "nearest facility" maps (distance from every cell to the closest exit/hospital/tower), fire- or infection-spread simulations, and shortest-path-to-any-target queries. Reversing an all-pairs question into one sweep from the targets is the same trick behind computing reachability from sinks in dataflow analysis.

What you're solving for is **killing redundant recomputation**: asking "can each cell reach the ocean?" independently re-explores shared downhill paths, giving `O((rows·cols)²)`. Flooding inward from each ocean once, then intersecting, drops it to a single linear pass per ocean.

## Start from the obvious

Ask the question literally: for each cell, can water starting there reach the
Pacific? The Atlantic? So you'd run a downhill search from every single cell:

```
for each cell:
    if downhill-search(cell) touches Pacific and downhill-search(cell) touches Atlantic:
        keep it
```

That's `rows × cols` searches, each up to `O(rows × cols)`, so `O((rows·cols)^2)`.
And it's wildly repetitive: a peak in the mountains gets re-explored by every
lowland cell that eventually drains through it.

## Find the waste

The repetition is the clue. "Can cell X drain into the Pacific?" and "can cell Y
drain into the Pacific?" share almost all of their downhill path. We're recomputing
the same reachability again and again.

## The insight

**Reverse the flow.** Water reaching an ocean is the same as: standing at the
ocean's edge and being able to climb *uphill* back to that cell without ever
stepping down. So flood **inward from the border**:

- Start from every Pacific-edge cell at once. Move to a neighbor only if it is
  `>=` the current height (uphill, since forward the water would flow back down to
  us). Everything you can reach is a cell that drains to the Pacific.
- Do the same starting from every Atlantic-edge cell.

Now each ocean needs just **one** multi-source flood over the grid. A cell that
both floods reach can drain to both oceans — the answer is the **intersection** of
the two reachable sets.

## Complexity

- **Time:** `O(rows × cols)`. Two floods; each visits every cell at most once (the
  `reachable` set prevents re-entry). The final intersection is linear too.
- **Space:** `O(rows × cols)` for the two reachable sets and the traversal stack.

## Pitfalls

- **Comparison direction.** In the *reverse* traversal you move to neighbors that
  are **higher or equal**, not lower. Getting this backwards inverts the whole
  answer.
- **`>=`, not `>`.** Equal heights let water pass, so level neighbors count.
- **Corners.** Top-left/bottom-right cells sit on both a top/bottom and a
  left/right edge; seeding all border cells handles them naturally.
- **Empty grid.** Guard `not heights or not heights[0]` before indexing.

## Transfer

"Don't search from every source — search once from the destination(s) backward" is
the reusable idea, and multi-source BFS from a whole border shows up in
[Rotting Oranges / 994](https://leetcode.com/problems/rotting-oranges/),
[Walls and Gates / 286](https://leetcode.com/problems/walls-and-gates/), and
[Surrounded Regions / 130](https://leetcode.com/problems/surrounded-regions/),
which also floods inward from the edges to decide interior cells.
