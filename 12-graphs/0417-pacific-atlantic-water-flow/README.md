# 417. Pacific Atlantic Water Flow

**Pattern:** Flood inward from the borders + intersect the two reachable sets
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/pacific-atlantic-water-flow/

## The problem in plain words

You have a grid of heights. Rain on a cell flows to a side-neighbor only if that
neighbor is **not higher** — water goes downhill or stays level. The Pacific laps
the top and left edges; the Atlantic laps the bottom and right edges. Find every
cell whose water can reach **both** oceans.

```diagram
   Pacific along top + left            Atlantic along bottom + right

     P P P P P                              . . . . A
     P . . . .          heights            . . . . A
     P . . . .          in the middle      . . . . A
     P . . . .                             . . . . A
     P . . . .                             A A A A A

   a cell counts only if water from it can slide to BOTH labels
```

## Why this matters

The reusable idea is **reachability worked out backward from the destinations
instead of forward from every start** — then intersecting two reachable sets.

Asking "from this cell, can water reach the ocean?" one cell at a time re-walks the
same downhill paths over and over: a peak in the mountains gets re-explored by every
lowland cell that eventually drains through it. Flip it. Water reaching an ocean is
the same as: stand at the ocean edge and climb **uphill** back to the cell. Do that
climb once from each ocean's whole border, and every cell you reach is one that
drains to that ocean.

That "search from the goal, not from every start" reversal is a real pattern.
Terrain tools compute drainage basins this way — which cells drain to which outlet.
Flooding from many seeds at once also powers "distance to the nearest exit" maps and
fire- or infection-spread simulations.

## Start from the obvious

Ask the question literally: for each cell, can water starting there reach the
Pacific? The Atlantic? That means a downhill search from every single cell.

```diagram
   for each cell:
       if downhill-search reaches Pacific AND downhill-search reaches Atlantic:
           keep it

   that is (rows x cols) searches, each up to (rows x cols) steps
   -> about (rows x cols) squared work.  and wildly repetitive.
```

## Find the waste

The repetition is the clue. "Can cell X drain to the Pacific?" and "can cell Y drain
to the Pacific?" share almost their whole downhill path. We recompute the same
reachability again and again.

## The insight — flood inward from each ocean

**Reverse the flow.** Water reaching an ocean is the same as standing at the ocean's
edge and climbing uphill back to the cell without ever stepping down. So flood
inward from the border, moving to a neighbor only when it is `>=` the current height
— uphill, because forward the water would flow back down to us.

```diagram
   heights:                 flood UP from the Pacific border (top row + left col):

     1 2 2 3 5              start on every P cell, step only to a >= neighbor
     3 2 3 4 4
     2 4 5 3 1              e.g. from (0,0)=1 you can step to (1,0)=3 (3 >= 1),
     6 7 1 4 5                   then to (3,0)=6, and so on, climbing uphill
     5 1 1 2 4

   mark every cell this reverse-flood touches: it drains to the Pacific
```

Do the same starting from every Atlantic-edge cell. Now each ocean needs just
**one** flood over the grid. A cell that both floods reach can drain to both oceans
— the answer is the overlap of the two reachable sets.

```diagram
   pacific-reachable set   P        atlantic-reachable set   A

   answer =  P and A  (cells in BOTH)

           P P             A         cells marked in both floods are the
         P                 A         ones you return, e.g. (0,4), (2,2),
         P                           (3,0), (4,0) ... on the sample grid
```

## Complexity

- **Time: about rows × cols steps.** Two floods, and each visits every cell at most
  once because a "reached" set blocks re-entry. The overlap step is linear too.
- **Extra memory: about rows × cols** for the two reached sets and the traversal
  stack.

## Pitfalls

- **Comparison direction.** In the *reverse* walk you move to neighbors that are
  **higher or equal**, not lower. Getting this backwards flips the whole answer.
- **`>=`, not `>`.** Equal heights let water pass, so level neighbors count.
- **Corners.** The top-left and bottom-right cells sit on two edges at once; seeding
  every border cell handles them on its own.
- **Empty grid.** Guard `not heights or not heights[0]` before you index.

## Transfer

"Don't search from every source — search once from the destination(s) backward" is
the reusable idea, and flooding from a whole border at once shows up in
[Rotting Oranges / 994](https://leetcode.com/problems/rotting-oranges/),
[Walls and Gates / 286](https://leetcode.com/problems/walls-and-gates/), and
[Surrounded Regions / 130](https://leetcode.com/problems/surrounded-regions/),
which also floods inward from the edges to decide the interior cells.
