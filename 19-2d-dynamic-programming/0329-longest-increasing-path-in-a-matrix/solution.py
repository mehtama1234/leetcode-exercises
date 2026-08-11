"""329. Longest Increasing Path in a Matrix —
https://leetcode.com/problems/longest-increasing-path-in-a-matrix/

Find the length of the longest path in a grid where each step moves to an adjacent
cell (up/down/left/right) with a strictly greater value.

Shown: the plain exponential DFS, then DFS + memo (DP on a DAG), which is the
optimal solution. There is no natural "flat table" order because the dependency
order is the value order itself, so memoized recursion is the clean form.
"""
from functools import lru_cache
from typing import List


def longest_increasing_path_naive(matrix: List[List[int]]) -> int:
    """Try the longest strictly-increasing walk from every cell. Exponential.

    From a cell we may step to any neighbour with a larger value; the best path
    length is 1 + the best over those neighbours. Without caching, a cell reachable
    from many places gets its whole downstream recomputed each time — that repeated
    recomputation is the exponential blow-up we remove next.
    """
    if not matrix or not matrix[0]:
        return 0
    rows, cols = len(matrix), len(matrix[0])

    def dfs(r: int, c: int) -> int:
        best = 1
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and matrix[nr][nc] > matrix[r][c]:
                best = max(best, 1 + dfs(nr, nc))
        return best

    return max(dfs(r, c) for r in range(rows) for c in range(cols))


def longest_increasing_path(matrix: List[List[int]]) -> int:
    """DFS with memoization = DP on the DAG of 'points to a larger neighbour'.

    Because every edge goes strictly uphill in value, there are no cycles: the
    graph is a DAG, and `best(r, c)` = longest increasing path starting at (r, c)
    is well defined. Each cell is solved once and cached, so total work is linear
    in the number of cells and edges.
    """
    if not matrix or not matrix[0]:
        return 0
    rows, cols = len(matrix), len(matrix[0])

    @lru_cache(maxsize=None)
    def best(r: int, c: int) -> int:
        longest = 1
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and matrix[nr][nc] > matrix[r][c]:
                longest = max(longest, 1 + best(nr, nc))
        return longest

    result = max(best(r, c) for r in range(rows) for c in range(cols))
    best.cache_clear()
    return result


def _test() -> None:
    cases = [
        ([[9, 9, 4], [6, 6, 8], [2, 1, 1]], 4),   # 1->2->6->9
        ([[3, 4, 5], [3, 2, 6], [2, 2, 1]], 4),   # 3->4->5->6
        ([[1]], 1),
        ([], 0),
        ([[1, 2, 3, 4, 5]], 5),                   # single strictly-increasing row
        ([[7, 7, 7], [7, 7, 7]], 1),              # all equal: no strict step
    ]
    for matrix, expected in cases:
        assert longest_increasing_path(matrix) == expected, matrix
    # naive agrees on the small cases (skip nothing here; all are small)
    for matrix, expected in cases:
        assert longest_increasing_path_naive(matrix) == expected, matrix
    print("longest_increasing_path: all cases passed")


if __name__ == "__main__":
    _test()
