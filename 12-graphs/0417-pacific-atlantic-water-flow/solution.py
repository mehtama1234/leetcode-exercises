"""417. Pacific Atlantic Water Flow — https://leetcode.com/problems/pacific-atlantic-water-flow/

Given a grid of heights, water flows from a cell to a neighbor (up/down/left/right)
only if the neighbor is not higher. The Pacific touches the top and left edges,
the Atlantic touches the bottom and right edges. Return every cell from which
water can reach BOTH oceans.

Instead of asking "from this cell, can water reach the ocean?" (a search per cell),
flip it: start AT each ocean's edge and walk UPHILL to find every cell that can
drain into that ocean. The answer is the intersection of the two reachable sets.
"""
from typing import List, Set, Tuple


def pacific_atlantic(heights: List[List[int]]) -> List[List[int]]:
    """Reverse BFS/DFS from both oceans. O(rows*cols) time, O(rows*cols) space.

    The naive idea — for each cell, search downhill and see if it hits an ocean —
    repeats a huge amount of work: a cell high in the mountains is re-explored by
    every downstream cell that flows through it. The fix is to reverse the flow.

    Water reaches the ocean iff, walking backward FROM the ocean, we can climb to
    the cell without ever going downhill. So we flood inward from each ocean's
    border, moving to a neighbor only when it is >= the current height (uphill in
    reverse). Do that from the Pacific border and the Atlantic border separately;
    a cell that both floods reach can drain to both oceans.
    """
    if not heights or not heights[0]:
        return []

    rows, cols = len(heights), len(heights[0])

    def flood(starts: List[Tuple[int, int]]) -> Set[Tuple[int, int]]:
        reachable: Set[Tuple[int, int]] = set()
        stack = list(starts)
        while stack:
            r, c = stack.pop()
            if (r, c) in reachable:
                continue
            reachable.add((r, c))
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if (
                    0 <= nr < rows
                    and 0 <= nc < cols
                    and (nr, nc) not in reachable
                    # reverse flow: step only to a neighbor at least as HIGH,
                    # because forward it would flow downhill back toward us.
                    and heights[nr][nc] >= heights[r][c]
                ):
                    stack.append((nr, nc))
        return reachable

    # Pacific hugs the top row and left column.
    pacific_starts = [(0, c) for c in range(cols)] + [(r, 0) for r in range(rows)]
    # Atlantic hugs the bottom row and right column.
    atlantic_starts = [(rows - 1, c) for c in range(cols)] + [
        (r, cols - 1) for r in range(rows)
    ]

    pacific = flood(pacific_starts)
    atlantic = flood(atlantic_starts)

    return [[r, c] for (r, c) in pacific & atlantic]


def _test() -> None:
    heights = [
        [1, 2, 2, 3, 5],
        [3, 2, 3, 4, 4],
        [2, 4, 5, 3, 1],
        [6, 7, 1, 4, 5],
        [5, 1, 1, 2, 4],
    ]
    expected = {
        (0, 4), (1, 3), (1, 4), (2, 2), (3, 0), (3, 1), (4, 0),
    }
    result = {tuple(cell) for cell in pacific_atlantic(heights)}
    assert result == expected, result

    # Edge cases
    assert pacific_atlantic([]) == []               # empty grid
    # Single cell touches both oceans trivially.
    assert pacific_atlantic([[42]]) == [[0, 0]]
    # A flat 2x2: every cell can reach both oceans (all heights equal).
    flat = {tuple(c) for c in pacific_atlantic([[1, 1], [1, 1]])}
    assert flat == {(0, 0), (0, 1), (1, 0), (1, 1)}

    print("pacific_atlantic: all cases passed")


if __name__ == "__main__":
    _test()
