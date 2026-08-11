"""153. Find Minimum in Rotated Sorted Array — https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/

A sorted array of distinct numbers has been rotated some unknown number of times
(the front chunk moved to the back). Return the smallest element. Do it in
O(log n).

Two implementations sit side by side so the reason binary search still works —
even though the array isn't fully sorted — is visible.
"""
from typing import List


def find_min_linear(nums: List[int]) -> int:
    """Just take the minimum. O(n) time, O(1) space.

    The honest first thought: scan everything and keep the smallest. Correct, but
    it reads all n elements and ignores that the array is *almost* sorted — only
    one "cliff" breaks the order. That structure is what we exploit next.
    """
    return min(nums)


def find_min(nums: List[int]) -> int:
    """Binary search on which half holds the rotation point. O(log n), O(1) space.

    Key insight: rotating a sorted array leaves exactly one place where a larger
    value is immediately followed by a smaller one — the "cliff" — and the minimum
    is the value right after that cliff. Comparing the middle element to the
    rightmost element tells us which side the cliff (and thus the minimum) is on:

      - If nums[mid] > nums[hi], the array wraps somewhere in (mid, hi]. The
        minimum is strictly to the right of mid, so move lo = mid + 1.
      - Otherwise nums[mid] <= nums[hi], meaning [mid, hi] is properly sorted, so
        the minimum is at mid or to its left; move hi = mid (keep mid — it might
        BE the minimum).

    Comparing to `hi` rather than `lo` is what makes the two cases clean and
    unambiguous. The window shrinks to a single element, which is the answer.
    """
    lo, hi = 0, len(nums) - 1
    while lo < hi:  # stop when the window is a single element
        mid = lo + (hi - lo) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1  # minimum is to the right of mid
        else:
            hi = mid      # minimum is mid or to its left (don't drop mid)
    return nums[lo]


def _test() -> None:
    cases = [
        ([3, 4, 5, 1, 2], 1),
        ([4, 5, 6, 7, 0, 1, 2], 0),
        ([11, 13, 15, 17], 11),   # not rotated at all
        ([1], 1),                 # single element
        ([2, 1], 1),              # smallest possible rotation
        ([5, 1, 2, 3, 4], 1),     # rotated so min is second
    ]
    for nums, expected in cases:
        assert find_min(nums) == expected, nums
        # brute force must agree on every case
        assert find_min_linear(nums) == expected, nums
    print("find_min_rotated: all cases passed")


if __name__ == "__main__":
    _test()
