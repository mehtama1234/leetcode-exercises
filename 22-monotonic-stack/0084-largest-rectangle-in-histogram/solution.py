"""84. Largest Rectangle in Histogram — https://leetcode.com/problems/largest-rectangle-in-histogram/

Given bar heights (all width 1), find the area of the largest axis-aligned
rectangle that fits entirely under the skyline.

The brute force and the monotonic-stack solution are kept side by side so the
reason the fast one exists is visible: the stack removes the repeated "how far
left/right can this bar stretch?" scans by resolving each bar exactly once, at
the moment the answer for it becomes known.
"""
from typing import List


def largest_rectangle_brute(heights: List[int]) -> int:
    """For each bar, expand left and right while bars stay >= its height. O(n^2).

    A rectangle is pinned by its shortest bar. So treat every bar as the shortest
    one and see how wide a rectangle of that height can grow: walk left and right
    until you hit a bar strictly lower. Correct, but every bar re-walks its
    neighbours — that repeated scanning is the waste the stack removes.
    """
    n = len(heights)
    best = 0
    for i in range(n):
        left = i
        while left - 1 >= 0 and heights[left - 1] >= heights[i]:
            left -= 1
        right = i
        while right + 1 < n and heights[right + 1] >= heights[i]:
            right += 1
        best = max(best, heights[i] * (right - left + 1))
    return best


def largest_rectangle(heights: List[int]) -> int:
    """Monotonic increasing stack. O(n) time, O(n) space.

    Key insight: a bar's rectangle is decided by the first strictly-shorter bar to
    its left and to its right. Keep a stack of bar indices whose heights are
    strictly increasing. When the current bar is shorter than the stack top, that
    top can never grow rightward past here — so we *resolve* it now:

      - its right boundary is the current index i (first shorter bar to the right),
      - its left boundary is the new stack top after popping (first shorter bar to
        the left), or the very start if the stack is empty.

    The width is `i - left_boundary - 1` and the area is `height * width`. Each
    bar is pushed once and popped once, so the total work is O(n) even though the
    inner `while` looks nested. A trailing sentinel of height 0 flushes anything
    still on the stack at the end.
    """
    stack: List[int] = []  # indices, heights strictly increasing bottom -> top
    best = 0
    for i, h in enumerate(heights + [0]):  # sentinel 0 flushes the stack
        while stack and heights[stack[-1]] > h:
            top = stack.pop()
            height = heights[top]
            # after popping, the new top (if any) is the first shorter bar to the
            # left; width spans everything strictly between it and i.
            left = stack[-1] if stack else -1
            width = i - left - 1
            best = max(best, height * width)
        stack.append(i)
    return best


def _test() -> None:
    cases = [
        ([2, 1, 5, 6, 2, 3], 10),
        ([2, 4], 4),
        ([1], 1),
        ([2, 2, 2], 6),          # flat: one wide rectangle
        ([5, 4, 3, 2, 1], 9),    # strictly decreasing
        ([1, 2, 3, 4, 5], 9),    # strictly increasing
        ([0], 0),
    ]
    for heights, expected in cases:
        assert largest_rectangle(heights) == expected, heights
        assert largest_rectangle_brute(heights) == expected, heights
    print("largest_rectangle: all cases passed")


if __name__ == "__main__":
    _test()
