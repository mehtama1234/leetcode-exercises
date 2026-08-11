"""304. Range Sum Query 2D - Immutable — https://leetcode.com/problems/range-sum-query-2d-immutable/

Given a fixed matrix, answer many "what is the sum of the rectangle from
(row1, col1) to (row2, col2)?" queries. Precompute a 2D prefix table once so each
rectangle query is O(1).
"""
from typing import List


class NumMatrixBrute:
    """Store the matrix; add up the rectangle on every query. O(rows*cols) per query.

    Correct and obvious, but a wide rectangle re-adds the same cells across many
    queries. That repeated adding is the waste the prefix table removes.
    """

    def __init__(self, matrix: List[List[int]]) -> None:
        self.matrix = matrix

    def sumRegion(self, row1: int, col1: int, row2: int, col2: int) -> int:
        total = 0
        for r in range(row1, row2 + 1):
            for c in range(col1, col2 + 1):
                total += self.matrix[r][c]
        return total


class NumMatrix:
    """Precompute a 2D prefix table once; answer each rectangle in O(1).

    Key insight: let prefix[r][c] = sum of every cell in the top-left rectangle
    from (0,0) to (r-1, c-1). Then the sum of the rectangle (row1,col1)..(row2,col2)
    is one big top-left block minus the strip above it minus the strip to its left,
    but that double-subtracts the corner they share, so we add it back once
    (inclusion-exclusion):

        big - top - left + corner
    """

    def __init__(self, matrix: List[List[int]]) -> None:
        rows = len(matrix)
        cols = len(matrix[0]) if rows else 0
        # (rows+1) x (cols+1) with a zero border so the formula needs no edge cases.
        self.prefix: List[List[int]] = [[0] * (cols + 1) for _ in range(rows + 1)]
        for r in range(rows):
            for c in range(cols):
                # current cell + block above + block left - overlap counted twice.
                self.prefix[r + 1][c + 1] = (
                    matrix[r][c]
                    + self.prefix[r][c + 1]
                    + self.prefix[r + 1][c]
                    - self.prefix[r][c]
                )

    def sumRegion(self, row1: int, col1: int, row2: int, col2: int) -> int:
        p = self.prefix
        # Shift by +1 because prefix has the zero border / is 1-indexed.
        return (
            p[row2 + 1][col2 + 1]  # whole top-left block ending at (row2, col2)
            - p[row1][col2 + 1]    # remove the strip above row1
            - p[row2 + 1][col1]    # remove the strip left of col1
            + p[row1][col1]        # add back the corner removed twice
        )


def _test() -> None:
    # Official LeetCode example.
    matrix = [
        [3, 0, 1, 4, 2],
        [5, 6, 3, 2, 1],
        [1, 2, 0, 1, 5],
        [4, 1, 0, 1, 7],
        [1, 0, 3, 0, 5],
    ]
    nm = NumMatrix(matrix)
    assert nm.sumRegion(2, 1, 4, 3) == 8, "inner rectangle"
    assert nm.sumRegion(1, 1, 2, 2) == 11, "small rectangle"
    assert nm.sumRegion(1, 2, 2, 4) == 12, "another rectangle"

    # Edge: single cell.
    assert nm.sumRegion(0, 0, 0, 0) == 3

    # Edge: whole matrix, and brute force must agree on every rectangle.
    ref = NumMatrixBrute(matrix)
    R, C = len(matrix), len(matrix[0])
    for r1 in range(R):
        for c1 in range(C):
            for r2 in range(r1, R):
                for c2 in range(c1, C):
                    assert nm.sumRegion(r1, c1, r2, c2) == ref.sumRegion(
                        r1, c1, r2, c2
                    ), (r1, c1, r2, c2)

    print("range_sum_query_2d_immutable: all cases passed")


if __name__ == "__main__":
    _test()
