"""54. Spiral Matrix — https://leetcode.com/problems/spiral-matrix/

Given an m x n grid, return all its elements in spiral order: walk the outer ring
clockwise (right across the top, down the right side, left across the bottom, up
the left side), then spiral inward and repeat until every cell is collected.
"""
from typing import List


def spiral_order(matrix: List[List[int]]) -> List[int]:
    """Peel the grid ring by ring using four shrinking boundaries. O(m*n) time.

    Key insight: a spiral is just the outer ring, then the spiral of what's left
    inside. Track four walls — top, bottom, left, right — that bound the part not
    yet visited. Each of the four directions walks along one wall, then that wall
    steps inward by one. When the walls cross, everything has been collected.

    The two mid-loop guards (`if top <= bottom` / `if left <= right`) matter for
    non-square grids: after doing the top row and right column, a single remaining
    row or column must not be walked back over in the reverse direction.
    """
    if not matrix or not matrix[0]:
        return []

    result: List[int] = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1

    while top <= bottom and left <= right:
        # top row, left -> right
        for c in range(left, right + 1):
            result.append(matrix[top][c])
        top += 1
        # right column, top -> bottom
        for r in range(top, bottom + 1):
            result.append(matrix[r][right])
        right -= 1
        # bottom row, right -> left (only if a row remains)
        if top <= bottom:
            for c in range(right, left - 1, -1):
                result.append(matrix[bottom][c])
            bottom -= 1
        # left column, bottom -> top (only if a column remains)
        if left <= right:
            for r in range(bottom, top - 1, -1):
                result.append(matrix[r][left])
            left += 1

    return result


def _test() -> None:
    cases = [
        (
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
            [1, 2, 3, 6, 9, 8, 7, 4, 5],
        ),
        (
            [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]],
            [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7],
        ),
        # edge: single row
        ([[1, 2, 3, 4]], [1, 2, 3, 4]),
        # edge: single column
        ([[1], [2], [3]], [1, 2, 3]),
        # edge: single cell
        ([[7]], [7]),
    ]
    for grid, expected in cases:
        assert spiral_order(grid) == expected, (grid, spiral_order(grid))
    print("spiral_matrix: all cases passed")


if __name__ == "__main__":
    _test()
