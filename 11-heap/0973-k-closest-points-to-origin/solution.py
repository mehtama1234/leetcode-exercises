"""973. K Closest Points to Origin — https://leetcode.com/problems/k-closest-points-to-origin/

Given points on a plane and a number k, return the k points nearest the origin
(0, 0). Distance is straight-line (Euclidean); the answer may be in any order.

The naive version (sort all points by distance) is kept next to the optimal one
(a max-heap capped at size k) so the reason the fast version exists is visible:
we only need the k nearest, so we should not pay to fully order the far-away
points we're going to discard anyway.
"""
from typing import List
import heapq


def k_closest_sorted(points: List[List[int]], k: int) -> List[List[int]]:
    """Naive: sort every point by distance, take the first k. O(n log n).

    Straightforward and correct: compute each point's distance and sort. But
    sorting orders *all* n points top to bottom when we only need the nearest k —
    the ordering among the far points is computed and then thrown away. That extra
    ordering is the waste the capped heap removes.

    We compare *squared* distance (x*x + y*y) to skip the sqrt: it's monotonic, so
    it ranks points identically while staying in exact integer arithmetic.
    """
    return sorted(points, key=lambda p: p[0] * p[0] + p[1] * p[1])[:k]


def k_closest(points: List[List[int]], k: int) -> List[List[int]]:
    """Optimal: a max-heap of size k holding the k nearest so far. O(n log k).

    Insight: to keep the k *nearest* points, watch the *farthest* of the ones you
    are currently keeping — if a new point beats it, swap them in. That "farthest
    of the current keepers" is the top of a MAX-heap of size k.

    Python's heapq is a MIN-heap, so we store NEGATED squared distance: the
    smallest negation is the largest real distance, so heap[0] is the current
    farthest keeper. For each point:

      - push it;
      - if the heap now holds more than k, pop the farthest — it can't be among
        the k nearest.

    Each push/pop is O(log k) and the heap never exceeds k, so O(n log k) total —
    a win over O(n log n) when k is much smaller than n.
    """
    heap: List[tuple[int, List[int]]] = []    # (negated squared distance, point)
    for p in points:
        d2 = p[0] * p[0] + p[1] * p[1]
        heapq.heappush(heap, (-d2, p))
        if len(heap) > k:
            heapq.heappop(heap)               # drop the current farthest
    return [p for _, p in heap]


def _test() -> None:
    # LeetCode order is unspecified, so compare as sets of points.
    def as_set(pts: List[List[int]]) -> set:
        return {tuple(p) for p in pts}

    cases = [
        # Official examples:
        ([[1, 3], [-2, 2]], 1, [[-2, 2]]),
        ([[3, 3], [5, -1], [-2, 4]], 2, [[3, 3], [-2, 4]]),
        # Edge: k equals the number of points -> return them all.
        ([[0, 1], [1, 0]], 2, [[0, 1], [1, 0]]),
        # Edge: the origin itself is distance 0 and must be included.
        ([[0, 0], [1, 1], [2, 2]], 1, [[0, 0]]),
    ]
    for points, k, expected in cases:
        assert as_set(k_closest(points, k)) == as_set(expected), (points, k)
        assert as_set(k_closest_sorted(points, k)) == as_set(expected), (points, k)

    # Cross-check: heap and sort agree on a larger random-ish case (by distance set).
    big = [[3, 3], [5, -1], [-2, 4], [1, 3], [-2, 2], [0, 0], [7, 7], [-6, -6]]
    for k in range(1, len(big) + 1):
        got = sorted(p[0] ** 2 + p[1] ** 2 for p in k_closest(big, k))
        want = sorted(p[0] ** 2 + p[1] ** 2 for p in k_closest_sorted(big, k))
        assert got == want, k

    print("k_closest: all cases passed")


if __name__ == "__main__":
    _test()
