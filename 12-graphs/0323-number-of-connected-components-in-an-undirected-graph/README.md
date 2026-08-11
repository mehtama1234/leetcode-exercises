# 323. Number of Connected Components in an Undirected Graph

**Pattern:** Union-Find (disjoint set union) — count components
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/number-of-connected-components-in-an-undirected-graph/

## The problem in plain words

You have `n` nodes and a list of undirected edges. Count how many separate
"islands" of nodes there are — groups where you can walk from any node to any
other in the group, but not across to a different group.

## Why this matters

The deeper problem is **incrementally merging things into groups while answering "are these two already in the same group?"** as edges arrive. The fundamental data structure is Union-Find (disjoint-set union), and its two operations — `union` and `find` — run in near-constant time.

This is the tool of choice when relationships stream in and you keep fusing sets. Kruskal's algorithm builds a minimum spanning tree by adding the cheapest edge whose endpoints aren't already connected — used in network/cable layout. Deduplication and entity resolution merge records that refer to the same person or account (merge emails that share a contact). Image segmentation and percolation/clustering group adjacent similar regions. Even friend-suggestion and "are these in the same social circle?" queries lean on it.

What you're solving for is **answering connectivity queries online, without re-running a full graph search after every edge**. Path compression + union-by-rank keep both operations effectively `O(α(n))` — practically constant — so processing all edges is essentially linear.

## Start from the obvious

The straightforward approach: build an adjacency list, then DFS/BFS. Every time
you start a fresh traversal from an unvisited node, that's one new component;
mark everything it reaches as visited so you don't recount it.

```
count = 0
for node in 0..n-1:
    if node not visited:
        count += 1
        flood-fill from node (mark all reachable visited)
```

That's a perfectly good `O(n + e)` answer (and it's the same idea as
[Number of Islands](../0200-number-of-islands/)). But this problem is a great
excuse to learn the tool that's *built* for merging groups: **Union-Find**.

## The insight

Flip your viewpoint. Start with every node in its **own** group, so there are `n`
groups. Now process edges one at a time. Each edge says "these two nodes belong
together":

- If they're **already** in the same group, the edge tells you nothing new.
- If they're in **different** groups, this edge fuses those two groups into one —
  so the total number of groups drops by exactly 1.

Answer = `n` minus the number of merges that actually happened.

The only hard part is answering "are these two already in the same group?"
quickly. **Union-Find** does it: each group is a little tree with a root, `find(x)`
climbs to `x`'s root, and two nodes are in the same group iff they share a root.
Two optimizations keep it near-constant-time:

- **Path compression** — after `find`, repoint the nodes you climbed straight at
  the root, so next time the walk is flat.
- **Union by rank** — always hang the shorter tree under the taller one, so trees
  never get tall.

## Complexity

- **Time:** `O(n + e · α(n))`, where `α` is the inverse-Ackermann function — so
  small it's effectively constant. Practically linear.
- **Space:** `O(n)` for the `parent` and `rank` arrays.

## Pitfalls

- **Counting merges, not edges.** A redundant edge (both endpoints already
  united, e.g. the third edge of a triangle) must **not** decrement the count.
  That's why `union` returns whether it actually merged.
- **Forgetting an optimization.** Without path compression *and* union by rank,
  `find` can degrade toward `O(n)` per call on adversarial inputs.
- **`n == 0`.** No nodes means zero components — the loops handle it, but sanity
  check it.

## Transfer

Union-Find is the go-to whenever you're incrementally merging groups and asking
"same group?": [Graph Valid Tree / 261](../0261-graph-valid-tree/) (a tree is one
component with `n-1` merges),
[Redundant Connection / 684](https://leetcode.com/problems/redundant-connection/)
(the first edge whose `union` returns false is the cycle-closer), and
[Accounts Merge / 721](https://leetcode.com/problems/accounts-merge/).
