"""347. Top K Frequent Elements — https://leetcode.com/problems/top-k-frequent-elements/

Given an array `nums` and an integer `k`, return the `k` values that appear most
often. The answer is guaranteed unique; return them in any order.

Two implementations: the obvious "count then sort by frequency", and a
bucket-by-frequency pass that avoids sorting entirely.
"""
from typing import Dict, List


def top_k_frequent_sort(nums: List[int], k: int) -> List[int]:
    """Count, then sort values by their count. O(n log n) time.

    Tally every value, then order the distinct values by frequency descending and
    take the first k. Correct and easy, but sorting all distinct values costs a
    log factor when we only ever want the top k.
    """
    counts: Dict[int, int] = {}
    for x in nums:
        counts[x] = counts.get(x, 0) + 1
    ordered = sorted(counts, key=lambda v: counts[v], reverse=True)
    return ordered[:k]


def top_k_frequent(nums: List[int], k: int) -> List[int]:
    """Bucket by frequency. O(n) time, O(n) space.

    Key insight: a value's frequency is an integer between 1 and n, so it can be
    used as an array index. Make buckets[f] = list of values seen exactly f times.
    Then walk buckets from the highest frequency down, collecting values until we
    have k. No comparison sort needed — the frequency *is* the sort key, and it
    lives in a bounded range, so counting-sort style placement replaces sorting.
    """
    counts: Dict[int, int] = {}
    for x in nums:
        counts[x] = counts.get(x, 0) + 1

    # index by frequency; index 0 is unused (no value has frequency 0)
    buckets: List[List[int]] = [[] for _ in range(len(nums) + 1)]
    for value, freq in counts.items():
        buckets[freq].append(value)

    result: List[int] = []
    for freq in range(len(nums), 0, -1):
        for value in buckets[freq]:
            result.append(value)
            if len(result) == k:
                return result
    return result


def _test() -> None:
    cases = [
        (([1, 1, 1, 2, 2, 3], 2), {1, 2}),
        (([1], 1), {1}),
        (([4, 4, 4, 5, 5, 6], 2), {4, 5}),
        (([7, 7, 8, 8, 9], 3), {7, 8, 9}),  # k equals number of distinct values
    ]
    for (nums, k), expected in cases:
        # answer order is unspecified, so compare as sets
        assert set(top_k_frequent(nums, k)) == expected, (nums, k)
        assert set(top_k_frequent_sort(nums, k)) == expected, (nums, k)
    print("top_k_frequent: all cases passed")


if __name__ == "__main__":
    _test()
