"""42. Trapping Rain Water — https://leetcode.com/problems/trapping-rain-water/

Given an elevation map of bar heights, compute how many units of water it traps
after rain. Water sits above a bar up to the shorter of the tallest walls on its
two sides.

Three views are kept side by side: the honest brute force, the monotonic-stack
solution (the pattern for this chapter), and the two-pointer solution (the
tightest O(1)-space answer), so the trade-offs are visible.
"""
from typing import List


def trap_brute(height: List[int]) -> int:
    """For each position, look outward for the tallest wall on each side. O(n^2).

    Water above column i is bounded by the shorter of (tallest bar to its left,
    tallest bar to its right), minus its own height. Computing those two maxima by
    scanning outward for every column is the honest definition — and the waste we
    remove: the same maxima get rescanned again and again.
    """
    n = len(height)
    total = 0
    for i in range(n):
        left_max = max(height[: i + 1])
        right_max = max(height[i:])
        total += min(left_max, right_max) - height[i]
    return total


def trap(height: List[int]) -> int:
    """Monotonic decreasing stack, filling water in horizontal layers. O(n)/O(n).

    Keep a stack of indices whose heights are non-increasing. When the current bar
    is taller than the stack top, that top is a "valley floor" that just found a
    right wall (current bar) to go with the left wall (the new stack top after
    popping). We *resolve* that trapped layer immediately:

      - `bottom` = the popped valley floor,
      - `left` = new stack top (left wall), `i` = current bar (right wall),
      - the water sits at `min(height[left], height[i])` above the floor,
      - across the horizontal gap `i - left - 1`.

    Each bar is pushed once and popped once, so it's O(n). The water is added in
    flat horizontal slabs rather than per-column vertical straws.
    """
    stack: List[int] = []  # indices, heights non-increasing bottom -> top
    total = 0
    for i, h in enumerate(height):
        while stack and height[stack[-1]] < h:
            bottom = stack.pop()
            if not stack:
                break  # no left wall -> water spills off the left edge
            left = stack[-1]
            width = i - left - 1
            bounded = min(height[left], h) - height[bottom]
            total += width * bounded
        stack.append(i)
    return total


def trap_two_pointer(height: List[int]) -> int:
    """Two pointers, O(n) time, O(1) space — the tightest answer.

    Walk inward from both ends. Track the tallest wall seen from each side. The
    side with the smaller running max is the *binding* constraint, so we can settle
    that column now: whatever bounds it can only come from the shorter side.
    """
    if not height:
        return 0
    left, right = 0, len(height) - 1
    left_max, right_max = height[left], height[right]
    total = 0
    while left < right:
        if left_max <= right_max:
            left += 1
            left_max = max(left_max, height[left])
            total += left_max - height[left]
        else:
            right -= 1
            right_max = max(right_max, height[right])
            total += right_max - height[right]
    return total


def _test() -> None:
    cases = [
        ([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1], 6),
        ([4, 2, 0, 3, 2, 5], 9),
        ([], 0),
        ([1], 0),
        ([2, 0, 2], 2),
        ([3, 2, 1, 2, 3], 4),
        ([1, 2, 3, 4], 0),   # monotone increasing traps nothing
        ([4, 3, 2, 1], 0),   # monotone decreasing traps nothing
    ]
    for h, expected in cases:
        assert trap(h) == expected, h
        assert trap_brute(h) == expected, h
        assert trap_two_pointer(h) == expected, h
    print("trap: all cases passed")


if __name__ == "__main__":
    _test()
