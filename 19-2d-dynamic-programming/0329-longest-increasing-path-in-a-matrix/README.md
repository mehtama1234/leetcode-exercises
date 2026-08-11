# 329. Longest Increasing Path in a Matrix

**Pattern:** 2-D dynamic programming (memoized DFS on an implicit DAG)
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/longest-increasing-path-in-a-matrix/

## The problem in plain words

You have a grid of numbers. A move goes to a neighbor up, down, left, or right, but
only if that neighbor's value is *strictly greater*. Find the length of the longest
path you can walk under that rule.

```diagram
   matrix        one longest increasing walk:

     9  9  4        1 -> 2 -> 6 -> 9     (length 4)
     6  6  8        going up the values, one step at a time
     2  1  1
```

## Why this matters

Two ideas make this click. First: because every step goes strictly *uphill* in
value, you can never return to a cell you've left — there are no loops. A graph with
directed edges and no cycles is a *DAG* (a one-way graph you can't walk in a circle),
and a DAG is exactly the setting where "longest path" is a well-behaved question with
a clean answer. Second: the best path length starting at a cell depends only on the
cell, never on how you arrived there — so compute it once and remember it.

"Turn a constraint into a direction, notice there are no cycles, then solve each node
once and cache it" is a reusable pattern: it handles task scheduling with
prerequisites, longest chains, and any problem shaped like "follow the arrows as far
as you can."

## Start from the obvious

From each cell, walk every uphill path and take the longest. The best length at a
cell is `1 + the best over its larger neighbors`. Do that with plain recursion from
every cell.

```diagram
   best(r, c) = 1 + max( best(neighbor) )  over neighbors with a bigger value
              = 1  if no neighbor is bigger (a local peak)

              from cell 1 (bottom middle):
                 1 -> 2 (left)  -> 6 -> 9
                 1 -> 2 (?)
              re-walks the same uphill tails again and again
```

This is correct but explosive: a cell reachable from many places has its whole
uphill tail recomputed each time it's visited. That repeated recomputation is the
waste.

## The insight — cache each cell once

Store `best[r][c]` = length of the longest increasing path *starting* at that cell.
Since there are no cycles, this value is well defined, and once you compute a cell
you never need to compute it again. This is a DP over the grid; the fill order is the
value order itself (small cells depend on bigger neighbors), so memoized recursion is
the natural form.

```diagram
   matrix                best[r][c]  (longest increasing path starting here)

     9  9  4               1  1  2
     6  6  8               2  2  1
     2  1  1               3  4  2
                              ^ start at value 1 -> 2 -> 6 -> 9, length 4
```

Watch a cell fill from its neighbors. A cell reads only the neighbors whose value is
*larger* (the ones it can step to); each already holds its own best length:

```diagram
   filling best[r][c], comparing to the four neighbors

                    up
                    ^ (only if bigger)
                    |
        left  <-- (r,c) --> right
                    |
                    v
                   down

   best[r][c] = 1 + max( best of each STRICTLY-bigger neighbor )
              = 1  if none is bigger

   e.g. cell "6" (value 6): its only bigger neighbor is "8"
        best(6) = 1 + best(8) = 1 + 1 = 2
        cell "2": bigger neighbor is "6"  -> best(2) = 1 + best(6) = 3
        cell "1": bigger neighbor is "2"  -> best(1) = 1 + best(2) = 4
```

The answer is the largest `best[r][c]` over the whole grid. Each cell is solved once
and its result reused, so the total work is proportional to the number of cells plus
the number of neighbor checks.

## Complexity

- **Time: about R × C steps** (rows × columns). Each cell is computed once and cached;
  each looks at its four neighbors. Linear in the grid size.
- **Extra memory: about R × C** for the cache (plus the recursion depth, up to the
  length of the longest path).

## Pitfalls

- Using `>=` instead of `>`. The step must be *strictly* increasing; a plateau of
  equal values gives no move, so a grid of equal numbers has answer 1.
- Adding a visited-set like ordinary DFS. You don't need one — the strictly-uphill
  rule already forbids revisiting, and a visited-set would wrongly block valid paths.
- Recomputing instead of caching. Without the cache this is exponential; the cache is
  the whole point.

## Transfer

The reusable move is *turn a monotonic-constraint grid into a DAG, then do
longest-path via memoized DFS (solve each node once, ignore arrival path).* Siblings:
[Course Schedule / 207](https://leetcode.com/problems/course-schedule/) (DAG
detection/topo order), [Word Break / 139](https://leetcode.com/problems/word-break/)
(memoized DFS over overlapping subproblems), and any "longest chain of increasing X"
such as [Longest Increasing Subsequence / 300](https://leetcode.com/problems/longest-increasing-subsequence/).
