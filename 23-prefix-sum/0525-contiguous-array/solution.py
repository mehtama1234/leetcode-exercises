"""525. Contiguous Array — https://leetcode.com/problems/contiguous-array/

Given a binary array of 0s and 1s, find the length of the longest contiguous
subarray with an equal number of 0s and 1s. A relabel turns this into a prefix-sum
problem solved in one pass.
"""
from typing import List


def find_max_length_brute(nums: List[int]) -> int:
    """Try every subarray, count 0s and 1s. O(n^2) time, O(1) space.

    Honest and correct: for each start, extend the end and track the running
    balance (0 -> -1, 1 -> +1); whenever balance is 0 the subarray is equal. But
    every start re-walks the tail — that repetition is the waste.
    """
    n = len(nums)
    best = 0
    for start in range(n):
        balance = 0
        for end in range(start, n):
            balance += 1 if nums[end] == 1 else -1
            if balance == 0:
                best = max(best, end - start + 1)
    return best


def find_max_length(nums: List[int]) -> int:
    """Relabel + prefix sum + hash map, single pass. O(n) time, O(n) space.

    Key insight: replace each 0 with -1. Now "equal 0s and 1s" means "the run sums
    to 0". A run (i..j) sums to 0 exactly when prefix[i] == prefix[j+1] — the two
    prefix sums are equal. So the longest equal run ending at j is j minus the
    *first* index where that same prefix value appeared. Store, for each prefix
    sum, the earliest index it occurred; the earlier it first appeared, the longer
    the balanced stretch.
    """
    best = 0
    balance = 0
    # prefix sum -> earliest index (as a running total *before* that index).
    # Seed {0: -1}: a prefix of 0 is "true before index 0" so runs from the very
    # start are measured correctly.
    first_seen: dict[int, int] = {0: -1}
    for i, x in enumerate(nums):
        balance += 1 if x == 1 else -1
        if balance in first_seen:
            best = max(best, i - first_seen[balance])
        else:
            first_seen[balance] = i  # only record the earliest occurrence
    return best


def _test() -> None:
    # Official LeetCode examples.
    assert find_max_length([0, 1]) == 2
    assert find_max_length([0, 1, 0]) == 2

    # Longer / trickier cases.
    assert find_max_length([0, 1, 0, 1]) == 4
    assert find_max_length([0, 0, 1, 0, 0, 0, 1, 1]) == 6
    assert find_max_length([1, 1, 1, 1]) == 0  # never balances

    # Edge: single element and empty array.
    assert find_max_length([0]) == 0
    assert find_max_length([]) == 0

    # Brute force must agree everywhere.
    for nums in [[0, 1], [0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0, 0, 0, 1, 1], [1, 1, 0]]:
        assert find_max_length(nums) == find_max_length_brute(nums), nums

    print("contiguous_array: all cases passed")


if __name__ == "__main__":
    _test()
