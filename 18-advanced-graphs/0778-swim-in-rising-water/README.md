# 778. Swim in Rising Water

**Pattern:** Lowest-worst-barrier path (Dijkstra with a `max` cost / binary search + DFS)
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/swim-in-rising-water/

## The problem in plain words

You're on an `n×n` grid where each cell has a height. At time `t` the water level
is `t`, and you can stand on any cell whose height is `≤ t`. You start at the
top-left `(0,0)` and want to reach the bottom-right `(n-1, n-1)`. Stepping between
neighboring cells is instant — the only thing that holds you up is *waiting for the
water to rise* high enough to cover the tallest cell on your route. Return the
earliest time you can arrive.

```diagram
   grid heights:              step-across is free; the wait is the cost

       0  2                    to go 0,0 -> 1,1 you must clear the
       1  3                    tallest cell on your path.

   path 0 -> 1 -> 3 :  tallest = 3   ->  wait until t=3
   path 0 -> 2 -> 3 :  tallest = 3   ->  wait until t=3
   every route to the corner passes a 3   ->  answer = 3
```

## Why this matters

The reframe is the whole thing: the "cost" of a path here isn't the *sum* of the
cells you cross — it is the **highest** cell on it, the single tallest barrier you
must wait out. You want the path whose highest point is as low as possible. That
is a *lowest-worst-barrier path* (also called a bottleneck path), and it is a
genuinely different goal from ordinary shortest path.

This shows up wherever a route is limited by its worst link, not its total. Network
routing that wants the best *bottleneck bandwidth* of a path (the slowest hop caps
throughput) is this shape. Choosing a hiking or shipping route that keeps the
*highest* pass or the *deepest* ford as low as possible is this. Reliability work
asks for the path whose weakest component is as strong as possible — same shape.

What the good solution buys is noticing that a small tweak to a standard tool
solves it. Swap Dijkstra's `+` for `max` and it finds these paths directly in
about `n^2·log n` steps, instead of trying to list out routes.

## Start from the obvious

The honest brute force: try every arrival time `t` from low to high; for each, run
a flood-fill to check whether start connects to end using only cells `≤ t`. The
first `t` that works is the answer.

```diagram
   for t = 0, 1, 2, ... :
       can a flood-fill from (0,0) using only cells <= t
       reach (n-1, n-1) ?    ->  first yes is the answer
```

Correct, but it re-runs a full grid search for every candidate `t`, and `t` can be
as large as `n^2 - 1`. That is a lot of repeated flood-fills.

## Find the waste

Two separate improvements fall out of two observations.

**Observation 1 — reachability only ever gets better as `t` rises.** If you can
cross at level `t`, you can cross at any higher level (more cells open, never
fewer). A yes/no test that flips once, from no to yes, is the textbook signal to
**binary search** the threshold instead of scanning every `t`.

```diagram
   t:        0   1   2   3   4   5   6
   reaches?  N   N   N   Y   Y   Y   Y
                         ^
              first Y — binary search jumps straight to it
              instead of trying 0,1,2,3 one by one
```

**Observation 2 — you don't need to fix `t` first at all.** The cost of reaching a
cell is "the tallest barrier on the best route to it." If you grow outward always
expanding the reachable cell with the *smallest worst-barrier-so-far*, the first
time you pop the destination, that barrier value **is** the answer. That is
Dijkstra — with `max` in place of `+`.

## The insight

**Dijkstra with a lowest-worst-barrier cost.** When you reach a neighbor, its cost
is `max(cost_so_far, neighbor_height)` instead of a sum. The min-heap always
expands the frontier cell needing the lowest water level; popping the goal gives
the smallest possible "worst barrier."

```diagram
   grid:  0 2      heap holds (worst barrier to reach cell, r, c)
          1 3

   heap = [(0, 0,0)]
   pop (0, 0,0)  lock start.  neighbors:
       (1,0) height 1 -> push (max(0,1)=1, 1,0)
       (0,1) height 2 -> push (max(0,2)=2, 0,1)
   heap = [(1,1,0),(2,0,1)]

   pop (1, 1,0)  lock it.  neighbor (1,1) height 3 -> push (max(1,3)=3, 1,1)
   heap = [(2,0,1),(3,1,1)]

   pop (2, 0,1)  lock it.  neighbor (1,1) -> push (max(2,3)=3, 1,1)
   heap = [(3,1,1),(3,1,1)]

   pop (3, 1,1)  that's the goal  ->  answer = 3
```

**Binary search + DFS** (shown alongside in the solution) makes the structure
explicit: binary-search the smallest `t` for which a DFS restricted to cells `≤ t`
connects start to end.

## Complexity

- **Dijkstra: about `n^2·log n`.** Each of `n^2` cells enters the heap once, each
  heap operation about `log(n^2) = log n`. Extra memory about `n^2`.
- **Binary search + DFS: about `n^2·log(n^2)`.** About `log(n^2)` rounds, each a
  full `n^2` flood-fill. Extra memory about `n^2`.

Both are far better than scanning every water level.

## Pitfalls

- Using **sum** instead of **max** when reaching a neighbor — that solves a
  different problem (cheapest total, not lowest worst barrier).
- Forgetting the **start cell's own height**: seed the cost with `grid[0][0]`, and
  in the binary-search version bail out if `grid[0][0] > t`.
- Marking a cell used only *after* popping (Dijkstra): mark on pop and skip stale
  duplicates, or you'll reprocess cells.
- The **1×1 grid**: the answer is just `grid[0][0]`.

## Transfer

"Dijkstra where the path cost is a `max` (or `min`) instead of a sum" is the
reusable lowest-worst-barrier pattern —
[Path With Minimum Effort / 1631](https://leetcode.com/problems/path-with-minimum-effort/)
and
[Path with Maximum Probability / 1514](https://leetcode.com/problems/path-with-maximum-probability/)
are close siblings. The "binary search on a yes/no answer that flips once, checked
by a reachability test" idea transfers to any problem where feasibility only
improves as a threshold loosens. Compare the heap machinery with
[Network Delay Time / 743](../0743-network-delay-time/).
