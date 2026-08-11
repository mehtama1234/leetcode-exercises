"""128. Longest Consecutive Sequence — https://leetcode.com/problems/longest-consecutive-sequence/

Given an unsorted array `nums`, return the length of the longest run of
consecutive integers (like 1,2,3,4) that can be formed from its values. Must run
in O(n) time.

Two implementations: the obvious sort-then-count, and an O(n) set-based scan that
only starts counting from the true beginning of each run.
"""
from typing import List


def longest_consecutive_sort(nums: List[int]) -> int:
    """Sort, then scan for the longest ascending run of +1 steps. O(n log n).

    Once sorted, consecutive integers sit next to each other, so a single walk
    counts run lengths. Correct and intuitive, but the sort violates the required
    O(n) bound — it's here only to contrast with the fast version.
    """
    if not nums:
        return 0
    ordered = sorted(set(nums))  # dedupe so repeats don't break the run count
    best = 1
    current = 1
    for i in range(1, len(ordered)):
        if ordered[i] == ordered[i - 1] + 1:
            current += 1
            best = max(best, current)
        else:
            current = 1
    return best


def longest_consecutive(nums: List[int]) -> int:
    """Hash set, count each run once from its start. O(n) time, O(n) space.

    Key insight: with all values in a set, membership is O(1), so we can ask "is
    x+1 present?" instantly and walk a run forward without sorting. The trick that
    keeps it O(n) overall is: only *start* counting a run at its true beginning —
    a value x is a start exactly when x-1 is NOT in the set. Every run is then
    walked forward exactly once, so total work is proportional to the number of
    elements, not to how many runs overlap.
    """
    present = set(nums)
    best = 0
    for x in present:
        if x - 1 in present:
            continue  # x is inside a run, not its start — skip it
        length = 1
        y = x
        while y + 1 in present:
            y += 1
            length += 1
        best = max(best, length)
    return best


def _test() -> None:
    cases = [
        ([100, 4, 200, 1, 3, 2], 4),          # 1,2,3,4
        ([0, 3, 7, 2, 5, 8, 4, 6, 0, 1], 9),  # 0..8, with a duplicate 0
        ([], 0),                              # empty array
        ([5], 1),                             # single element
        ([1, 2, 0, 1], 3),                    # duplicates don't inflate the run
        ([9, 1, 4, 7, 3, -1, 0, 5, 8, -1, 6], 7),  # -1,0,1 ... plus 3..9 run of 7
    ]
    for nums, expected in cases:
        assert longest_consecutive(nums) == expected, nums
        assert longest_consecutive_sort(nums) == expected, nums
    print("longest_consecutive: all cases passed")


if __name__ == "__main__":
    _test()
