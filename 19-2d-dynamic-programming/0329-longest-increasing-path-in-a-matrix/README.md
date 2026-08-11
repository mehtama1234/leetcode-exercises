# 329. Longest Increasing Path in a Matrix

**Pattern:** 2-D dynamic programming (memoized DFS on an implicit DAG)
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/longest-increasing-path-in-a-matrix/

## The problem in plain words

You have a grid of numbers. Starting anywhere, you may step to a neighbouring cell
(up, down, left, or right) only if its value is strictly larger. Find the length of
the longest such strictly-increasing walk you can take.

## Why this matters

The real lesson is *recognizing that a grid with a "strictly increasing" rule is
secretly a DAG (directed acyclic graph), and that longest-path on a DAG is a clean
DP.* The "strictly greater" constraint is doing heavy lifting: it guarantees no
cycles, which is exactly why the recursion terminates and why memoization is even
valid. Spotting "this constraint makes it acyclic" is the transferable insight.

The pattern shows up wherever you trace the longest chain of monotonically changing
states over a 2-D field. Terrain and hydrology: water flows downhill, so the longest
descending flow path on an elevation grid is this problem. Dependency or version
chains laid out on a grid, "longest run of increasing brightness" in image
processing, and gradient-following on a heightmap all reduce to longest path on the
uphill/downhill DAG.

What the good solution buys is turning an exponential re-exploration of overlapping
paths into `O(rows × cols)` work: each cell's answer is computed once and reused,
because a cell's best onward path doesn't depend on how you arrived.

## Start from the obvious

From a cell, the longest increasing path is `1 + ` the best over its larger
neighbours. DFS it directly:

```
def dfs(r, c):
    best = 1
    for each neighbour (nr, nc) with matrix[nr][nc] > matrix[r][c]:
        best = max(best, 1 + dfs(nr, nc))
    return best
answer = max(dfs(r, c) over all cells)
```

Correct — and exponential, because a cell reachable from many predecessors has its
entire downstream recomputed every time.

## Find the waste

Here's the key observation: **`dfs(r, c)` depends only on `(r, c)`**, never on the
path taken to reach it. And because every edge goes to a *strictly larger* value,
the "points to a larger neighbour" graph has no cycles — it's a DAG. So each cell
has one well-defined answer. Cache it:

```
@lru_cache
def best(r, c):
    ...same body, calling best(nr, nc)...
```

Now each cell is expanded once. This memoized DFS *is* the DP — the topological
order is the value order, handled implicitly by recursion.

## The insight

You could make the order explicit instead: sort all cells by value ascending and
relax them (a Kahn-style / peeling-outer-layers approach), which removes recursion
depth risk. But the memoized DFS already captures the DP essence — solve each DAG
node once, reuse everywhere. There is no rectangular row-by-row sweep here because
the dependency order follows the *values*, not the grid coordinates.

## Complexity

- **Time:** `O(rows × cols)` — each cell computed once; each of its ≤4 edges examined
  once. So `O(V + E)` on the DAG, and `E ≤ 4V`.
- **Space:** `O(rows × cols)` for the memo, plus recursion stack up to the path
  length in the worst case.

## Pitfalls

- **Strictly** greater, not `≥`. Using `≥` would create equal-value cycles and hang
  the recursion; equal neighbours must not be an edge.
- Forgetting to take the max over **all** start cells — the longest path can begin
  anywhere, not just the smallest cell.
- Empty matrix / empty rows should return 0 before indexing.
- Deep recursion on a large gradient grid can hit stack limits; the explicit
  sort-and-relax version avoids that.

## Transfer

The reusable move is *turn a monotonic-constraint grid into a DAG, then do
longest-path via memoized DFS (solve each node once, ignore arrival path).* Siblings:
[Course Schedule / 207](https://leetcode.com/problems/course-schedule/) (DAG
detection/topo order), [Word Break / 139](https://leetcode.com/problems/word-break/)
(memoized DFS over overlapping subproblems), and any "longest chain of increasing X"
such as [Longest Increasing Subsequence / 300](https://leetcode.com/problems/longest-increasing-subsequence/).
