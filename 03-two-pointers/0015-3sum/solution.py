"""15. 3Sum — https://leetcode.com/problems/3sum/

Given an integer array, return all unique triplets [a, b, c] that sum to zero.
The result must not contain duplicate triplets.
"""
from typing import List


def three_sum_brute(nums: List[int]) -> List[List[int]]:
    """Check every triple, dedupe with a set. O(n^3) time.

    The definition made literal: try all three-element combinations and keep the
    ones that sum to zero. To avoid reporting the same triplet twice (the array
    can have repeats), we sort each found triplet and stash it in a set. It's
    correct but cubic — every element re-scans two nested tails. That repeated
    scanning is what the sorted two-pointer version erases.
    """
    n = len(nums)
    found: set[tuple[int, int, int]] = set()
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                if nums[i] + nums[j] + nums[k] == 0:
                    found.add(tuple(sorted((nums[i], nums[j], nums[k]))))
    return [list(t) for t in sorted(found)]


def three_sum(nums: List[int]) -> List[List[int]]:
    """Sort, then fix one number and two-pointer the rest. O(n^2) time, O(1) extra.

    Key insight: 3Sum is Two Sum done n times. Sort the array first. Then for each
    index `i`, the partners we need are two numbers in the tail that sum to `-nums[i]`
    — that is exactly Two Sum on a *sorted* array, which the converging two-pointer
    trick solves in one linear pass instead of a nested loop.

    Sorting also makes deduping easy: equal numbers sit next to each other, so we
    skip a value whenever it repeats the previous one — both for the fixed `i` and
    for the two pointers after a match. A small early exit: once `nums[i] > 0`, the
    smallest possible triplet sum is already positive, so no zero triplet remains.
    """
    nums = sorted(nums)
    n = len(nums)
    result: List[List[int]] = []

    for i in range(n):
        if nums[i] > 0:  # sorted: everything from here on is positive
            break
        if i > 0 and nums[i] == nums[i - 1]:  # skip duplicate anchors
            continue

        left, right = i + 1, n - 1
        while left < right:
            s = nums[i] + nums[left] + nums[right]
            if s < 0:
                left += 1
            elif s > 0:
                right -= 1
            else:
                result.append([nums[i], nums[left], nums[right]])
                left += 1
                right -= 1
                # skip duplicate seconds / thirds
                while left < right and nums[left] == nums[left - 1]:
                    left += 1
                while left < right and nums[right] == nums[right + 1]:
                    right -= 1
    return result


def _norm(triplets: List[List[int]]) -> List[List[int]]:
    """Sort triplets and the overall list so results compare regardless of order."""
    return sorted([sorted(t) for t in triplets])


def _test() -> None:
    cases = [
        ([-1, 0, 1, 2, -1, -4], [[-1, -1, 2], [-1, 0, 1]]),
        ([0, 1, 1], []),                 # no triplet sums to zero
        ([0, 0, 0], [[0, 0, 0]]),        # all zeros -> exactly one triplet
        ([0, 0, 0, 0], [[0, 0, 0]]),     # duplicates must not repeat the triplet
        ([-2, 0, 1, 1, 2], [[-2, 0, 2], [-2, 1, 1]]),
    ]
    for nums, expected in cases:
        got = _norm(three_sum(nums))
        assert got == _norm(expected), (nums, got)
        # brute force must agree with the fast version on every case
        assert _norm(three_sum_brute(nums)) == _norm(expected), (nums,)
    print("three_sum: all cases passed")


if __name__ == "__main__":
    _test()
