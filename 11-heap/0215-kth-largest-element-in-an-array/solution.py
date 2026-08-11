"""215. Kth Largest Element in an Array — https://leetcode.com/problems/kth-largest-element-in-an-array/

Given an array and a number k, return the kth largest value in sorted order (the
kth largest, counting duplicates — not the kth distinct value).

Three approaches are kept side by side so the trade-offs are visible: sort the
whole thing (simple), a min-heap capped at size k (streaming-friendly, O(n log k)),
and Quickselect (O(n) average, no full sort). Squared distances aren't needed
here; we compare the raw numbers.
"""
from typing import List
import heapq
import random


def find_kth_largest_sorted(nums: List[int], k: int) -> int:
    """Naive: sort descending, index to the kth largest. O(n log n).

    Correct and one line. But it fully orders all n numbers when we only need the
    single value at rank k — every comparison spent ordering the other n-1 numbers
    among themselves is work the answer never reads. The two versions below buy
    that back.
    """
    return sorted(nums, reverse=True)[k - 1]


def find_kth_largest(nums: List[int], k: int) -> int:
    """Min-heap capped at size k: hold the k largest, answer is their smallest.

    Insight: the kth largest is the *smallest* of the top k numbers. Keep those k
    in a MIN-heap (smallest on top). Push each number; whenever the heap exceeds k,
    pop its smallest — that number is now outside the top k. When the pass ends,
    heap[0] is the smallest of the k largest = the kth largest.

    O(n log k) time, O(k) space. This is the version to reach for when k is much
    smaller than n, or when numbers arrive as a stream you can't hold all at once.
    """
    heap: List[int] = []
    for x in nums:
        heapq.heappush(heap, x)
        if len(heap) > k:
            heapq.heappop(heap)               # evict the current smallest keeper
    return heap[0]                             # smallest of the top k


def find_kth_largest_quickselect(nums: List[int], k: int) -> int:
    """Quickselect: partition toward the answer's position. O(n) average.

    The kth largest sits at index `k-1` when the array is sorted *descending*,
    i.e. at index `n-k` when sorted *ascending*. Quickselect finds the value that
    belongs at a target index without sorting the rest: pick a random pivot,
    partition the array into < pivot / == pivot / > pivot, and recurse only into
    the side that contains the target index.

    Because each step discards one side, the expected work is n + n/2 + n/4 + ...
    = O(n). Worst case is O(n^2) if pivots are unlucky, which the random pivot
    makes vanishingly rare. O(1) extra space beyond the recursion if done in place;
    this readable version builds sublists (O(n) space).
    """
    target = len(nums) - k                     # index of the answer in ASCENDING order

    def select(arr: List[int], idx: int) -> int:
        pivot = arr[random.randrange(len(arr))]
        less = [x for x in arr if x < pivot]
        equal = [x for x in arr if x == pivot]
        greater = [x for x in arr if x > pivot]
        if idx < len(less):
            return select(less, idx)           # answer is in the smaller side
        if idx < len(less) + len(equal):
            return pivot                        # answer equals the pivot
        # answer is in the greater side; shift the index past less+equal
        return select(greater, idx - len(less) - len(equal))

    return select(nums, target)


def _test() -> None:
    solvers = (
        find_kth_largest,
        find_kth_largest_sorted,
        find_kth_largest_quickselect,
    )
    # Official LeetCode examples:
    #   [3,2,1,5,6,4], k=2 -> 5
    #   [3,2,3,1,2,4,5,5,6], k=4 -> 4
    cases = [
        ([3, 2, 1, 5, 6, 4], 2, 5),
        ([3, 2, 3, 1, 2, 4, 5, 5, 6], 4, 4),
        ([1], 1, 1),                            # single element
        ([2, 2, 2, 2], 3, 2),                   # all duplicates: kth largest is 2
        ([7, 6, 5, 4, 3, 2, 1], 7, 1),          # k = n -> the minimum
        ([-1, -1, 0, 1], 2, 0),                 # negatives; 2nd largest is 0
    ]
    for nums, k, expected in cases:
        for solve in solvers:
            assert solve(list(nums), k) == expected, (solve.__name__, nums, k)

    # Cross-check all three agree with a sort on a larger random array, every k.
    rng = random.Random(0)
    for _ in range(200):
        n = rng.randint(1, 20)
        arr = [rng.randint(-10, 10) for _ in range(n)]
        k = rng.randint(1, n)
        want = sorted(arr, reverse=True)[k - 1]
        for solve in solvers:
            assert solve(list(arr), k) == want, (solve.__name__, arr, k)

    print("kth_largest_array: all cases passed")


if __name__ == "__main__":
    _test()
