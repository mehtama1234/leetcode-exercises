"""238. Product of Array Except Self — https://leetcode.com/problems/product-of-array-except-self/

Given an array `nums`, return an array `answer` where `answer[i]` is the product
of every element except `nums[i]`. No division allowed; do it in O(n).

Two implementations: the naive re-multiply-everything, and the prefix/suffix
pass that computes each answer from products already accumulated.
"""
from typing import List


def product_except_self_brute(nums: List[int]) -> List[int]:
    """For each i, multiply all the others. O(n^2) time.

    Straight from the definition: answer[i] is the product of the rest, so for
    each i loop over the array skipping i. Correct, but every position re-multiplies
    almost the whole array — that overlap is exactly what we remove.
    """
    n = len(nums)
    answer = [1] * n
    for i in range(n):
        for j in range(n):
            if j != i:
                answer[i] *= nums[j]
    return answer


def product_except_self(nums: List[int]) -> List[int]:
    """Prefix products left, then suffix products right. O(n) time, O(1) extra.

    Key insight: the product of everything except i splits cleanly into two
    pieces — the product of all elements to the LEFT of i, times the product of
    all to the RIGHT. Neither piece includes nums[i]. Sweep left to right filling
    answer[i] with the running left product, then sweep right to left multiplying
    in the running right product. Two passes, no division, and the output array
    doubles as scratch so we use only O(1) beyond it.
    """
    n = len(nums)
    answer = [1] * n

    prefix = 1  # product of everything strictly left of the current index
    for i in range(n):
        answer[i] = prefix
        prefix *= nums[i]

    suffix = 1  # product of everything strictly right of the current index
    for i in range(n - 1, -1, -1):
        answer[i] *= suffix
        suffix *= nums[i]

    return answer


def _test() -> None:
    cases = [
        ([1, 2, 3, 4], [24, 12, 8, 6]),
        ([-1, 1, 0, -3, 3], [0, 0, 9, 0, 0]),   # a single zero
        ([2, 3], [3, 2]),                        # two elements
        ([5, 0, 0], [0, 0, 0]),                  # two zeros → all zero
        ([-2, -3, -4], [12, 8, 6]),              # negatives
    ]
    for nums, expected in cases:
        assert product_except_self(nums) == expected, nums
        assert product_except_self_brute(nums) == expected, nums
    print("product_except_self: all cases passed")


if __name__ == "__main__":
    _test()
