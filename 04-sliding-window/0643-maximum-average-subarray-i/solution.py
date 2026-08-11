"""643. Maximum Average Subarray I — https://leetcode.com/problems/maximum-average-subarray-i/

Given an array `nums` and an integer `k`, find the contiguous block of exactly
`k` numbers with the largest average, and return that average.

The average of a fixed-size block is just its sum divided by `k`. Since `k` is
constant, maximizing the average is the same as maximizing the sum — so the real
job is "biggest sum of any window of length k". Two versions are kept side by
side so the reason the fast one exists is visible.
"""
from typing import List


def find_max_average_brute(nums: List[int], k: int) -> float:
    """Re-add every window from scratch. O(n*k) time, O(1) space.

    The definition turned straight into code: for each start position, sum the k
    numbers there and keep the best. It works, but notice that neighboring
    windows overlap in k-1 elements — we re-add those same numbers again and
    again. That repeated adding is the waste we remove next.
    """
    n = len(nums)
    best = float("-inf")
    for i in range(n - k + 1):
        window_sum = sum(nums[i:i + k])
        best = max(best, window_sum)
    return best / k


def find_max_average(nums: List[int], k: int) -> float:
    """Slide a running sum. O(n) time, O(1) space.

    Key insight: moving a window of size k one step right doesn't change most of
    it — you drop the element leaving on the left and add the element entering on
    the right. So instead of re-summing k numbers each step, keep a running sum
    and update it with two arithmetic operations. Every element is added once and
    removed once, so the whole scan is O(n).
    """
    window_sum = sum(nums[:k])       # the first window, summed once
    best = window_sum
    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]  # add the newcomer, drop the leaver
        best = max(best, window_sum)
    return best / k


def _test() -> None:
    cases = [
        (([1, 12, -5, -6, 50, 3], 4), 12.75),
        (([5], 1), 5.0),
        (([0, 4, 0, 3, 2], 1), 4.0),          # k == 1: best single element
        (([-1, -2, -3, -4], 2), -1.5),        # all negative
        (([4, 4, 4, 4], 2), 4.0),             # all equal
    ]
    for (nums, k), expected in cases:
        assert abs(find_max_average(nums, k) - expected) < 1e-9, (nums, k)
        # brute force must agree with the fast version on every case
        assert abs(find_max_average_brute(nums, k) - expected) < 1e-9, (nums, k)
    print("find_max_average: all cases passed")


if __name__ == "__main__":
    _test()
