"""73. Set Matrix Zeroes — https://leetcode.com/problems/set-matrix-zeroes/

If any cell in an m x n grid is 0, set that cell's entire row and entire column
to 0 — **in place**. The catch is doing it without an extra O(m+n) marker array.

Two implementations are kept side by side: the honest O(m+n)-space version that
just records which rows and columns to blank, and the O(1)-space version that
reuses the grid's own first row and column as those markers.
"""
from typing import List
import copy


def set_zeroes_marker(matrix: List[List[int]]) -> None:
    """Record zero rows/cols in two sets, then blank them. O(m+n) extra space.

    This is the honest first pass. You can't zero a row the moment you see a 0,
    because the fresh zeros you write would trigger more rows/columns to blank on a
    later scan — a chain reaction that wipes the whole grid. So you *first* note
    every row and column that originally held a 0, then blank them in a second pass
    over untouched information. The two sets are the waste we remove next.
    """
    zero_rows: set[int] = set()
    zero_cols: set[int] = set()
    m, n = len(matrix), len(matrix[0])

    for r in range(m):
        for c in range(n):
            if matrix[r][c] == 0:
                zero_rows.add(r)
                zero_cols.add(c)

    for r in range(m):
        for c in range(n):
            if r in zero_rows or c in zero_cols:
                matrix[r][c] = 0


def set_zeroes(matrix: List[List[int]]) -> None:
    """Use row 0 and column 0 as the marker arrays. In place, O(1) extra space.

    Key insight: we don't need separate storage for "which rows/cols to zero" — the
    grid already has an unused strip we can repurpose. Row 0 remembers which
    columns must be blanked, and column 0 remembers which rows must be blanked.

    The one conflict is cell (0,0), which both strips want to use. So track column 0
    separately in a single boolean, then:

      1. Scan the grid; when matrix[r][c] == 0, set the markers matrix[r][0] and
         matrix[0][c] (and the col0 flag if c == 0).
      2. Blank the interior (r>=1, c>=1) based on those markers.
      3. Blank row 0 if matrix[0][0] was marked, and column 0 if the flag was set.

    Interior is done before the first row/column so the markers survive until read.
    """
    m, n = len(matrix), len(matrix[0])
    first_col_zero = False

    # 1. set markers on row 0 / column 0
    for r in range(m):
        if matrix[r][0] == 0:
            first_col_zero = True
        for c in range(1, n):
            if matrix[r][c] == 0:
                matrix[r][0] = 0
                matrix[0][c] = 0

    # 2. blank the interior using the markers
    for r in range(1, m):
        for c in range(1, n):
            if matrix[r][0] == 0 or matrix[0][c] == 0:
                matrix[r][c] = 0

    # 3. blank row 0 and column 0 themselves, last, so markers stayed intact
    if matrix[0][0] == 0:
        for c in range(n):
            matrix[0][c] = 0
    if first_col_zero:
        for r in range(m):
            matrix[r][0] = 0


def _test() -> None:
    cases = [
        (
            [[1, 1, 1], [1, 0, 1], [1, 1, 1]],
            [[1, 0, 1], [0, 0, 0], [1, 0, 1]],
        ),
        (
            [[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]],
            [[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]],
        ),
        # edge: a zero in the first row and first column
        (
            [[0, 2, 3], [4, 5, 6]],
            [[0, 0, 0], [0, 5, 6]],
        ),
        # edge: no zeros at all -> grid unchanged
        (
            [[1, 2], [3, 4]],
            [[1, 2], [3, 4]],
        ),
        # edge: single cell that is zero
        ([[0]], [[0]]),
    ]
    for grid, expected in cases:
        a = copy.deepcopy(grid)
        set_zeroes(a)
        assert a == expected, (grid, a)
        # the marker-based version must agree, and both mutate in place
        b = copy.deepcopy(grid)
        set_zeroes_marker(b)
        assert b == expected, (grid, b)
    print("set_matrix_zeroes: all cases passed")


if __name__ == "__main__":
    _test()
