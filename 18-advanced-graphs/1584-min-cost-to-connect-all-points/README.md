# 1584. Min Cost to Connect All Points

**Pattern:** Minimum Spanning Tree (Prim's heap / Kruskal's union-find)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/min-cost-to-connect-all-points/

## The problem in plain words

You have points on a grid. You may connect any two of them, and doing so costs
their Manhattan distance (`|x1-x2| + |y1-y2|`). Connect them all — every point
reachable from every other — for the least total cost. You don't need a direct
wire between every pair; you just need the whole thing to hang together as one
connected piece.

That "connect everything as cheaply as possible, no wasted wires" is exactly a
**Minimum Spanning Tree**.

## Why this matters

The deeper operation is: *given a set of things and the cost to link any pair,
what is the cheapest set of links that ties them all into one network?* The
answer always has a specific shape — a tree: it touches every node, has no
cycles (a cycle means one redundant, removable link), and uses exactly `n-1`
edges.

This is not academic. Laying fiber, water pipes, or power lines to connect towns
for minimal trenching is the original MST problem. Clustering algorithms build a
minimum spanning tree over data points and cut the longest edges to separate
groups. Chip designers route wires between components to minimize total wire
length. Network engineers use spanning trees to connect switches without loops.

What the good solution buys is provable optimality cheaply. Trying combinations
of edges is exponential; both MST algorithms here run in roughly `O(E log E)` and
are *guaranteed* to return the true minimum thanks to the greedy "cheapest safe
edge is always safe" property.

## Start from the obvious

The honest brute force: try every subset of possible connections, keep the ones
that make everything connected, and take the cheapest such subset.

```
best = infinity
for every subset S of the possible edges:
    if S connects all points and has no leftover:
        best = min(best, total_cost(S))
```

With `n` points there are up to `n(n-1)/2` edges and `2^(edges)` subsets —
astronomically slow. But there's a beautiful shortcut hiding in the structure.

## The insight

The greedy fact that makes MST tractable: **the single cheapest edge crossing
from your current connected piece to the outside is always safe to add.** It can
never cause you to overspend later. Two algorithms exploit this:

**Prim — grow one tree.** Start from any point. Repeatedly add the cheapest edge
that reaches a point not yet in the tree. A min-heap of candidate edges hands you
that cheapest crossing edge in `O(log n)`:

```
seed point 0 into the tree (cost 0)
while tree doesn't span all points:
    pop cheapest edge (cost, point) to an outside point
    if point already in tree: skip (stale)
    add it, then offer edges from it to remaining outsiders
```

**Kruskal — merge many trees.** Sort *all* edges cheapest-first. Add each edge
only if its endpoints aren't already connected (else it'd make a cycle).
Union-find answers "already connected?" in near-constant time. Stop after `n-1`
edges. Both land on the same minimum cost.

## Complexity

- **Prim (dense/all-pairs):** `O(n^2 log n)` time — up to `n^2` heap pushes,
  each `O(log n)`; `O(n)` space beyond the point list.
- **Kruskal:** `O(n^2 log n)` time — building and sorting all `~n^2/2` edges
  dominates; `O(n^2)` space to hold them. Union-find ops are ~`O(1)` amortized.

For this problem the graph is complete (any pair is connectable), so Prim's heap
form is usually the tidier fit.

## Pitfalls

- **Stop at `n-1` edges** / when the tree spans all points. Adding more creates
  cycles and over-counts.
- Prim's **stale-entry skip** (`if in_tree[i]: continue`) is essential — the heap
  holds outdated candidates once a point joins via a cheaper edge.
- Kruskal without the **cycle check** (union returning False) will happily add
  redundant edges and inflate the cost.
- Union-find without path compression / union by rank degrades toward `O(n)` per
  op — keep both optimizations.

## Transfer

MST via Prim's heap or Kruskal's union-find is the reusable engine. Union-find
alone powers connectivity problems like
[Number of Connected Components / 323](https://leetcode.com/problems/number-of-connected-components-in-an-undirected-graph/)
and [Redundant Connection / 684](https://leetcode.com/problems/redundant-connection/).
Prim's "grow via a heap of frontier edges" is a cousin of Dijkstra in
[Network Delay Time / 743](../0743-network-delay-time/) — same heap machinery,
different quantity minimized (tree weight vs. path distance).
