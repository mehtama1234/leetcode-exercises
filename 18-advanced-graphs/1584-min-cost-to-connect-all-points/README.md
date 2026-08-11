# 1584. Min Cost to Connect All Points

**Pattern:** Minimum spanning tree (Prim's heap / Kruskal's union-find)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/min-cost-to-connect-all-points/

## The problem in plain words

You have points on a grid. You may wire any two of them together, and doing so
costs their Manhattan distance (`|x1-x2| + |y1-y2|`). Connect them all — every
point reachable from every other — for the least total cost. You don't need a
direct wire between every pair; you just need the whole thing to hang together as
one connected piece.

That "connect everything as cheaply as possible, no wasted wires" is exactly a
**minimum spanning tree** — the cheapest set of links that ties every point into
one network with no loops.

```diagram
   points:  A(0,0)  B(2,2)  C(3,10)  D(5,2)  E(7,0)

   a few Manhattan distances:
       A-B = 4    B-D = 3    D-E = 4    B-C = 9

   one cheapest way to wire all 5 (total = 20):

       A --4-- B --3-- D --4-- E
                       |
                       9
                       C

   4 wires for 5 points, no loop  ->  total cost 20
```

## Why this matters

The deeper operation is: *given a set of things and the cost to link any pair,
what is the cheapest set of links that ties them all into one network?* The answer
always has the same shape — a tree. It touches every node, has no loop (a loop
means one redundant, removable link), and uses exactly `n-1` links.

This is not academic. Laying fiber, water pipes, or power lines to connect towns
with the least trenching is the original spanning-tree problem. Clustering methods
build a minimum spanning tree over data points and cut the longest links to
separate groups. Chip designers route wires between components to keep total wire
length down. Network engineers connect switches into a tree so there are no loops.

What the good solution buys is a provable minimum, cheaply. Trying combinations of
links is astronomically slow; both methods here run in about `E·log E` steps and
are *guaranteed* to return the true minimum, thanks to one greedy fact.

## Start from the obvious

Try every subset of possible wires, keep the ones that make everything connected,
and take the cheapest such subset.

```diagram
   best = infinity
   for every subset S of the possible wires:
       if S connects all points with nothing left over:
           best = min(best, total_cost(S))
```

With `n` points there are up to `n(n-1)/2` possible wires, and the number of
subsets doubles with each extra wire — far too many to check. But there is a
shortcut hiding in the structure.

## The insight

The greedy fact that makes this tractable: **the single cheapest wire crossing
from your current connected piece to a point outside it is always safe to add.**
It can never force you to overspend later. Two methods use this.

**Prim — grow one tree.** Start from any point. Keep adding the cheapest wire that
reaches a point not yet in the tree. A min-heap (a bucket that always hands you its
smallest item) gives you that cheapest crossing wire quickly.

```diagram
   seed A into the tree (cost 0).  in_tree = {A}
   heap offers wires from A: (B,4) (D,7) (E,7) (C,13)

   pop (B,4)  -> add B, total=4    now offer wires from B
   pop (D,3)  -> add D, total=7    (B-D=3 beat the old A-D=7)
   pop (E,4)  -> add E, total=11
   pop (C,9)  -> add C, total=20   all 5 in  ->  done

   tree grows one point at a time, always by its cheapest reach
```

**Kruskal — merge many trees.** Sort *all* wires cheapest-first. Add each wire
only if its two ends aren't already connected (else it would make a loop).
Union-find (a structure that tracks "are these two in the same group?" in near-
constant time) answers that. Stop after `n-1` wires. Both land on the same total.

```diagram
   sorted wires (cost, ends):  (3,B-D) (4,A-B) (4,D-E) ... (9,B-C) ...

   (3,B-D)  ends in different groups?  yes  -> take it. total=3
   (4,A-B)  different groups?          yes  -> take it. total=7
   (4,D-E)  different groups?          yes  -> take it. total=11
   ...
   (9,B-C)  different groups?          yes  -> take it. total=20   (4 wires: stop)

   a wire whose ends are already joined would close a loop  ->  skip it
```

## Complexity

- **Prim (every pair connectable):** about `n^2·log n` steps — up to `n^2` heap
  pushes, each about `log n`. Extra memory about `n` beyond the point list.
- **Kruskal:** about `n^2·log n` steps — building and sorting all `~n^2/2` wires
  dominates. Extra memory about `n^2` to hold them. Each union-find operation is
  near-constant on average.

Here any pair is connectable, so the graph is dense and Prim's heap form is
usually the tidier fit.

## Pitfalls

- **Stop at `n-1` wires** / when the tree spans all points. Adding more makes
  loops and over-counts.
- Prim's **stale-entry skip** (`if in_tree[i]: continue`) is essential — the heap
  holds outdated candidates once a point has joined through a cheaper wire.
- Kruskal without the **loop check** (union returning False) will happily add
  redundant wires and inflate the cost.
- Union-find without path compression / union by rank drifts toward `O(n)` per
  operation — keep both speedups.

## Transfer

Spanning-tree via Prim's heap or Kruskal's union-find is the reusable engine.
Union-find alone powers connectivity problems like
[Number of Connected Components / 323](https://leetcode.com/problems/number-of-connected-components-in-an-undirected-graph/)
and [Redundant Connection / 684](https://leetcode.com/problems/redundant-connection/).
Prim's "grow via a heap of frontier wires" is a cousin of Dijkstra in
[Network Delay Time / 743](../0743-network-delay-time/) — same heap machinery,
different quantity minimized (tree weight vs. path distance).
