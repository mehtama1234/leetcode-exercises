# 684. Redundant Connection

**Pattern:** Union-Find (Disjoint Set Union) — the edge that closes a cycle
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/redundant-connection/

## The problem in plain words

A tree on `n` nodes has exactly `n-1` edges and no cycles. You're given `n` edges —
one too many — so somewhere they form exactly one cycle. Return the last edge (in
the order given) whose removal turns the graph back into a tree.

```diagram
   edges = [[1,2], [1,3], [2,3]]

        1
       / \
      2 - 3      the edge [2,3] closes the triangle

   removing [2,3] leaves a clean tree  ->  answer: [2, 3]
```

## Why this matters

The extra edge is the one that connects two nodes that were *already reachable from
each other*. Every other edge joins a new node into the growing structure; the
redundant one links two nodes already in the same clump, closing a loop. So the
real question, edge by edge, is: **are these two endpoints already connected?**

That membership question — "are these two things already in the same group?" — is
the heart of cycle detection, and it drives real systems: a build tool rejecting a
circular dependency, a spanning-tree algorithm refusing an edge that would form a
loop, a filesystem preventing a symlink cycle. Union-Find answers it in effectively
constant time.

## Start from the obvious

For each edge you could run a fresh search to see whether a path already exists
between its two endpoints, then add the edge. That re-explores the graph for every
edge — slow, and it repeats work each time. Union-Find replaces the whole search
with a one-step "same group?" check.

Union-Find keeps every node in a group, each group named by a "root." Two nodes are
connected exactly when they share a root. Start with every node alone, then process
edges in order, merging groups as you go.

```diagram
   start: every node its own group

     (1)   (2)   (3)      each points to itself = its own root
```

## The insight

Process edges in the given order. For each edge `(u, v)`, try to union them. The
first time union reports "these two were *already* in the same group," that edge
closed the cycle — and because you're going in input order, it's automatically the
last such edge the problem asks for.

```diagram
   edges = [[1,2], [1,3], [2,3]]

   union(1,2): roots 1,2 differ -> merge
        1
        |          groups: {1,2}  {3}
        2

   union(1,3): find(1)=1, find(3)=3 differ -> merge
        1
       / \         groups: {1,2,3}
      2   3

   union(2,3): find(2)=1, find(3)=1  -> SAME root already!
               [2,3] is the redundant edge  ->  return [2, 3]
```

Two speedups keep every step near-constant. **Path compression**: `find` re-points
every node it walks straight to the root, flattening the tree so later lookups are
instant. **Union by rank**: hang the shorter tree under the taller one, so no chain
grows long enough to make `find` crawl.

```diagram
   find(x) walks up to the root, then flattens:

   before:    a          after path compression:   a
              |                                    /|\
              b                                   b c x
              |
              c
              |
              x        (b, c, x now point straight at root a)

   union by rank: shorter tree goes under the taller root
     rank 2 tree   rank 1 tree        merged: rank-1 hangs under rank-2 root
         R              s                         R
        /|             |                         /|\
       . .             t                        . .  s
                                                     |
                                                     t
```

## Complexity

- **Time: about n steps**, each union effectively constant. One pass over the
  edges, stopping the moment a cycle is found.
- **Extra memory: about n.** Two arrays — each node's parent and each root's rank.

## Pitfalls

- Returning the *first* edge of a cycle instead of the redundant one. Processing in
  input order and returning the edge that fails to merge gives the last edge, which
  is what's asked.
- Skipping path compression or union by rank — without them a degenerate chain
  makes `find` slow toward `O(n)`.
- Node labels here are 1-indexed; sizing the parent/rank arrays for `0..n` avoids
  an off-by-one.

## Transfer

The reusable move is **detect a cycle by asking Union-Find whether an edge's
endpoints are already connected before you add it.** The same structure counts
groups in [Number of Provinces / 547](../0547-number-of-provinces/), and this
exact "reject the edge that closes a loop" test is the cycle guard inside Kruskal's
minimum-spanning-tree algorithm.
