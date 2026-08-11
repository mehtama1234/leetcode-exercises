"""200. Number of Islands — https://leetcode.com/problems/number-of-islands/

Given a grid of '1' (land) and '0' (water), count the islands. An island is a
group of land cells connected horizontally or vertically (not diagonally).

The whole problem is "how many connected blobs of land are there?". Once you see
each blob as a connected component of a grid-graph, the answer is: walk the grid,
and every time you step onto a fresh piece of land, flood-fill the entire blob it
belongs to and count that as one island.
"""
from typing import List


def num_islands(grid: List[List[str]]) -> int:
    """Scan + flood fill. O(rows*cols) time, O(rows*cols) worst-case space.

    Every cell is visited a constant number of times. When we find an unvisited
    '1', it can only belong to an island we have not counted yet (if it were part
    of a counted island, the flood fill would already have sunk it). So we bump
    the counter once and then sink the *whole* connected blob so it can never be
    counted again. The sinking (turning '1' into '0') doubles as our "visited"
    marker, which is why we need no separate visited set.
    """
    if not grid or not grid[0]:
        return 0

    rows, cols = len(grid), len(grid[0])

    def sink(r: int, c: int) -> None:
        # Iterative DFS with an explicit stack so a huge island can't blow the
        # Python recursion limit.
        stack = [(r, c)]
        while stack:
            i, j = stack.pop()
            if i < 0 or i >= rows or j < 0 or j >= cols:
                continue
            if grid[i][j] != "1":
                continue
            grid[i][j] = "0"  # mark visited by sinking it
            stack.extend([(i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)])

    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                count += 1
                sink(r, c)
    return count


def _test() -> None:
    g1 = [
        ["1", "1", "1", "1", "0"],
        ["1", "1", "0", "1", "0"],
        ["1", "1", "0", "0", "0"],
        ["0", "0", "0", "0", "0"],
    ]
    assert num_islands([row[:] for row in g1]) == 1

    g2 = [
        ["1", "1", "0", "0", "0"],
        ["1", "1", "0", "0", "0"],
        ["0", "0", "1", "0", "0"],
        ["0", "0", "0", "1", "1"],
    ]
    assert num_islands([row[:] for row in g2]) == 3

    # Edge cases
    assert num_islands([]) == 0                       # empty grid
    assert num_islands([["0", "0"], ["0", "0"]]) == 0  # all water
    assert num_islands([["1"]]) == 1                   # single land cell
    # Diagonal touch does NOT connect — two separate islands
    assert num_islands([["1", "0"], ["0", "1"]]) == 2

    print("num_islands: all cases passed")


if __name__ == "__main__":
    _test()
