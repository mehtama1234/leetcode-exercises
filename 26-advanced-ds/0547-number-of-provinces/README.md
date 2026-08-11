# 547. Number of Provinces

**Pattern:** Union-Find (Disjoint Set Union) — count connected components
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/number-of-provinces/

## The problem in plain words

There are `n` cities. A grid tells you which pairs are directly connected:
`isConnected[i][j] == 1` means a road runs straight between city `i` and city `j`.
A **province** is a clump of cities all reachable from one another, directly or by
hopping through intermediate cities. Count the clumps.

## Why this matters

Stripped of the city story, this is **counting connected components of a graph** —
"how many separate islands does this network break into?" That single question
sits under a surprising amount of real work.

**Clustering by relationship:** group users who share a device or IP into
suspected fraud rings; merge duplicate customer records that share an email or
phone into one identity. Each shared attribute is an edge; each resulting cluster
is a province. **Infrastructure health:** given which servers can still reach each
other after a partition, how many isolated islands did the outage create?
**Image and map analysis:** connected-component labeling counts distinct blobs,
regions, or objects by merging touching pixels. **Social / collaboration graphs:**
how many disconnected communities exist in a friend or co-authorship network?

The good solution buys you the count in **one near-linear sweep with almost no
bookkeeping**: with Union-Find you never traverse the graph a second time to count
— you start with `n` groups and just watch the group count fall as edges merge
things. The resource saved is repeated work: no re-exploration, no visited-set
juggling across components.

## Start from the obvious

A province is a connected component, and the textbook way to peel off one component
is a flood fill: pick an unvisited city, mark everything reachable from it, and
that's one province.

```
provinces = 0
for city in cities:
    if not seen[city]:
        provinces += 1
        dfs_mark_everything_reachable(city)   # BFS works too
return provinces
```

This is completely correct and is genuinely one of the two good answers (it's in
the solution file as `findCircleNum_dfs`). Each city and each matrix cell is
touched once, so it's `O(n²)` — the cost of reading the adjacency matrix at all.

## Find the waste

DFS is fine here, but notice what it forces on you: an explicit `seen` array, a
recursion (or stack) that can be deep, and a mental model of "explore one whole
region, then find the next unexplored start." The *counting* is a side effect of
where the exploration happens to begin.

Union-Find flips it around. Instead of exploring regions, **merge cities as you see
each road and keep a running count of how many separate groups remain.** No
traversal, no visited set, no recursion depth to worry about. The count is
maintained directly: it starts at `n` and drops by one every time a road joins two
cities that weren't already in the same group.

## The insight

Give each city a group id (its Union-Find root). Two operations:

```
find(x)    -> the root of x's group
union(a,b) -> if find(a) != find(b): merge them, count -= 1
```

Initialize `count = n` (every city its own province). Scan the upper triangle of
the matrix (`j > i`, since it's symmetric); for every `isConnected[i][j] == 1`,
`union(i, j)`. When two different provinces merge, the count drops by one; when the
two cities were already in the same province, nothing changes. After the sweep,
`count` **is** the number of provinces — no second pass.

Two optimizations keep it fast:

- **Path compression** — `find` re-points nodes straight at the root, flattening
  trees so repeat lookups are `O(1)`.
- **Union by rank** — hang the shorter tree under the taller one so trees stay shallow.

Together: `O(alpha(n))` amortized per operation, where `alpha` (inverse Ackermann)
is `≤ 4` for any real `n` — effectively constant.

## Complexity

- **Time:** `O(n² · alpha(n))` ≈ `O(n²)` — we must read all `n²` matrix cells; each
  `union` on a `1` cell is near-constant. The matrix read dominates.
- **Space:** `O(n)` — the `parent` and `rank` arrays. (DFS is also `O(n)`, but adds
  recursion-stack depth up to `n`.)

## Pitfalls

- **Double-processing the symmetric matrix.** Scanning all `n²` cells still works,
  but iterate `j > i` to halve the unions and avoid the always-1 diagonal.
- **Miscounting.** Only decrement the province count on a *successful* union (two
  different groups). Decrementing on every `1` cell over-subtracts.
- **DFS recursion depth.** For a large fully-connected instance the DFS version can
  hit Python's recursion limit; Union-Find (or an explicit-stack DFS) sidesteps it.
- **Forgetting the diagonal is always 1.** `isConnected[i][i] == 1` is noise — a
  city connected to itself. Skip it.

## Transfer

The reusable move is **count-the-groups-as-you-merge**: maintain a live group count
in Union-Find and read it off at the end instead of re-traversing to count. Reach
for it whenever the question is "how many separate clusters?" over a set of
pairwise links. Siblings: [Redundant Connection /
684](../0684-redundant-connection/) uses the same DSU to catch the edge that closes
a cycle; [Number of Islands / 200] is the grid-flood-fill twin; [Accounts Merge /
721] and [Number of Connected Components / 323] are direct component-counting
relatives.
