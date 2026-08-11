"""435. Non-overlapping Intervals — https://leetcode.com/problems/non-overlapping-intervals/

Given a set of intervals, return the minimum number you must remove so that none
of the ones that remain overlap.

"Remove the fewest" is the same as "keep the most," which is the classic greedy
activity-selection problem: sort by end time and always keep the interval that
finishes earliest.
"""
from typing import List


def erase_overlap_intervals_brute(intervals: List[List[int]]) -> int:
    """Sort by start; on each clash, drop the one that ends later. O(n log n).

    This is the intuitive greedy: walk the sorted list keeping a "current end."
    When the next interval starts before that end, they clash and one must go — so
    keep whichever ends earlier (it leaves more room), and count the other as
    removed. Correct, but it's clearer to phrase the greedy the standard way
    below, which makes *why it's optimal* obvious.
    """
    if not intervals:
        return 0
    ordered = sorted(intervals, key=lambda iv: iv[0])
    removed = 0
    prev_end = ordered[0][1]
    for start, end in ordered[1:]:
        if start < prev_end:            # overlap — must delete one
            removed += 1
            prev_end = min(prev_end, end)   # keep the earlier-ending one
        else:
            prev_end = end
    return removed


def erase_overlap_intervals(intervals: List[List[int]]) -> int:
    """Greedy: sort by END, keep each interval that doesn't clash. O(n log n).

    The problem "remove the fewest to make them disjoint" is exactly "keep the
    most non-overlapping intervals" — the removals are just everything you didn't
    keep. That's the interval-scheduling / activity-selection problem.

    Why sort by end? When you're choosing which intervals to keep, the one that
    *finishes earliest* is always safe to take: it uses up the least of the
    timeline, leaving the most room for the rest. Any optimal solution can swap in
    the earliest-finishing interval without losing anything (an exchange
    argument), so the greedy is provably optimal.

    Walk the intervals by end time, tracking the end of the last one we kept. If
    the next interval starts at or after that end, it fits — keep it and move the
    boundary. If it starts earlier, it clashes with something we already kept, so
    it's a removal.
    """
    if not intervals:
        return 0

    ordered = sorted(intervals, key=lambda iv: iv[1])
    kept_end = ordered[0][1]
    kept = 1                            # we always keep the first (earliest end)

    for start, end in ordered[1:]:
        if start >= kept_end:           # fits after the last kept one
            kept += 1
            kept_end = end
        # else: overlaps a kept interval -> it will be removed

    return len(intervals) - kept


def _test() -> None:
    cases = [
        ([[1, 2], [2, 3], [3, 4], [1, 3]], 1),
        ([[1, 2], [1, 2], [1, 2]], 2),
        ([[1, 2], [2, 3]], 0),                 # touching, not overlapping
        ([], 0),
        ([[1, 100], [11, 22], [1, 11], [2, 12]], 2),
        ([[1, 2]], 0),                          # single interval
    ]
    for intervals, expected in cases:
        assert erase_overlap_intervals(intervals) == expected, intervals
        # the two greedies must agree
        assert erase_overlap_intervals_brute([iv[:] for iv in intervals]) == expected, intervals
    print("non_overlapping_intervals: all cases passed")


if __name__ == "__main__":
    _test()
