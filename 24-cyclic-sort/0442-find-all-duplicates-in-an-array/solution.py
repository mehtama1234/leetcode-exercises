"""442. Find All Duplicates in an Array — https://leetcode.com/problems/find-all-duplicates-in-an-array/

Given `nums` of length n where every value is in 1..n, some appear once and some
appear exactly twice. Return all the values that appear twice, in O(n) time and
O(1) extra space.

Because values are exactly 1..n, value `v` maps to index `v-1`. We use the SIGN
of the number parked at that home index as a "have I visited this value?" flag —
the array is its own hash table.
"""
from typing import List


def find_duplicates_counter(nums: List[int]) -> List[int]:
    """Honest baseline: count occurrences, report the ones that hit 2.

    Simple and correct, but the counter is O(n) EXTRA memory — the thing the
    problem asks us to avoid. Kept only to check the clever version against.
    """
    seen: set[int] = set()
    out: List[int] = []
    for x in nums:
        if x in seen:
            out.append(x)
        seen.add(x)
    return out


def find_duplicates(nums: List[int]) -> List[int]:
    """Sign-flip trick (index-as-hash). O(n) time, O(1) extra space.

    Key insight: every value is in 1..n, so value `v` has a home index `v - 1`.
    Walk the array. For each value `v`, look at its home slot. We use the SIGN of
    the number sitting there as a visited-flag:

      - If it's still positive, this is the first time we've reached `v` — flip it
        negative to record "seen once".
      - If it's already negative, we've been here before, so `v` is a duplicate.

    We read `abs(x)` because a slot's value may have been flipped by an earlier
    step; the magnitude still tells us which value we're looking at. The array
    carries the bookkeeping, so we spend no extra memory.
    """
    out: List[int] = []
    for x in nums:
        v = abs(x)
        home = v - 1
        if nums[home] < 0:
            out.append(v)
        else:
            nums[home] = -nums[home]
    return out


def _test() -> None:
    cases = [
        ([4, 3, 2, 7, 8, 2, 3, 1], [2, 3]),
        ([1, 1, 2], [1]),
        ([1], []),                 # no duplicates
        ([2, 2], [2]),             # smallest duplicate case
        ([1, 2, 3, 4], []),        # all unique
    ]
    for nums, expected in cases:
        assert sorted(find_duplicates_counter(list(nums))) == sorted(expected), nums
        assert sorted(find_duplicates(list(nums))) == sorted(expected), nums
    print("find_duplicates: all cases passed")


if __name__ == "__main__":
    _test()
