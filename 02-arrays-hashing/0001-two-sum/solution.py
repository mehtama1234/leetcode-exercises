"""1. Two Sum — https://leetcode.com/problems/two-sum/

Given an array `nums` and a target, return the indices of the two numbers that
add up to the target. Exactly one solution exists; you may not reuse an element.

Two implementations are kept side by side so the *reason* the fast one exists is
visible: the brute force is the honest starting point, and the hash map is what
you get by asking "what am I re-computing?".
"""
from typing import List


def two_sum_brute(nums: List[int], target: int) -> List[int]:
    """Check every pair. O(n^2) time, O(1) space.

    This is the definition of the problem turned directly into code: for each i,
    look at every later j and test the pair. It works, but for each element it
    re-scans the whole tail — that repeated scanning is the waste we remove next.
    """
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []


def two_sum(nums: List[int], target: int) -> List[int]:
    """Hash map, single pass. O(n) time, O(n) space.

    Key insight: for the current number x, its partner is fully determined —
    it must be `target - x`. So the only question is "have I already seen that
    partner?". A dict from value -> index answers that in O(1), so we never scan
    the tail at all. We check before inserting, which also handles duplicates
    (e.g. target = x + x) correctly without matching an element with itself.
    """
    seen: dict[int, int] = {}  # value -> index we saw it at
    for i, x in enumerate(nums):
        need = target - x
        if need in seen:
            return [seen[need], i]
        seen[x] = i
    return []


def _test() -> None:
    cases = [
        (([2, 7, 11, 15], 9), [0, 1]),
        (([3, 2, 4], 6), [1, 2]),
        (([3, 3], 6), [0, 1]),
        (([-1, -2, -3, -4, -5], -8), [2, 4]),
    ]
    for (nums, target), expected in cases:
        assert two_sum(nums, target) == expected, (nums, target)
        # brute force must agree with the fast version on every case
        assert two_sum_brute(nums, target) == expected, (nums, target)
    print("two_sum: all cases passed")


if __name__ == "__main__":
    _test()
