"""57. Insert Interval — https://leetcode.com/problems/insert-interval/

You're given a list of non-overlapping intervals sorted by start, plus one new
interval. Insert the new one and return the list still merged and sorted.

Because the existing list is already sorted and disjoint, we can do it in one
linear pass with no re-sorting: skip what's before, absorb what overlaps, then
copy the rest.
"""
from typing import List


def insert(intervals: List[List[int]], new_interval: List[int]) -> List[List[int]]:
    """One linear pass in three phases. O(n) time, O(n) space.

    The input is already sorted and non-overlapping, which is the gift: we don't
    need to sort, and we can split the existing intervals into three clean groups
    relative to the new one:

      1. Intervals that end *before* the new one starts (iv_end < new_start).
         They can't touch it — copy them straight through.
      2. Intervals that overlap the new one (iv_start <= new_end and
         iv_end >= new_start). Merge them all into the new interval by widening
         it: start = min(starts), end = max(ends).
      3. Intervals that start *after* the merged interval ends — copy the rest
         straight through.

    Walking left to right, we hit those three groups in exactly that order, so a
    single pass with three small loops does it.
    """
    result: List[List[int]] = []
    start, end = new_interval[0], new_interval[1]
    i, n = 0, len(intervals)

    # Phase 1: everything strictly before the new interval.
    while i < n and intervals[i][1] < start:
        result.append(intervals[i])
        i += 1

    # Phase 2: everything that overlaps — grow the new interval to cover them all.
    while i < n and intervals[i][0] <= end:
        start = min(start, intervals[i][0])
        end = max(end, intervals[i][1])
        i += 1
    result.append([start, end])

    # Phase 3: everything strictly after.
    while i < n:
        result.append(intervals[i])
        i += 1

    return result


def _test() -> None:
    cases = [
        ([[1, 3], [6, 9]], [2, 5], [[1, 5], [6, 9]]),
        ([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8],
         [[1, 2], [3, 10], [12, 16]]),
        ([], [5, 7], [[5, 7]]),                        # empty list
        ([[1, 5]], [2, 3], [[1, 5]]),                  # new is swallowed
        ([[1, 5]], [6, 8], [[1, 5], [6, 8]]),          # goes after everything
        ([[3, 5]], [1, 2], [[1, 2], [3, 5]]),          # goes before everything
        ([[1, 3], [4, 6]], [3, 4], [[1, 6]]),          # touching endpoints merge
    ]
    for intervals, new_interval, expected in cases:
        assert insert(intervals, new_interval) == expected, (intervals, new_interval)
    print("insert_interval: all cases passed")


if __name__ == "__main__":
    _test()
