"""56. Merge Intervals — https://leetcode.com/problems/merge-intervals/

Given a list of intervals `[start, end]`, merge every group that overlaps into a
single interval, and return the merged list.

The only real move is: overlap becomes obvious once the intervals are sorted by
start, so a single sweep can decide "extend the last one" vs "start a new one".
"""
from typing import List


def merge(intervals: List[List[int]]) -> List[List[int]]:
    """Sort by start, then sweep once. O(n log n) time, O(n) space.

    Why sorting is the whole trick: two intervals overlap when one starts before
    the other ends. If we sort by start, then when we walk left to right the only
    thing that can overlap the interval we're currently building is the *next*
    one — anything earlier already started earlier and was handled. So we never
    have to compare far-apart intervals.

    For each interval in sorted order:
      - if its start is <= the end of the interval we're building, they touch or
        overlap, so absorb it by pushing our end out to max(end, its end);
      - otherwise there's a gap, so the current one is finished — emit it and
        begin a new one from here.

    We take max(end, ...) rather than just its end because a later interval can be
    fully swallowed, e.g. [1, 10] then [2, 3]: the end must stay 10.
    """
    if not intervals:
        return []

    ordered = sorted(intervals, key=lambda iv: iv[0])
    merged: List[List[int]] = [ordered[0][:]]  # copy so we don't mutate the input

    for start, end in ordered[1:]:
        last = merged[-1]
        if start <= last[1]:          # overlap or touch
            last[1] = max(last[1], end)
        else:                         # gap — the previous run is done
            merged.append([start, end])

    return merged


def _test() -> None:
    cases = [
        ([[1, 3], [2, 6], [8, 10], [15, 18]], [[1, 6], [8, 10], [15, 18]]),
        ([[1, 4], [4, 5]], [[1, 5]]),                 # touching endpoints merge
        ([[1, 4]], [[1, 4]]),                         # single interval
        ([[1, 10], [2, 3], [4, 5]], [[1, 10]]),       # fully swallowed insiders
        ([[1, 4], [0, 4]], [[0, 4]]),                 # unsorted input, same span
        ([[1, 4], [2, 3]], [[1, 4]]),                 # nested
    ]
    for intervals, expected in cases:
        assert merge(intervals) == expected, intervals
    # input must not be mutated
    original = [[1, 3], [2, 6]]
    merge(original)
    assert original == [[1, 3], [2, 6]]
    print("merge_intervals: all cases passed")


if __name__ == "__main__":
    _test()
