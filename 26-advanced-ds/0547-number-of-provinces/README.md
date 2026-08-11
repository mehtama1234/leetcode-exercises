# 547. Number of Provinces

**Pattern:** Union-Find (Disjoint Set Union) — merge groups, count what's left
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/number-of-provinces/

## The problem in plain words

You get an `n x n` grid where `isConnected[i][j] == 1` means city `i` and city `j`
have a direct road. A "province" is a set of cities all reachable from one another,
directly or through others. Count the provinces.

```diagram
   isConnected = [[1,1,0],
                  [1,1,0],
                  [0,0,1]]

   city 0 -- city 1      (connected)
   city 2                (alone)

   -> 2 provinces:  {0,1}  and  {2}
```

## Why this matters

Strip the map away and the question is: *how many separate clumps are there in a
network?* You don't care about paths or distances — only about which cities end up
in the same group once every road is accounted for. That's the count of connected
components of a graph.

Counting clumps is a recurring need: how many separate clusters of friends in a
social graph, how many islands of connected servers, how many distinct groups of
equivalent records to merge. Union-Find is the tool built exactly for "keep merging
things that belong together, and tell me how many groups remain" — and it does each
merge in effectively constant time.

## Start from the obvious

You could flood-fill: pick an unvisited city, walk out to everything reachable from
it marking as you go, and each fresh start is one new province. That works. But
Union-Find makes the counting fall out for free, and it's the tool you'd reach for
when the roads arrive one at a time rather than as a fixed grid.

Union-Find keeps every city in a group, each group represented by a "root" city.
Two cities are in the same province exactly when they share a root. Start with `n`
groups — every city its own root — and merge whenever a road connects two different
groups.

```diagram
   start: every city is its own group (points to itself)

     0     1     2     3        count = 4
    (0)   (1)   (2)   (3)       each is its own root
```

## The insight

Walk the roads. For each road, merge the two cities' groups. The clever part is the
count: it starts at `n`, and every merge that joins two *different* groups drops it
by one. When the merging is done, the count *is* the number of provinces — no
separate counting pass.

```diagram
   roads: (0,1), (1,2)     n = 4, count starts at 4

   union(0,1): roots 0 and 1 differ -> attach one under the other
     0<-1    2    3        count 4 -> 3
     (0)         (2) (3)   1's root is now 0

   union(1,2): find(1)=0, find(2)=2, differ -> merge
       0        3          count 3 -> 2
      / \
     1   2

   final forest:  {0,1,2}  and  {3}   ->  2 provinces
```

Two speedups keep every operation near-constant. **Path compression**: when you
walk up to find a root, re-point every node you passed straight at the root, so the
next lookup is instant. **Union by rank**: always hang the shorter tree under the
taller one, so no chain grows long enough to make `find` slow.

```diagram
   find(3) walks 3 -> 1 -> 0, then flattens the path:

   before:      0            after path compression:    0
               /                                       /|
              1                                       1 3
             /                                        |
            3                                       (3 now points straight to 0)

   next find(3) is one hop
```

## Complexity

- **Time: about n^2 steps** to scan the grid, each merge effectively constant. The
  grid itself has `n^2` cells, so reading it dominates.
- **Extra memory: about n.** Two arrays — each city's parent and each root's rank.

## Pitfalls

- Scanning the whole grid when it's symmetric — you only need the upper triangle
  (`j > i`), since a road from `i` to `j` is the same as `j` to `i`.
- Skipping path compression or union by rank — without them a chain can grow to
  length `n` and `find` degrades toward `O(n)`.
- Recounting groups at the end by scanning roots, when the running `count`
  (decremented on each real merge) already holds the answer.

## Transfer

The reusable move is **merge things into groups with Union-Find, and read the group
count straight off the merges.** The exact same structure answers
[Redundant Connection / 684](../0684-redundant-connection/) (spot the edge that
joins two already-connected nodes) and
[Number of Islands / 200](https://leetcode.com/problems/number-of-islands/), and it
underlies Kruskal's minimum-spanning-tree algorithm.
