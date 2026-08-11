"""33. Search in Rotated Sorted Array — https://leetcode.com/problems/search-in-rotated-sorted-array/

A sorted array of distinct numbers was rotated at some unknown pivot. Given a
target, return its index, or -1 if it's absent. Must run in O(log n).

Two implementations sit side by side so the reason one binary-search pass can
handle the rotation is visible.
"""
from typing import List


def search_linear(nums: List[int], target: int) -> int:
    """Scan every element. O(n) time, O(1) space.

    The honest first thought: look at each value until you find the target. It
    works, but ignores that the array is two sorted runs — exactly the structure
    that lets us throw away half the array per step.
    """
    for i, x in enumerate(nums):
        if x == target:
            return i
    return -1


def search(nums: List[int], target: int) -> int:
    """One binary-search pass over the rotated array. O(log n), O(1) space.

    Key insight: split at mid and at least ONE of the two halves [lo, mid] and
    [mid, hi] is fully sorted (the rotation seam can only sit in one of them).
    Identify the sorted half by comparing endpoints, then check whether target
    falls inside that half's known range:

      - If [lo, mid] is sorted (nums[lo] <= nums[mid]):
          if nums[lo] <= target < nums[mid], target is in the left half -> go left,
          else -> go right.
      - Otherwise [mid, hi] is sorted:
          if nums[mid] < target <= nums[hi], target is in the right half -> go right,
          else -> go left.

    Because we always recurse into a range we can reason about, each step still
    discards half the array, preserving O(log n).
    """
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:            # left half [lo, mid] is sorted
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1                 # target is inside the sorted left half
            else:
                lo = mid + 1                 # otherwise it's in the right half
        else:                                # right half [mid, hi] is sorted
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1                 # target is inside the sorted right half
            else:
                hi = mid - 1                 # otherwise it's in the left half
    return -1


def _test() -> None:
    cases = [
        (([4, 5, 6, 7, 0, 1, 2], 0), 4),
        (([4, 5, 6, 7, 0, 1, 2], 3), -1),
        (([1], 0), -1),
        (([1], 1), 0),
        (([5, 1, 3], 5), 0),          # target is the pivot's left edge
        (([4, 5, 6, 7, 0, 1, 2], 4), 0),  # target at the very front
        (([4, 5, 6, 7, 0, 1, 2], 2), 6),  # target at the very back
        (([3, 1], 1), 1),             # tiny rotated array
    ]
    for (nums, target), expected in cases:
        assert search(nums, target) == expected, (nums, target)
        # linear scan must agree on every case
        assert search_linear(nums, target) == expected, (nums, target)
    print("search_rotated: all cases passed")


if __name__ == "__main__":
    _test()
