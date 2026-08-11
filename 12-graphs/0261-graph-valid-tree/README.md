# 261. Graph Valid Tree

**Pattern:** Connectivity + the "n-1 edges" tree shortcut
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/graph-valid-tree/

## The problem in plain words

You have `n` nodes (labeled `0..n-1`) and a list of undirected edges. Is this a
**tree**? A tree means two things at once: everything hangs together in a single
piece, and there are **no loops**.

```diagram
   a tree (n=5):            NOT a tree (has a loop):

      (0)                      (0)
     / | \                    /   \
   (1)(2)(3)                 (1)---(2)
    |                         a loop 0-1-2-0; can't be a tree
   (4)
   one piece, no loop
```

## Why this matters

The deeper question is: **is this set of connections a clean hierarchy — one piece,
no extra links, no loop?** A tree has to satisfy two things at once: it is fully
connected, and it has no cycle.

Here is the shortcut that makes the whole problem cheap. For `n` nodes, being a
tree collapses to one crisp test: **connected AND exactly `n-1` edges.** It takes
at least `n-1` edges to tie `n` nodes into one piece; and once connected with
exactly `n-1`, there is no spare edge left to close a loop.

That "minimal links, no loop" shape is load-bearing in real systems. A spanning
tree is the smallest set of links that connects a network with no loops — which is
why network switches run spanning-tree protocol to switch off redundant links that
would otherwise cause broadcast storms. File systems and org charts are trees, and
validating a proposed set of parent-child links keeps them from curling into loops.

## Start from the obvious

Translate the definition literally: check "connected" and check "no loop"
separately.

```diagram
   tree  ==  connected  AND  no loop
```

You could walk from node 0, and if you ever reach an already-visited node that
isn't the one you just came from, you have found a loop → not a tree. Then check
the walk reached all `n` nodes → connected. That works and grows in step with
nodes + edges.

## The insight — count the edges first

There is a cleaner path that folds both checks into one. A classic fact:

> A connected graph on `n` nodes is a tree exactly when it has `n-1` edges.

So the algorithm shrinks to three steps:

1. If `n == 0`, it is vacuously a tree.
2. If the edge count isn't `n-1`, reject right away. Fewer than `n-1` can't connect
   everything; more than `n-1` forces a loop.
3. Otherwise run **one** connectivity walk from node 0. If it reaches all `n` nodes,
   it is a tree.

```diagram
   n = 5, edges = [0-1, 0-2, 0-3, 1-4]   ->  4 edges == n-1 == 4  ok

   walk from 0:   seen = {0}
     visit 1,2,3            seen = {0,1,2,3}
       from 1 visit 4       seen = {0,1,2,3,4}
   reached all 5 nodes  ->  connected  ->  TREE
```

But the edge count alone is not enough — you still need the walk:

```diagram
   n = 4, edges = [0-1, 1-2, 0-2]        ->  3 edges == n-1 == 3   (passes count!)

      (0)---(1)
        \   /
        (2)          (3) is off on its own

   walk from 0 reaches {0,1,2} only  ->  3 != 4  ->  NOT connected  ->  NOT a tree
```

That example has the right edge count yet a loop in the triangle and a stranded
node 3. The count screen alone can't see it — that's why the connectivity walk
stays. What the count buys you is skipping a separate loop search: once the count is
`n-1` and the graph is connected, no loop is possible.

## Complexity

- **Time: about n + e steps** — building the neighbor lists and one walk.
- **Extra memory: about n + e** — the neighbor lists plus the visited set and stack.

## Pitfalls

- **`n == 0`.** With no nodes, `n - 1` is `-1`; guard it or the edge-count test
  misfires. An empty graph counts as a valid tree.
- **Right edge count but disconnected.** The triangle-plus-stranded-node above has
  `n-1` edges and still fails — that's why the walk is required.
- **Duplicate or self edges.** A self-loop or a repeated edge would break the
  counting argument; note it if the constraints allow them.

## Transfer

The "`n-1` edges + connected ⇒ tree" shortcut, and the connected-clump walk under
it, carry over to
[Number of Connected Components / 323](../0323-number-of-connected-components-in-an-undirected-graph/)
and to merge-based problems like
[Redundant Connection / 684](https://leetcode.com/problems/redundant-connection/),
where the one extra edge over `n-1` is exactly the edge that closes a loop.
