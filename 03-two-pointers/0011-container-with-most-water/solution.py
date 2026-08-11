"""11. Container With Most Water — https://leetcode.com/problems/container-with-most-water/

Each array value is a vertical line's height at that x-position. Pick two lines so
that the water held between them (width times the shorter line) is as large as
possible, and return that maximum area.
"""
from typing import List


def max_area_brute(height: List[int]) -> int:
    """Try every pair of lines. O(n^2) time, O(1) space.

    Straight from the definition: the area for lines i and j is
    (j - i) * min(height[i], height[j]); take the best over all pairs. Correct,
    but it re-tests every pair even though most of them can never be optimal —
    that's the waste the two-pointer version skips past.
    """
    n = len(height)
    best = 0
    for i in range(n):
        for j in range(i + 1, n):
            area = (j - i) * min(height[i], height[j])
            if area > best:
                best = area
    return best


def max_area(height: List[int]) -> int:
    """Two pointers from the ends, always move the shorter wall. O(n) time, O(1) space.

    Key insight: start with the widest possible container — the two outermost
    lines. Area is width * min(left, right). To find anything bigger we must give
    up width (the pointers can only move inward), so the only hope of a larger
    area is a taller shorter wall.

    The shorter wall is the one capping the area right now, so move *it* inward;
    keeping it and moving the taller wall only loses width while the height stays
    pinned by the same short wall — strictly worse. Discarding the shorter wall
    provably throws away no better container, so a single inward sweep finds the
    max.
    """
    left, right = 0, len(height) - 1
    best = 0
    while left < right:
        width = right - left
        area = width * min(height[left], height[right])
        if area > best:
            best = area
        # Move the shorter wall inward; ties can move either side.
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return best


def _test() -> None:
    cases = [
        ([1, 8, 6, 2, 5, 4, 8, 3, 7], 49),
        ([1, 1], 1),
        ([4, 3, 2, 1, 4], 16),   # the two outer 4s, width 4
        ([1, 2, 1], 2),
        ([2, 3, 10, 5, 7, 8, 9], 36),
    ]
    for height, expected in cases:
        assert max_area(height) == expected, height
        # brute force must agree with the fast version on every case
        assert max_area_brute(height) == expected, height
    print("max_area: all cases passed")


if __name__ == "__main__":
    _test()
