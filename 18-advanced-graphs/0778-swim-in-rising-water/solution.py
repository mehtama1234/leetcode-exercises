"""778. Swim in Rising Water — https://leetcode.com/problems/swim-in-rising-water/

On an n×n grid, cell (i,j) has an elevation. At time t the water level is t, and
you can be on any cell whose elevation ≤ t. You start at (0,0) and want (n-1,n-1);
you may step to any 4-adjacent cell instantly. Return the earliest time you can
arrive.

The cost of a path is the *highest* cell along it (you must wait for the water to
rise past the tallest barrier). So we want the path whose maximum elevation is as
small as possible — a "minimax path". Two clean approaches: Dijkstra where the
path cost is a max instead of a sum, and binary search on the answer + reachability
DFS.
"""
from typing import List, Tuple
import heapq


def swim_in_water(grid: List[List[int]]) -> int:
    """Dijkstra with a min-max cost. O(n^2 log n) time, O(n^2) space.

    Normal Dijkstra minimizes a *sum* of edge weights. Here the cost of reaching a
    cell is the largest elevation on the best path to it — so we relax with
    `max(cost_so_far, elevation)` instead of `+`. The min-heap always expands the
    reachable cell with the smallest "worst barrier so far", and the moment we pop
    the destination that value is the answer: the earliest time the whole path is
    submerged enough to walk.
    """
    n = len(grid)
    seen = [[False] * n for _ in range(n)]
    # heap holds (max elevation needed to reach this cell, row, col)
    heap: List[Tuple[int, int, int]] = [(grid[0][0], 0, 0)]

    while heap:
        t, r, c = heapq.heappop(heap)
        if seen[r][c]:
            continue
        seen[r][c] = True
        if r == n - 1 and c == n - 1:
            return t  # first time we pop the goal, t is the minimal max-elevation
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and not seen[nr][nc]:
                # cost to stand on (nr,nc) via here = max(barrier so far, that cell)
                heapq.heappush(heap, (max(t, grid[nr][nc]), nr, nc))
    return -1  # unreachable on a valid grid this never happens


def swim_in_water_binary_search(grid: List[List[int]]) -> int:
    """Binary search on the answer + DFS reachability. O(n^2 log(n^2)) time.

    Kept beside the Dijkstra version because it exposes the "minimax" nature
    directly. The answer t is monotonic: if you can reach the end when water = t,
    you can also at any t' > t (more cells are open). So binary search the
    smallest t for which a DFS using only cells ≤ t connects start to end.
    """
    n = len(grid)
    lo, hi = grid[0][0], max(max(row) for row in grid)

    def can_reach(t: int) -> bool:
        if grid[0][0] > t:
            return False
        stack = [(0, 0)]
        seen = {(0, 0)}
        while stack:
            r, c = stack.pop()
            if r == n - 1 and c == n - 1:
                return True
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if (0 <= nr < n and 0 <= nc < n and (nr, nc) not in seen
                        and grid[nr][nc] <= t):
                    seen.add((nr, nc))
                    stack.append((nr, nc))
        return False

    while lo < hi:
        mid = (lo + hi) // 2
        if can_reach(mid):
            hi = mid          # mid works, maybe smaller does too
        else:
            lo = mid + 1      # mid too shallow, need more water
    return lo


def _test() -> None:
    cases = [
        ([[0, 2], [1, 3]], 3),
        ([[0, 1, 2, 3, 4],
          [24, 23, 22, 21, 5],
          [12, 13, 14, 15, 16],
          [11, 17, 18, 19, 20],
          [10, 9, 8, 7, 6]], 16),
        ([[0]], 0),                      # 1x1 grid: already at goal
        ([[0, 1], [2, 3]], 3),           # must clear the tallest corner
    ]
    for grid, expected in cases:
        assert swim_in_water(grid) == expected, grid
        # Binary-search approach must agree with Dijkstra on every case.
        assert swim_in_water_binary_search(grid) == expected, grid
    print("swim_in_water: all cases passed")


if __name__ == "__main__":
    _test()
