# 684. Redundant Connection

**Pattern:** Union-Find (Disjoint Set Union) — dynamic connectivity
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/redundant-connection/

## The problem in plain words

Start with a tree: `n` nodes wired together with exactly `n-1` edges, everything
connected, no loops. Someone adds one more edge, so now there are `n` edges and
exactly one cycle. You're handed the edges in the order they were added. Find and
return the one edge that, if removed, turns the graph back into a proper tree. If
several would work, return the one that appears last in the input.

## Why this matters

The deep operation is **incremental connectivity**: as connections arrive one at a
time, keep answering "are these two things already in the same connected group?"
The redundant edge is simply the first edge whose two endpoints were *already*
reachable from each other — adding it just closes a loop. So the whole problem
reduces to a fast "same group?" test that stays fast as groups keep merging.

That test is a workhorse in real systems. **Kruskal's minimum-spanning-tree
algorithm** adds edges cheapest-first and uses exactly this check to skip any edge
that would form a cycle — think laying out a network, road, or circuit at minimum
cost. **Network and cluster membership**: are hosts A and B in the same partition
after this link comes up? **Image processing / percolation**: flood-fill and
connected-component labeling merge neighboring pixels into blobs. **Account or
entity resolution**: "are these two records the same person?" as merge rules fire.

What Union-Find buys is answering a growing pile of these questions in **near-
constant time each** — `O(alpha(n))`, effectively `O(1)` — where the honest
alternative (re-run a graph search per edge) is `O(n)` per question and turns the
whole task quadratic.

## Start from the obvious

For each new edge `(u, v)`, ask directly: is there already a path from `u` to `v`
using the edges we've added so far? If yes, this edge is redundant.

```
for edge (u, v) in edges:
    if path_exists(u, v, edges_added_so_far):   # BFS or DFS
        return [u, v]
    edges_added_so_far.add((u, v))
```

Correct, and a fine first thought. But each `path_exists` is a full graph search —
`O(n)` — and we do it up to `n` times, so it's `O(n²)`. We're also rebuilding
knowledge from scratch every time when the connectivity structure barely changed.

## Find the waste

Each search rediscovers "who is connected to whom" from zero, even though the
answer only ever *grows* — edges are added, never removed, so two nodes that are
connected stay connected. We're throwing away everything we learned last time.

The fix is to **remember the groups directly** instead of re-deriving them. Give
every connected group a single representative ("root"). Then "are `u` and `v`
connected?" becomes "do `u` and `v` have the same root?" — no traversal of the
graph, just two lookups. Adding an edge that spans two different groups **merges**
them (point one root at the other). An edge inside one group changes nothing — and
*that* is the redundant edge.

## The insight

**Union-Find** maintains a forest where each node points at a parent, and each
group's root points at itself. Two operations:

```
find(x)    -> follow parent pointers to the root (x's group id)
union(a,b) -> if find(a) == find(b): already connected  (redundant edge!)
              else: attach one root under the other      (merge the groups)
```

Walk the edges in input order and `union` each. The first `union` that reports
"already connected" is the answer — and because we go in order, it's automatically
the *last* qualifying edge the problem wants.

Two optimizations make it nearly free:

- **Path compression** — during `find`, re-point every node on the path straight to
  the root. The tree flattens as you query it, so repeats are `O(1)`.
- **Union by rank** — always hang the shorter tree under the taller one, so trees
  never get needlessly deep.

Together they give `O(alpha(n))` amortized per operation. `alpha` is the inverse
Ackermann function; it's `≤ 4` for any `n` that fits in memory — constant for all
practical purposes. Skip both and a bad input can chain nodes into a length-`n`
list, dragging `find` back to `O(n)`.

## Complexity

- **Time:** `O(n · alpha(n))` ≈ `O(n)` — one near-constant `union` per edge.
- **Space:** `O(n)` — the `parent` and `rank` arrays.

## Pitfalls

- **Node labels are 1-indexed.** Size the arrays `n+1` (or map labels down), or
  you'll index out of bounds.
- **Dropping one optimization.** With only path compression *or* only union-by-rank
  you're usually fine, but with *neither* the tree can degenerate to `O(n)` per
  find and the whole thing goes quadratic — defeating the point.
- **Returning the wrong edge on ties.** Process in input order and return the first
  cycle-closing edge; don't sort or reverse the edges.
- **Confusing "no path" with "not in graph yet."** A node you haven't seen is its
  own group — the `parent[x] = x` initialization handles this; don't special-case it.

## Transfer

The reusable pattern is **dynamic connectivity: merge groups and test same-group
membership in near-constant time**. Reach for Union-Find whenever connections only
get added (never removed) and you keep asking "are these two connected?". Siblings:
[Number of Provinces / 547](../0547-number-of-provinces/) counts the groups that
remain; [Graph Valid Tree / 261] is this problem's yes/no cousin (exactly `n-1`
edges and no cycle); [Accounts Merge / 721] unions accounts sharing an email; and
Kruskal's MST uses `union`/`find` as its cycle guard.
