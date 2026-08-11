# 323. Number of Connected Components in an Undirected Graph

**Pattern:** Union-Find — merge groups and ask "same group?"
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/number-of-connected-components-in-an-undirected-graph/

## The problem in plain words

You have `n` nodes and a list of undirected edges. Count how many separate clumps
of nodes there are — groups where you can walk from any node to any other in the
group, but not across to a different group.

```diagram
   n = 5,  edges = [0-1, 1-2, 3-4]

     (0)---(1)---(2)        (3)---(4)

      one clump  {0,1,2}     another clump {3,4}
                                          answer: 2
```

## Why this matters

The deeper task is: **merge things into groups as connections arrive, and be able
to ask "are these two already in the same group?" at any point.** The tool built
for exactly this is **Union-Find** (also called disjoint-set union). It has two
moves — `union` (fuse two groups) and `find` (which group is this node in?) — and
both run in near-constant time.

This is the go-to when relationships stream in and you keep fusing sets. Building a
minimum-cost network adds the cheapest link whose two ends aren't already
connected. Deduplication merges records that turn out to be the same person.
Friend-of-a-friend "are these two in the same social circle?" queries lean on it.

What you are solving for is answering connectivity **online** — as each edge
arrives — without re-running a full graph search every time.

## Start from the obvious

The straightforward way is the same as counting islands: build neighbor lists, then
walk. Each time you start a fresh walk from an unvisited node, that is one new
clump; mark everything it reaches so you don't recount it.

```diagram
   count = 0
   for node in 0..n-1:
       if node not visited:
           count += 1
           walk from node, marking everything reachable
```

That is a fine answer that grows in step with nodes + edges, and it is the same
idea as [Number of Islands](../0200-number-of-islands/). But this problem is a
good excuse to learn the tool made for merging groups: **Union-Find.**

## The insight — start apart, count the merges

Flip your viewpoint. Start with every node in its **own** group, so there are `n`
groups. Now feed in edges one at a time. Each edge says "these two belong
together":

- If they are **already** in the same group, the edge tells you nothing new.
- If they are in **different** groups, this edge fuses those two into one — so the
  group count drops by exactly 1.

Answer = `n` minus the number of merges that actually happened.

```diagram
   n = 5.  each node its own group -> count = 5

   parent: 0  1  2  3  4      (each points to itself)

   edge 0-1:  different groups -> merge      count 5 -> 4
   edge 1-2:  different groups -> merge      count 4 -> 3
   edge 3-4:  different groups -> merge      count 3 -> 2

                                          answer: 2
```

The one hard part is answering "same group?" fast. Union-Find stores each group as
a little tree with a root. `find(x)` climbs to `x`'s root, and two nodes are in the
same group exactly when they share a root.

```diagram
   how a redundant edge is caught (triangle, n=3):

   edge 0-1: merge -> tree:  1                edge 2 of the triangle
   edge 1-2: merge -> tree:  0                is redundant, so count
                              \                stays at 1, not 0
                             root of {0,1,2}

   edge 0-2: find(0) and find(2) share the SAME root  ->  no merge, count unchanged
```

Two touch-ups keep the trees from getting tall and slow:

- **Path compression** — after a `find`, repoint the nodes you climbed straight at
  the root, so next time the climb is flat.
- **Union by rank** — always hang the shorter tree under the taller one.

## Find the waste

Re-running a full graph walk after every new edge would redo almost all the work
each time. Union-Find answers each "same group?" in effectively constant time, so
processing all the edges together grows in step with the input instead.

## Complexity

- **Time: effectively linear.** Each `find`/`union` is near-constant with both
  touch-ups, so handling all edges is about n + e steps in practice.
- **Extra memory: about n** for the `parent` and `rank` arrays.

## Pitfalls

- **Count merges, not edges.** A redundant edge — both ends already in one group,
  like the third edge of a triangle — must **not** drop the count. That's why
  `union` reports whether it actually merged.
- **Skipping a touch-up.** Without path compression *and* union by rank, `find` can
  slow toward a full climb per call on bad inputs.
- **`n == 0`.** No nodes means zero components — the loops handle it, but check it.

## Transfer

Union-Find is the reach-for tool whenever you merge groups and ask "same group?":
[Graph Valid Tree / 261](../0261-graph-valid-tree/) (a tree is one group formed by
`n-1` merges),
[Redundant Connection / 684](https://leetcode.com/problems/redundant-connection/)
(the first edge whose `union` reports "already together" is the loop-closer), and
[Accounts Merge / 721](https://leetcode.com/problems/accounts-merge/).
