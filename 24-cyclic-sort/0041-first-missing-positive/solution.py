"""41. First Missing Positive — https://leetcode.com/problems/first-missing-positive/

Given an unsorted array `nums`, return the smallest positive integer that is NOT
present. Must run in O(n) time and use O(1) extra space (beyond the input array).

The trick that unlocks O(1) space: in an array of length n, the answer is always
in the range 1..n+1. So we can use the array's OWN indices as a hash table —
value `v` belongs at index `v-1` — and detect the first slot that isn't filled.
"""
from typing import List


def first_missing_positive_set(nums: List[int]) -> int:
    """Honest first attempt: dump the values into a set, then scan 1, 2, 3, ...

    Clear and correct, but it spends O(n) EXTRA memory on the set. That extra
    memory is exactly what the problem forbids, so it's the baseline to beat.
    """
    present = set(nums)
    candidate = 1
    while candidate in present:
        candidate += 1
    return candidate


def first_missing_positive(nums: List[int]) -> int:
    """Cyclic sort / index-as-hash. O(n) time, O(1) extra space.

    Key insight: with n slots, the first missing positive can only be one of
    1..n+1 (if all of 1..n are present, the answer is n+1; otherwise it's some
    value <= n). So values outside 1..n are irrelevant and every relevant value
    `v` has a natural home: index `v - 1`.

    Pass 1 — place each value at its home by swapping. We keep swapping the value
    currently at index `i` to where it belongs until index `i` holds something
    that either doesn't belong (out of range) or is already home. This is O(n)
    total because every swap puts at least one number in its final seat.

    Pass 2 — scan left to right. The first index `i` whose value is NOT `i + 1`
    is the gap: `i + 1` is missing. If every seat is correct, the answer is n + 1.
    """
    n = len(nums)
    for i in range(n):
        # Move nums[i] to its correct seat (index nums[i]-1) while it belongs
        # in 1..n and isn't already sitting where it should.
        while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
            correct = nums[i] - 1
            nums[i], nums[correct] = nums[correct], nums[i]
    for i in range(n):
        if nums[i] != i + 1:
            return i + 1
    return n + 1


def _test() -> None:
    cases = [
        ([1, 2, 0], 3),
        ([3, 4, -1, 1], 2),
        ([7, 8, 9, 11, 12], 1),
        ([1], 2),            # single element, all present -> n+1
        ([], 1),             # empty -> smallest positive is 1
        ([2, 2], 1),         # duplicates don't break the placement loop
        ([1, 2, 3], 4),      # fully packed -> n+1
    ]
    for nums, expected in cases:
        assert first_missing_positive_set(list(nums)) == expected, nums
        assert first_missing_positive(list(nums)) == expected, nums
    print("first_missing_positive: all cases passed")


if __name__ == "__main__":
    _test()
