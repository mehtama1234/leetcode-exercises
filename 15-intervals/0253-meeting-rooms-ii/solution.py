"""253. Meeting Rooms II — https://leetcode.com/problems/meeting-rooms-ii/  (premium)

Given meeting time intervals `[start, end]`, return the minimum number of
conference rooms needed so that no two overlapping meetings share a room.

The answer is the largest number of meetings happening at the same instant. Two
clean ways to get it: a min-heap of end times, or a sweep over split start/end
events.

Standard signature: min_meeting_rooms(intervals) -> int.
"""
from typing import List
import heapq


def min_meeting_rooms_heap(intervals: List[List[int]]) -> int:
    """Sort by start; a min-heap holds the end times of in-use rooms. O(n log n).

    Process meetings in start order. The heap holds the end times of rooms that
    are currently busy. For each meeting:
      - if the earliest-freeing room (heap top) is done by the time this meeting
        starts, reuse it: pop the old end, push this meeting's end;
      - otherwise every room is busy, so open a new one: push this end.
    The number of rooms is the largest the heap ever grows to. We keep the heap
    small by reusing whenever possible, so its size at the end is the peak
    concurrency — exactly the rooms needed.
    """
    if not intervals:
        return 0

    ordered = sorted(intervals, key=lambda iv: iv[0])
    ends: List[int] = []                 # min-heap of end times of busy rooms

    for start, end in ordered:
        if ends and ends[0] <= start:    # earliest room is free by now — reuse it
            heapq.heapreplace(ends, end)
        else:                            # need a new room
            heapq.heappush(ends, end)

    return len(ends)


def min_meeting_rooms(intervals: List[List[int]]) -> int:
    """Sweep line: split into +1 start events and -1 end events. O(n log n).

    Forget which room is which — just count how many meetings are live at once.
    Turn each meeting into two events on the timeline: a start (+1 room) and an
    end (-1 room). Sort all events by time; on a tie, process ends before starts
    so a meeting ending at time t frees its room for one starting at t (they don't
    truly overlap). Sweep, tracking the running count, and the peak of that count
    is the number of rooms.
    """
    starts = sorted(iv[0] for iv in intervals)
    ends = sorted(iv[1] for iv in intervals)

    rooms = 0
    peak = 0
    i = j = 0
    n = len(intervals)
    while i < n:
        if starts[i] < ends[j]:          # a meeting begins before the next frees
            rooms += 1
            peak = max(peak, rooms)
            i += 1
        else:                            # a meeting ends first — free a room
            rooms -= 1
            j += 1
    return peak


def _test() -> None:
    cases = [
        ([[0, 30], [5, 10], [15, 20]], 2),
        ([[7, 10], [2, 4]], 1),                 # disjoint
        ([], 0),
        ([[1, 5]], 1),                          # single meeting
        ([[1, 5], [5, 10]], 1),                 # back-to-back reuse one room
        ([[1, 10], [2, 7], [3, 19], [8, 12], [10, 20], [11, 30]], 4),
        ([[2, 15], [36, 45], [9, 29], [16, 23], [4, 9]], 2),
    ]
    for intervals, expected in cases:
        assert min_meeting_rooms(intervals) == expected, intervals
        # the heap version must agree with the sweep-line version
        assert min_meeting_rooms_heap([iv[:] for iv in intervals]) == expected, intervals
    print("meeting_rooms_ii: all cases passed")


if __name__ == "__main__":
    _test()
