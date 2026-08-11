"""268. Missing Number — https://leetcode.com/problems/missing-number/

You're given an array containing `n` distinct numbers taken from the range
`0..n` (that's n+1 possible values). Exactly one value in that range is missing.
Return it.

Two implementations: the sum formula (the clean arithmetic idea) and XOR (the
bit trick that needs no addition and can't overflow).
"""
from typing import List


def missing_number_sum(nums: List[int]) -> int:
    """Compare the ideal sum to the actual sum. O(n) time, O(1) space.

    The numbers 0..n add up to a known total, n*(n+1)/2. If one value is missing,
    the actual sum falls short by exactly that value. So:

        missing = expected_sum - actual_sum

    Simple and correct; the only worry (in fixed-width languages) is that the
    sums can overflow. Python integers don't overflow, but XOR sidesteps it
    entirely.
    """
    n = len(nums)
    expected = n * (n + 1) // 2
    return expected - sum(nums)


def missing_number(nums: List[int]) -> int:
    """XOR every index and every value together. O(n) time, O(1) space.

    Two facts about XOR make this work:
      - x ^ x == 0  (a value cancels itself)
      - x ^ 0 == x  (0 is the identity)

    XOR is also order-independent. So if we XOR together all the indices 0..n AND
    all the values in the array, every number that appears in *both* lists cancels
    to 0, and only the missing one — which appears as an index but not as a value
    — survives.

    Example nums = [3, 0, 1] (n = 3, missing 2). Fold in i then nums[i]:

        acc = 3                       (start with n = 3)
        i=0: acc ^= 0 ^ 3 = 3^0^3 = 0
        i=1: acc ^= 1 ^ 0 = 0^1^0 = 1
        i=2: acc ^= 2 ^ 1 = 1^2^1 = 2   <- the missing value

    We seed `acc` with n because indices only run 0..n-1, but the value range is
    0..n, so n itself is a value we must fold in from somewhere.
    """
    acc = len(nums)  # this is n; folds in the top of the value range
    for i, x in enumerate(nums):
        acc ^= i ^ x
    return acc


def _test() -> None:
    cases = [
        ([3, 0, 1], 2),
        ([0, 1], 2),
        ([9, 6, 4, 2, 3, 5, 7, 0, 1], 8),
        ([0], 1),   # single element, top of range missing
        ([1], 0),   # single element, bottom of range missing
    ]
    for nums, expected in cases:
        assert missing_number(nums) == expected, nums
        assert missing_number_sum(nums) == expected, nums
    print("missing_number: all cases passed")


if __name__ == "__main__":
    _test()
