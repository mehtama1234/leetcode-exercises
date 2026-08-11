"""303. Range Sum Query - Immutable — https://leetcode.com/problems/range-sum-query-immutable/

Given a fixed array, answer many "what is the sum of nums[left..right]?" queries.
The array never changes, but you may be asked thousands of ranges — so precompute
once and answer each query in O(1).
"""
from typing import List


class NumArrayBrute:
    """Store the array; add up the range on every query. O(n) per query.

    This is the honest first version: sumRange just walks from left to right and
    adds. It's correct, but if you ask q queries each spanning most of the array,
    you re-add the same numbers over and over — that repeated adding is the waste.
    """

    def __init__(self, nums: List[int]) -> None:
        self.nums = nums

    def sumRange(self, left: int, right: int) -> int:
        return sum(self.nums[left : right + 1])


class NumArray:
    """Precompute prefix sums once; answer each range in O(1).

    Key insight: the sum of nums[left..right] is
        (sum of the first right+1 numbers) - (sum of the first left numbers).
    So if we store `prefix[i] = nums[0] + ... + nums[i-1]` (prefix[0] = 0), then
    any range sum is just one subtraction: prefix[right+1] - prefix[left]. The
    per-query scan disappears — all the adding happened once, up front.
    """

    def __init__(self, nums: List[int]) -> None:
        # prefix[i] = sum of the first i elements. Length n+1, prefix[0] = 0.
        self.prefix: List[int] = [0] * (len(nums) + 1)
        for i, x in enumerate(nums):
            self.prefix[i + 1] = self.prefix[i] + x

    def sumRange(self, left: int, right: int) -> int:
        # right+1 counts elements up to and including index right;
        # subtracting prefix[left] removes everything before left.
        return self.prefix[right + 1] - self.prefix[left]


def _test() -> None:
    # Official LeetCode example.
    na = NumArray([-2, 0, 3, -5, 2, -1])
    assert na.sumRange(0, 2) == 1, "sum of [-2,0,3]"
    assert na.sumRange(2, 5) == -1, "sum of [3,-5,2,-1]"
    assert na.sumRange(0, 5) == -3, "whole array"

    # Single-element range.
    assert na.sumRange(3, 3) == -5, "one element"

    # Edge: length-1 array, and the brute force must agree everywhere.
    one = NumArray([7])
    assert one.sumRange(0, 0) == 7

    ref = NumArrayBrute([-2, 0, 3, -5, 2, -1])
    for left in range(6):
        for right in range(left, 6):
            assert na.sumRange(left, right) == ref.sumRange(left, right), (left, right)

    print("range_sum_query_immutable: all cases passed")


if __name__ == "__main__":
    _test()
