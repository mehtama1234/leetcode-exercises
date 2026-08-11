"""704. Binary Search — https://leetcode.com/problems/binary-search/

Given a sorted array `nums` (ascending, all distinct) and a `target`, return the
index of `target` if it is present, otherwise -1.

Two implementations sit side by side so the *reason* binary search exists is
visible: the linear scan is the honest starting point, and binary search is what
you get by asking "the array is sorted — what am I ignoring?".
"""
from typing import List


def search_linear(nums: List[int], target: int) -> int:
    """Look at every element left to right. O(n) time, O(1) space.

    This is the definition turned into code: "is target in the list, and where?"
    It never uses the fact that the array is sorted — it treats a sorted array
    exactly like a shuffled one. That ignored structure is the waste we remove.
    """
    for i, x in enumerate(nums):
        if x == target:
            return i
    return -1


def search(nums: List[int], target: int) -> int:
    """Binary search. O(log n) time, O(1) space.

    Key insight: because the array is sorted, one comparison against the middle
    element tells us which *half* the target must be in — the other half can be
    thrown away entirely. Each step deletes half of what's left, so we reach the
    answer in about log2(n) steps instead of n.

    We keep a closed window [lo, hi] of indices that could still hold target and
    shrink it until it's empty. `mid = lo + (hi - lo) // 2` avoids overflow in
    languages with fixed-width ints (a good habit even though Python is immune).
    """
    lo, hi = 0, len(nums) - 1
    while lo <= hi:  # window is non-empty while lo <= hi
        mid = lo + (hi - lo) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = mid + 1  # target is strictly to the right
        else:
            hi = mid - 1  # target is strictly to the left
    return -1


def _test() -> None:
    cases = [
        (([-1, 0, 3, 5, 9, 12], 9), 4),
        (([-1, 0, 3, 5, 9, 12], 2), -1),
        (([5], 5), 0),
        (([5], -5), -1),
        (([], 1), -1),            # empty array
        (([1, 2, 3, 4, 5], 1), 0),  # target at the very start
        (([1, 2, 3, 4, 5], 5), 4),  # target at the very end
    ]
    for (nums, target), expected in cases:
        assert search(nums, target) == expected, (nums, target)
        # linear scan must agree with binary search on every case
        assert search_linear(nums, target) == expected, (nums, target)
    print("binary_search: all cases passed")


if __name__ == "__main__":
    _test()
