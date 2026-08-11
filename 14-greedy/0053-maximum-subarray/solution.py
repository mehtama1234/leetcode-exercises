"""53. Maximum Subarray — https://leetcode.com/problems/maximum-subarray/

Given an integer array, find the contiguous subarray (at least one element) with
the largest sum, and return that sum.
"""
from typing import List


def max_sub_array_brute(nums: List[int]) -> int:
    """Try every contiguous subarray. O(n^2) time, O(1) space.

    The definition turned into code: for each start i, extend the end j and track
    the running sum, keeping the best seen. It's correct and it's the honest first
    attempt — but for every start it re-adds the same tail elements over and over.
    That repeated summing is the waste we remove.
    """
    n = len(nums)
    best = nums[0]
    for i in range(n):
        running = 0
        for j in range(i, n):
            running += nums[j]
            if running > best:
                best = running
    return best


def max_sub_array(nums: List[int]) -> int:
    """Kadane's algorithm — one greedy pass. O(n) time, O(1) space.

    Greedy choice at each element x: the best subarray ENDING at x is either
    - x on its own, or
    - x glued onto the best subarray ending at the previous element.

    So `cur = max(x, cur + x)`. The subtle part is *why* it's safe to throw away
    the running sum whenever it goes negative: a negative prefix can only drag
    down anything that follows it, so starting fresh at x is never worse than
    carrying that deadweight forward. We keep a separate `best` because the
    globally-best subarray ends at *some* position, and by checking `cur` at every
    position we're guaranteed to see it.
    """
    cur = nums[0]   # best subarray sum ending exactly at the current index
    best = nums[0]  # best subarray sum seen ending anywhere so far
    for x in nums[1:]:
        cur = max(x, cur + x)   # extend, or start over at x
        best = max(best, cur)
    return best


def _test() -> None:
    cases = [
        ([-2, 1, -3, 4, -1, 2, 1, -5, 4], 6),   # [4, -1, 2, 1]
        ([1], 1),
        ([5, 4, -1, 7, 8], 23),                  # whole array
        # all negative: must still pick one element (the least negative)
        ([-3, -1, -2], -1),
        # single negative
        ([-5], -5),
        # a dip worth crossing vs. one not worth crossing
        ([1, -2, 3], 3),
    ]
    for nums, expected in cases:
        assert max_sub_array(nums) == expected, nums
        # Kadane must agree with the honest brute force on every case
        assert max_sub_array_brute(nums) == expected, nums
    print("max_sub_array: all cases passed")


if __name__ == "__main__":
    _test()
