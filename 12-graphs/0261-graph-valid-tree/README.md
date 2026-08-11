# 261. Graph Valid Tree

**Pattern:** Connectivity + the "n-1 edges" tree property
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/graph-valid-tree/

## The problem in plain words

You have `n` nodes (labeled `0..n-1`) and a list of undirected edges. Is this a
**tree**? A tree means two things at once: everything is connected into a single
piece, and there are **no cycles** (no loops).

## Start from the obvious

Translate the definition literally: check "connected" and check "no cycle"
separately.

```
tree  ==  connected  AND  acyclic
```

You could DFS from node 0, and along the way, if you ever reach an already-visited
node that isn't the one you just came from, you've found a cycle → not a tree.
Then afterward, confirm the DFS reached all `n` nodes → connected. That works and
is `O(n + e)`.

## Find the insight

There's a cleaner path that folds both checks into one. A classic fact:

> Any two of {connected, acyclic, "exactly n-1 edges"} imply the third.

In particular, **a connected graph on `n` nodes is a tree iff it has exactly
`n-1` edges.** Intuitively: it takes at least `n-1` edges to connect `n` nodes at
all; and once connected with exactly `n-1`, there's no spare edge left to close a
loop, so it must be acyclic.

So the algorithm becomes just:

1. If `n == 0`, it's vacuously a tree.
2. If `len(edges) != n - 1`, reject immediately. (Fewer than `n-1` → can't be
   connected. More than `n-1` → a connected graph would have a cycle; a
   disconnected one still fails.)
3. Otherwise run one connectivity pass (DFS from node 0). If it reaches all `n`
   nodes, it's a tree.

The edge-count check is what lets us **skip an explicit cycle check** — that's the
payoff.

## Complexity

- **Time:** `O(n + e)` — building the adjacency list and one DFS.
- **Space:** `O(n + e)` — adjacency list plus the visited set and stack.

## Pitfalls

- **`n == 0`.** With no nodes, `n - 1` is `-1`; guard it or the edge-count test
  misfires. An empty graph counts as a valid tree.
- **Right edge count but disconnected.** `n=4` with edges forming a triangle
  `[[0,1],[1,2],[0,2]]` has 3 edges = `n-1`, yet node 3 is isolated *and* the
  triangle has a cycle. The edge count alone can't tell — that's why the
  connectivity pass is still required.
- **Duplicate / self edges.** Real inputs are usually clean, but a self-loop or a
  duplicated edge would break the counting argument; note it if the constraints
  allow them.

## Transfer

The "n-1 edges + connected ⇒ tree" shortcut, and the underlying connected-component
walk, transfer to
[Number of Connected Components / 323](../0323-number-of-connected-components-in-an-undirected-graph/)
and to union-find problems like
[Redundant Connection / 684](https://leetcode.com/problems/redundant-connection/),
where the extra edge over `n-1` is exactly the one that creates a cycle.
