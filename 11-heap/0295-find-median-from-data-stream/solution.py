"""295. Find Median from Data Stream — https://leetcode.com/problems/find-median-from-data-stream/

Design a structure that accepts numbers one at a time and can report the median
of everything seen so far at any moment. The median is the middle value of the
sorted numbers (the average of the two middles when the count is even).

The naive class (keep a sorted list) is kept next to the optimal one (two heaps)
so the reason the fast version exists is visible: the median only ever needs the
one or two values sitting at the *middle*, so we should not pay to keep the whole
stream sorted — only to keep those middle values reachable.
"""
from typing import List
import heapq


class MedianFinderSorted:
    """Naive: keep a fully sorted list, insert in order.

    `addNum` finds the insertion point with binary search (O(log n)) but then
    shifts every element after it to make room — that shift is O(n). `findMedian`
    is then trivially O(1) by index. The whole stream stays sorted at all times,
    which is far more order than the median actually needs, and the per-insert
    shift is the waste we remove in the two-heap version below.
    """

    def __init__(self) -> None:
        self._nums: List[int] = []

    def addNum(self, num: int) -> None:
        # bisect.insort would do this in one call; written out to show the O(n) shift.
        lo, hi = 0, len(self._nums)
        while lo < hi:
            mid = (lo + hi) // 2
            if self._nums[mid] < num:
                lo = mid + 1
            else:
                hi = mid
        self._nums.insert(lo, num)  # O(n): shifts the tail right

    def findMedian(self) -> float:
        n = len(self._nums)
        mid = n // 2
        if n % 2 == 1:
            return float(self._nums[mid])
        return (self._nums[mid - 1] + self._nums[mid]) / 2


class MedianFinder:
    """Optimal: two heaps that split the stream at the middle. O(log n) per add.

    Insight: to report the median we never need the whole sorted order — we only
    need the value(s) at the center. So split the numbers into two halves:

      - `low`  — the smaller half, kept as a MAX-heap so its *largest* value
                 (the top of the lower half) is always reachable in O(1).
      - `high` — the larger half, kept as a MIN-heap so its *smallest* value
                 (the top of the upper half) is always reachable in O(1).

    Python's heapq is a MIN-heap only, so we simulate the max-heap `low` by
    storing negated numbers: the smallest negation is the largest real value.

    We keep two invariants after every add:
      1. Every value in `low` <= every value in `high` (the split is at the median).
      2. The sizes differ by at most 1, and when they differ `low` holds the extra.

    Then the median is either `low`'s top (odd count) or the average of the two
    tops (even count) — both O(1). Each add is O(log n): one push, and at most a
    couple of pushes/pops to rebalance.
    """

    def __init__(self) -> None:
        self._low: List[int] = []   # max-heap via negation: smaller half
        self._high: List[int] = []  # min-heap: larger half

    def addNum(self, num: int) -> None:
        # Step 1: tentatively add to `low` (max-heap). Push num, then move its
        # largest across to `high`. This guarantees invariant 1: whatever lands in
        # `high` is >= everything left in `low`.
        heapq.heappush(self._low, -num)
        heapq.heappush(self._high, -heapq.heappop(self._low))

        # Step 2: rebalance sizes so `low` is equal to or one larger than `high`.
        # After step 1 `high` may have grown one too big; hand its smallest back.
        if len(self._high) > len(self._low):
            heapq.heappush(self._low, -heapq.heappop(self._high))

    def findMedian(self) -> float:
        # `low` is never smaller than `high`, so it holds the middle when the
        # count is odd, and shares the two middles with `high` when it's even.
        if len(self._low) > len(self._high):
            return float(-self._low[0])
        return (-self._low[0] + self._high[0]) / 2


def _test() -> None:
    # Official LeetCode example:
    #   addNum(1); addNum(2); findMedian() -> 1.5; addNum(3); findMedian() -> 2.0
    for cls in (MedianFinder, MedianFinderSorted):
        mf = cls()
        mf.addNum(1)
        mf.addNum(2)
        assert mf.findMedian() == 1.5, cls.__name__
        mf.addNum(3)
        assert mf.findMedian() == 2.0, cls.__name__

        # Edge: a single number is its own median.
        single = cls()
        single.addNum(5)
        assert single.findMedian() == 5.0, cls.__name__

        # Edge: negatives, duplicates, and an even count crossing zero.
        mixed = cls()
        for x in [-3, -3, 4, 4]:
            mixed.addNum(x)
        assert mixed.findMedian() == 0.5, cls.__name__  # middles are -3 and 4

        # Longer run checked against a brute recompute of the median each step.
        import statistics
        brute: List[int] = []
        streamed = cls()
        for x in [6, -1, 10, 10, -5, 3, 0, 8, 8, -2]:
            brute.append(x)
            streamed.addNum(x)
            assert streamed.findMedian() == statistics.median(brute), (cls.__name__, x)

    print("median_finder: all cases passed")


if __name__ == "__main__":
    _test()
