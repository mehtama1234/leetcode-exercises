"""62. Unique Paths — https://leetcode.com/problems/unique-paths/

A robot sits in the top-left cell of an m x n grid and wants to reach the
bottom-right cell. It can only move right or down. Return how many distinct
paths there are.

The full 2-D table makes the recurrence obvious; a 1-row rolling version follows
because each row only depends on the row above it.
"""
from typing import List


def unique_paths_2d(m: int, n: int) -> int:
    """Bottom-up 2-D table. O(m*n) time, O(m*n) space.

    Define dp[i][j] = number of distinct paths from the top-left corner to cell
    (i, j). To arrive at (i, j) the robot's last move was either a step DOWN from
    (i-1, j) or a step RIGHT from (i, j-1) — those are the only two ways in, and
    they lead to disjoint sets of paths. So:

        dp[i][j] = dp[i-1][j] + dp[i][j-1]

    The top row and left column are all 1: there's exactly one way to reach any
    cell on the top edge (keep going right) or left edge (keep going down).
    """
    dp: List[List[int]] = [[1] * n for _ in range(m)]
    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = dp[i - 1][j] + dp[i][j - 1]
    return dp[m - 1][n - 1]


def unique_paths(m: int, n: int) -> int:
    """Same recurrence, one rolling row. O(m*n) time, O(n) space.

    dp[i][j] = dp[i-1][j] + dp[i][j-1] only reads the cell directly above and the
    cell directly to the left. If we keep a single row and update it left to
    right, then at the moment we compute column j:
      - row[j] still holds the OLD value = dp[i-1][j] (the cell above), and
      - row[j-1] already holds the NEW value = dp[i][j-1] (the cell to the left).
    So `row[j] += row[j-1]` folds both terms in place. Start the row as all 1s
    (the top row), and each pass turns it into the next row down.
    """
    row = [1] * n
    for _ in range(1, m):
        for j in range(1, n):
            row[j] += row[j - 1]
    return row[n - 1]


def _test() -> None:
    cases = [
        ((3, 7), 28),   # official example 1
        ((3, 2), 3),    # official example 2
        ((1, 1), 1),    # single cell — one (empty) path
        ((1, 10), 1),   # single row — only one way (all right)
        ((10, 1), 1),   # single column — only one way (all down)
        ((3, 3), 6),
    ]
    for (m, n), expected in cases:
        assert unique_paths(m, n) == expected, (m, n)
        assert unique_paths_2d(m, n) == expected, (m, n)
    print("unique_paths: all cases passed")


if __name__ == "__main__":
    _test()
