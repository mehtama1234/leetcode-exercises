"""252. Meeting Rooms — https://leetcode.com/problems/meeting-rooms/  (premium)

Given meeting time intervals `[start, end]`, decide whether a single person could
attend all of them — i.e. whether any two meetings overlap.

Standard signature: can_attend_all(intervals) -> bool.
"""
from typing import List


def can_attend_all(intervals: List[List[int]]) -> bool:
    """Sort by start, then check only adjacent pairs. O(n log n) time, O(1) space.

    You can attend everything iff no two meetings overlap. Checking all pairs is
    O(n^2), but sorting by start removes the waste: after sorting, if *any* two
    meetings overlap, then two *adjacent* meetings overlap. Reason: the meeting
    that overlaps you and starts earliest is the immediate next one, since starts
    only increase. So we just need each meeting to end no later than the next
    one's start.

    A conflict is `next_start < current_end`. Equality (one ends exactly when the
    next begins) is fine — that's back-to-back, not an overlap.
    """
    ordered = sorted(intervals, key=lambda iv: iv[0])
    for i in range(1, len(ordered)):
        if ordered[i][0] < ordered[i - 1][1]:   # this one starts before the last ends
            return False
    return True


def _test() -> None:
    cases = [
        ([[0, 30], [5, 10], [15, 20]], False),   # [0,30] clashes with both
        ([[7, 10], [2, 4]], True),               # disjoint (unsorted input)
        ([], True),                              # nothing to attend
        ([[1, 5]], True),                        # one meeting
        ([[1, 5], [5, 10]], True),               # back-to-back, no overlap
        ([[1, 5], [4, 10]], False),              # 1-unit overlap
    ]
    for intervals, expected in cases:
        assert can_attend_all(intervals) == expected, intervals
    print("meeting_rooms: all cases passed")


if __name__ == "__main__":
    _test()
