"""1046. Last Stone Weight — https://leetcode.com/problems/last-stone-weight/

Repeatedly smash the two heaviest stones together; if they differ, the leftover
weight goes back in. Return the weight of the last stone, or 0 if none remain.

The naive version (re-sort every round to find the two heaviest) is kept next to
the optimal one (a max-heap) so the reason the fast version exists is visible:
each round only needs the two largest values, so we should keep those cheap to
reach instead of re-sorting the whole pile.
"""
from typing import List
import heapq


def last_stone_weight_sorted(stones: List[int]) -> int:
    """Naive: re-sort the pile every round to grab the two heaviest. O(n^2 log n).

    Each round we sort (O(n log n)) just to read the top two, smash them, and push
    any leftover back. There are up to O(n) rounds, so the whole thing is
    O(n^2 log n). We re-establish full order every round even though only the two
    largest values matter — that repeated sorting is the waste.
    """
    stones = list(stones)                     # copy; don't mutate the caller's list
    while len(stones) > 1:
        stones.sort()                         # ascending; two heaviest at the end
        y = stones.pop()                      # heaviest
        x = stones.pop()                      # second heaviest
        if y != x:
            stones.append(y - x)              # leftover from the smash
    return stones[0] if stones else 0


def last_stone_weight(stones: List[int]) -> int:
    """Optimal: a max-heap so the two heaviest are always on top. O(n log n).

    Insight: each round we only need the two largest stones. A heap gives the
    largest in O(1) and removes it in O(log n), so we never re-sort. Python's
    heapq is a MIN-heap, so we store NEGATED weights: the smallest negation is the
    heaviest real stone.

    Each round pops the two heaviest; if they differ, push the (negated) leftover.
    n rounds at O(log n) each -> O(n log n) overall.
    """
    heap = [-w for w in stones]               # negate to fake a max-heap
    heapq.heapify(heap)                        # O(n)
    while len(heap) > 1:
        y = -heapq.heappop(heap)              # heaviest (undo negation)
        x = -heapq.heappop(heap)              # second heaviest
        if y != x:
            heapq.heappush(heap, -(y - x))    # push leftover, negated
    return -heap[0] if heap else 0


def _test() -> None:
    # Official LeetCode example: [2,7,4,1,8,1] -> 1
    #   smash 8,7 -> 1 back; pile [2,4,1,1,1]; smash 4,2 -> 2; [2,1,1,1];
    #   smash 2,1 -> 1; [1,1,1]; smash 1,1 -> nothing; [1] -> answer 1.
    cases = [
        ([2, 7, 4, 1, 8, 1], 1),
        ([1], 1),                              # single stone survives untouched
        ([2, 2], 0),                           # equal pair annihilates -> none left
        ([], 0),                               # no stones
        ([3, 7, 2], 2),                        # 7,3 -> 4; then 4,2 -> 2
        ([10, 4, 4, 4], 2),                    # 10,4 ->6; 6,4 ->2; 4,2 ->2
    ]
    for stones, expected in cases:
        assert last_stone_weight(stones) == expected, stones
        # naive must agree with the heap version on every case
        assert last_stone_weight_sorted(stones) == expected, stones
    print("last_stone_weight: all cases passed")


if __name__ == "__main__":
    _test()
