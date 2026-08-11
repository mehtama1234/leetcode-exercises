"""152. Maximum Product Subarray — https://leetcode.com/problems/maximum-product-subarray/

Find the contiguous subarray with the largest product and return that product.
The array can contain negatives and zeros, which is what makes it interesting.

The naive O(n^2) scan and the O(n) rolling-min/max DP are kept side by side so
the reason the fast one has to track *two* running values is visible.
"""
from typing import List


def max_product_brute(nums: List[int]) -> int:
    """Try every subarray, multiply it out. O(n^2) time, O(1) space.

    Honest first move: for each start i, extend to each end j and keep a running
    product, tracking the best. Correct, but it re-multiplies overlapping
    prefixes over and over — that repeated work is what the DP removes.
    """
    best = nums[0]
    for i in range(len(nums)):
        prod = 1
        for j in range(i, len(nums)):
            prod *= nums[j]
            best = max(best, prod)
    return best


def max_product(nums: List[int]) -> int:
    """Rolling max AND min ending at each index. O(n) time, O(1) space.

    The twist over ordinary max-subarray: a negative number flips sign, so the
    *smallest* (most negative) product so far can become the *largest* the moment
    we hit another negative. So we can't track only the running max — we must
    also carry the running min.

    For each x, the best product of a subarray ending here is one of three
    things: x alone (start fresh), max_so_far * x, or min_so_far * x. When x is
    negative, multiplying swaps which of max/min is bigger, so we compute both
    candidates and take the new max and min from them.
    """
    best = cur_max = cur_min = nums[0]
    for x in nums[1:]:
        # x might be negative, so max_so_far*x and min_so_far*x can trade places
        candidates = (x, cur_max * x, cur_min * x)
        cur_max = max(candidates)
        cur_min = min(candidates)
        best = max(best, cur_max)
    return best


def _test() -> None:
    cases = [
        ([2, 3, -2, 4], 6),        # [2,3]
        ([-2, 0, -1], 0),          # zero resets the run
        ([-2, 3, -4], 24),         # two negatives multiply to a big positive
        ([2, -5, -2, -4, 3], 24),  # tricky sign flips
        ([-3], -3),                # single element (may be negative)
        ([0, 2], 2),               # leading zero
    ]
    for nums, expected in cases:
        assert max_product(nums) == expected, nums
        assert max_product_brute(nums) == expected, nums
    print("max_product: all cases passed")


if __name__ == "__main__":
    _test()
