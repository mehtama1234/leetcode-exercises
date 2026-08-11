"""167. Two Sum II - Input Array Is Sorted — https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/

Given a 1-indexed array that is already sorted in non-decreasing order, return
the 1-based indices of the two numbers that add up to `target`.
"""
from typing import List


def two_sum_brute(numbers: List[int], target: int) -> List[int]:
    """Check every pair. O(n^2) time, O(1) space.

    The definition turned straight into code: for each i, test every later j.
    It completely ignores that the array is *sorted*, which is the one fact this
    problem hands us for free — and throwing that fact away is the waste we fix.
    """
    n = len(numbers)
    for i in range(n):
        for j in range(i + 1, n):
            if numbers[i] + numbers[j] == target:
                return [i + 1, j + 1]  # answer is 1-indexed
    return []


def two_sum(numbers: List[int], target: int) -> List[int]:
    """Two pointers from both ends. O(n) time, O(1) space.

    Key insight: because the array is sorted, the sum at the two ends tells us
    which way to move. Start with `left` at the smallest value and `right` at the
    largest.

      - If numbers[left] + numbers[right] is too big, the only way to shrink the
        sum is to move `right` left to a smaller number.
      - If it's too small, the only way to grow it is to move `left` right to a
        bigger number.
      - If it's exactly the target, we're done.

    Each step provably discards a value that cannot be part of any answer, so the
    two pointers sweep toward each other and the whole thing is one linear pass —
    no hash map and no extra memory needed.
    """
    left, right = 0, len(numbers) - 1
    while left < right:
        s = numbers[left] + numbers[right]
        if s == target:
            return [left + 1, right + 1]  # answer is 1-indexed
        if s < target:
            left += 1
        else:
            right -= 1
    return []


def _test() -> None:
    cases = [
        (([2, 7, 11, 15], 9), [1, 2]),
        (([2, 3, 4], 6), [1, 3]),
        (([-1, 0], -1), [1, 2]),
        (([1, 2, 3, 4, 4, 9, 56, 90], 8), [4, 5]),  # duplicates, answer in the middle
        (([0, 0, 3, 4], 0), [1, 2]),                # the two zeros
    ]
    for (numbers, target), expected in cases:
        assert two_sum(numbers, target) == expected, (numbers, target)
        # brute force must agree with the fast version on every case
        assert two_sum_brute(numbers, target) == expected, (numbers, target)
    print("two_sum_ii: all cases passed")


if __name__ == "__main__":
    _test()
