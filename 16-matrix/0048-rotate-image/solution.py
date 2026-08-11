"""48. Rotate Image — https://leetcode.com/problems/rotate-image/

Rotate an n x n matrix 90 degrees clockwise, **in place**. You may not allocate
another matrix — the input grid itself must end up rotated.

Two implementations are kept side by side. The first shows the honest "where does
each cell go?" reasoning using an extra matrix, so the target mapping is explicit.
The second collapses that mapping into two in-place passes (transpose, then
reverse each row) — which is what "no extra matrix" forces you to discover.
"""
from typing import List
import copy


def rotate_with_copy(matrix: List[List[int]]) -> None:
    """Compute the rotation into a fresh grid, then copy it back. O(n^2) space.

    This is the honest first thought. Rotating 90 degrees clockwise sends the cell
    at (row, col) to (col, n-1-row): the top row becomes the right column, and so
    on. If we're allowed scratch space we just write every source cell to its
    destination and copy the result back. It works, but the extra n x n grid is the
    waste — the problem explicitly bans it, so we look for a mapping we can apply
    in place next.
    """
    n = len(matrix)
    result = [[0] * n for _ in range(n)]
    for r in range(n):
        for c in range(n):
            result[c][n - 1 - r] = matrix[r][c]
    for r in range(n):
        matrix[r][:] = result[r]  # copy back so the mutation is in place


def rotate(matrix: List[List[int]]) -> None:
    """Transpose, then reverse each row. In place, O(1) extra space.

    Key insight: a 90-degree clockwise rotation is exactly two simpler moves that
    each swap cells within the grid.

      1. Transpose — swap matrix[r][c] with matrix[c][r]. This flips the grid over
         its main diagonal, turning rows into columns.
      2. Reverse each row left-to-right.

    Do the transpose only for c > r so each pair is swapped once (not swapped back).
    Neither step needs scratch storage, so the whole rotation happens in place.
    """
    n = len(matrix)
    # 1. transpose across the main diagonal
    for r in range(n):
        for c in range(r + 1, n):
            matrix[r][c], matrix[c][r] = matrix[c][r], matrix[r][c]
    # 2. reverse each row
    for row in matrix:
        row.reverse()


def _test() -> None:
    cases = [
        (
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
            [[7, 4, 1], [8, 5, 2], [9, 6, 3]],
        ),
        (
            [[5, 1, 9, 11], [2, 4, 8, 10], [13, 3, 6, 7], [15, 14, 12, 16]],
            [[15, 13, 2, 5], [14, 3, 4, 1], [12, 6, 8, 9], [16, 7, 10, 11]],
        ),
        # edge: 1x1 grid is unchanged
        ([[42]], [[42]]),
        # edge: 2x2 grid
        ([[1, 2], [3, 4]], [[3, 1], [4, 2]]),
    ]
    for grid, expected in cases:
        a = copy.deepcopy(grid)
        rotate(a)
        assert a == expected, (grid, a)
        # the copy-based version must agree, and both mutate in place
        b = copy.deepcopy(grid)
        rotate_with_copy(b)
        assert b == expected, (grid, b)
    print("rotate_image: all cases passed")


if __name__ == "__main__":
    _test()
