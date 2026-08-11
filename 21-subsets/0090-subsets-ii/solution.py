"""90. Subsets II — https://leetcode.com/problems/subsets-ii/

Like Subsets, but the input may contain duplicate numbers. Return all *unique*
subsets — no two subsets in the answer may be equal as multisets.

The whole difficulty is duplicate handling: sort first, then at each depth skip a
number equal to the previous sibling you already tried.
"""
from typing import List


def subsets_with_dup(nums: List[int]) -> List[List[int]]:
    """Backtracking with a sorted array and a sibling-skip. O(n * 2^n) time.

    Sorting makes equal values adjacent. We build subsets by *position*, choosing
    at each depth which number to place next from the remaining tail. The rule
    that kills duplicates: within one level of the loop, if nums[i] == nums[i-1]
    and i > start, skip it — we already generated every subset that starts with
    that value at this position, so trying it again only remakes the same sets.
    """
    nums = sorted(nums)
    n = len(nums)
    result: List[List[int]] = []
    path: List[int] = []

    def backtrack(start: int) -> None:
        result.append(path[:])          # every node is itself a valid subset
        for i in range(start, n):
            if i > start and nums[i] == nums[i - 1]:
                continue                # skip duplicate sibling at this depth
            path.append(nums[i])        # choose
            backtrack(i + 1)            # explore the tail after i
            path.pop()                  # un-choose

    backtrack(0)
    return result


def _key(lists: List[List[int]]) -> set:
    """Order-independent key: multiset of subsets, each as a sorted tuple."""
    from collections import Counter
    return dict(Counter(tuple(sorted(s)) for s in lists))


def _test() -> None:
    cases = [
        ([1, 2, 2], [[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]),
        ([0], [[], [0]]),
        ([], [[]]),                         # edge: empty input
        ([4, 4, 4, 1, 4],                   # heavy duplication
         [[], [1], [1, 4], [1, 4, 4], [1, 4, 4, 4], [1, 4, 4, 4, 4],
          [4], [4, 4], [4, 4, 4], [4, 4, 4, 4]]),
    ]
    for nums, expected in cases:
        got = subsets_with_dup(nums)
        # no duplicate subsets in the output
        seen = {tuple(s) for s in got}
        assert len(seen) == len(got), (nums, "produced a duplicate subset")
        assert _key(got) == _key(expected), (nums, got)
    print("subsets_with_dup: all cases passed")


if __name__ == "__main__":
    _test()
