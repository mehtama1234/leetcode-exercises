# 778. Swim in Rising Water

**Pattern:** Minimax path (Dijkstra with a `max` cost / binary search + DFS)
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/swim-in-rising-water/

## The problem in plain words

You're on an `n×n` grid where each cell has an elevation. Time `t` means the
water level is `t`, and you can stand on any cell whose elevation is `≤ t`.
Starting at the top-left `(0,0)`, you want to reach the bottom-right
`(n-1, n-1)`. Moving between adjacent cells is instant — the only thing that
holds you up is *waiting for the water to rise* high enough to cover the tallest
cell on your route. Return the earliest time you can arrive.

## Why this matters

The key reframe: the "cost" of a path here isn't the *sum* of the cells you
cross — it's the **maximum** cell on it, the single tallest barrier you must wait
out. You want the path whose highest point is as low as possible. That's a
**minimax path** (also called a bottleneck shortest path), and it's a genuinely
different objective from ordinary shortest path.

This shows up wherever a route is limited by its worst link, not its total.
Network routing that maximizes the *bottleneck bandwidth* of a path (the slowest
hop determines throughput) is minimax. Choosing a hiking or shipping route that
minimizes the *highest* pass or the *deepest* ford is this. Reliability
engineering asks for the path whose weakest component is as strong as possible —
same shape.

What the good solution buys is recognizing that a small tweak to a standard tool
solves it. Swap Dijkstra's `+` for `max` and it finds minimax paths directly in
`O(n² log n)`, versus trying to enumerate routes.

## Start from the obvious

The honest brute force: try every possible arrival time `t` from low to high; for
each, check with a flood-fill whether start connects to end using only cells
`≤ t`. First `t` that works is the answer.

```
for t = 0, 1, 2, ...:
    if DFS/BFS from (0,0) using only cells <= t reaches (n-1,n-1):
        return t
```

Correct, but it re-runs a full grid search for every candidate `t`, and `t` can
be as large as `n²-1`. That's a lot of repeated flood-fills.

## Find the waste

Two independent improvements fall out of two observations.

**Observation 1 — reachability is monotonic in `t`.** If you can cross at level
`t`, you can cross at any higher level (more cells are open, never fewer). A
monotonic yes/no function is the textbook signal to **binary search** the
threshold instead of scanning every `t`. That cuts the number of flood-fills from
`O(n²)` to `O(log n²)`.

**Observation 2 — you don't need to fix `t` first at all.** The cost of reaching
a cell is "the tallest barrier on the best route to it." If you grow outward
always expanding the reachable cell with the *smallest max-barrier-so-far*, the
first time you pop the destination, that barrier value **is** the answer. That's
Dijkstra — with `max` in place of `+`.

## The insight

**Dijkstra with a min-max cost.** Relax neighbors with
`max(cost_so_far, neighbor_elevation)` instead of a sum. The min-heap always
expands the frontier cell needing the lowest water level; popping the goal gives
the minimal possible "worst barrier":

```
heap = [(grid[0][0], 0, 0)]
while heap:
    t, r, c = pop-min
    if (r,c) is goal: return t
    for each neighbor: push (max(t, grid[neighbor]), neighbor)
```

**Binary search + DFS** (shown alongside) makes the minimax nature explicit:
binary-search the smallest `t` for which a DFS restricted to cells `≤ t` connects
start to end.

## Complexity

- **Dijkstra:** `O(n² log n)` time — each of `n²` cells enters the heap once,
  each heap op `O(log n²) = O(log n)`. Space `O(n²)`.
- **Binary search + DFS:** `O(n² log(n²))` time — `O(log n²)` iterations, each a
  full `O(n²)` flood-fill. Space `O(n²)`.

Both are far better than scanning every water level.

## Pitfalls

- Using **sum** instead of **max** when relaxing — that solves a different
  problem (cheapest total, not lowest bottleneck).
- Forgetting the **start cell's own elevation**: seed the cost with `grid[0][0]`,
  and in the binary-search version bail if `grid[0][0] > t`.
- Marking a cell visited only *after* popping (Dijkstra) — mark on pop, and skip
  stale duplicates, or you'll reprocess cells.
- The **1×1 grid**: the answer is just `grid[0][0]`.

## Transfer

"Dijkstra where the path cost is a `max` (or `min`) instead of a sum" is the
reusable minimax-path pattern —
[Path With Minimum Effort / 1631](https://leetcode.com/problems/path-with-minimum-effort/)
and
[Swim / Path of maximum bottleneck](https://leetcode.com/problems/path-with-maximum-probability/)
are close siblings. The "binary search on a monotonic yes/no answer, verified by
a reachability check" idea transfers to any problem where feasibility only
improves as a threshold loosens. Compare the heap machinery with
[Network Delay Time / 743](../0743-network-delay-time/).
