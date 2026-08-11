"""703. Kth Largest Element in a Stream — https://leetcode.com/problems/kth-largest-element-in-a-stream/

Design a class that, given a fixed `k`, accepts numbers one at a time and after
every add reports the kth largest value among everything seen so far.

The naive class (re-sort the whole history each add) is kept next to the optimal
one (a min-heap capped at size k) so the reason the fast version exists is
visible: to know the kth largest you only ever need to remember the k biggest
numbers, not the entire stream.
"""
from typing import List
import heapq


class KthLargestSorted:
    """Naive: keep every number, re-sort on demand. O(n log n) per query.

    `add` just appends (O(1)), but `add` must also return the answer, so we sort
    the whole history and index to the kth largest. Sorting n numbers is
    O(n log n), repeated on every add — and we throw away almost all of that
    order, since only the top k ever matter. That waste is what the capped heap
    below removes.
    """

    def __init__(self, k: int, nums: List[int]) -> None:
        self._k = k
        self._nums = list(nums)

    def add(self, val: int) -> int:
        self._nums.append(val)
        # sorted descending; the kth largest sits at index k-1
        return sorted(self._nums, reverse=True)[self._k - 1]


class KthLargest:
    """Optimal: a min-heap holding only the k largest values. O(log k) per add.

    Insight: the kth largest number is the *smallest* of the top k numbers. So we
    never need the whole stream — just the k biggest so far, and specifically the
    smallest among them, which is the answer.

    Keep those k values in a MIN-heap of fixed size k. Its top (`heap[0]`) is the
    smallest of the k, i.e. the kth largest overall. On each add:

      - push the new number;
      - if the heap now holds more than k, pop the smallest — it can't be in the
        top k, so discard it.

    The top is then the current answer, read in O(1). Each add is O(log k), not
    O(n log n), because the heap never grows past k.
    """

    def __init__(self, k: int, nums: List[int]) -> None:
        self._k = k
        self._heap: List[int] = list(nums)
        heapq.heapify(self._heap)                 # O(n) once
        while len(self._heap) > k:
            heapq.heappop(self._heap)             # trim down to the k largest

    def add(self, val: int) -> int:
        heapq.heappush(self._heap, val)
        if len(self._heap) > self._k:
            heapq.heappop(self._heap)             # drop the smallest, keep top k
        return self._heap[0]                       # smallest of top k = kth largest


def _test() -> None:
    # Official LeetCode example: k = 3, stream starts [4, 5, 8, 2]
    #   add(3) -> 4, add(5) -> 5, add(10) -> 5, add(9) -> 8, add(4) -> 8
    for cls in (KthLargest, KthLargestSorted):
        kth = cls(3, [4, 5, 8, 2])
        assert kth.add(3) == 4, cls.__name__
        assert kth.add(5) == 5, cls.__name__
        assert kth.add(10) == 5, cls.__name__
        assert kth.add(9) == 8, cls.__name__
        assert kth.add(4) == 8, cls.__name__

        # Edge: fewer than k numbers to start; the kth exists only after adds.
        empty = cls(1, [])
        assert empty.add(-1) == -1, cls.__name__   # k=1 -> the maximum so far
        assert empty.add(-2) == -1, cls.__name__
        assert empty.add(0) == 0, cls.__name__

        # Edge: duplicates count as distinct positions.
        dup = cls(2, [5, 5])
        assert dup.add(5) == 5, cls.__name__       # top two are both 5
        assert dup.add(6) == 5, cls.__name__       # top two now 6, 5

    print("kth_largest_stream: all cases passed")


if __name__ == "__main__":
    _test()
