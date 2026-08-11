"""217. Contains Duplicate — https://leetcode.com/problems/contains-duplicate/

Given an array `nums`, return True if any value appears at least twice, and
False if every element is distinct.

Two implementations are kept side by side so the reason the fast one exists is
visible: the brute force is the honest starting point, and the set is what you
get by asking "what am I re-computing?".
"""
from typing import List


def contains_duplicate_brute(nums: List[int]) -> bool:
    """Check every pair. O(n^2) time, O(1) space.

    The definition turned straight into code: a duplicate is two positions with
    the same value, so compare every position against every later one. Correct,
    but for each element it re-scans the whole tail — that repeated scanning is
    the waste we remove next.
    """
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] == nums[j]:
                return True
    return False


def contains_duplicate(nums: List[int]) -> bool:
    """Hash set, single pass. O(n) time, O(n) space.

    Key insight: the only question at each element is "have I seen this value
    already?". A set answers that in O(1), so we never scan the tail. We check
    before inserting so the first repeat is caught the moment it arrives.
    """
    seen: set[int] = set()
    for x in nums:
        if x in seen:
            return True
        seen.add(x)
    return False


def _test() -> None:
    cases = [
        ([1, 2, 3, 1], True),
        ([1, 2, 3, 4], False),
        ([1, 1, 1, 3, 3, 4, 3, 2, 4, 2], True),
        ([], False),          # empty: nothing can repeat
        ([7], False),         # single element: nothing to pair with
    ]
    for nums, expected in cases:
        assert contains_duplicate(nums) == expected, nums
        assert contains_duplicate_brute(nums) == expected, nums
    print("contains_duplicate: all cases passed")


if __name__ == "__main__":
    _test()
