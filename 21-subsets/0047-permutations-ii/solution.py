"""47. Permutations II — https://leetcode.com/problems/permutations-ii/

Like Permutations, but the input may contain duplicates. Return all *unique*
orderings — no two permutations in the answer may be identical.

Same trick as Subsets II: sort the array, then within one slot refuse to place a
value equal to the previous one unless that previous copy is currently in use.
"""
from typing import List


def permute_unique(nums: List[int]) -> List[List[int]]:
    """Backtracking with sorted input + a duplicate-sibling skip. O(n * n!).

    Sorting groups equal values so we can check the neighbor in O(1). The skip
    rule for filling the current slot: if nums[i] == nums[i-1] and the previous
    copy is NOT currently used (used[i-1] is False), skip nums[i]. That enforces a
    fixed order among equal copies — a duplicate value may only be placed after
    its identical predecessor has already been placed — so the same arrangement is
    never built two different ways.
    """
    nums = sorted(nums)
    n = len(nums)
    result: List[List[int]] = []
    path: List[int] = []
    used = [False] * n

    def backtrack() -> None:
        if len(path) == n:
            result.append(path[:])
            return
        for i in range(n):
            if used[i]:
                continue
            if i > 0 and nums[i] == nums[i - 1] and not used[i - 1]:
                continue                # earlier equal copy not placed yet -> skip
            used[i] = True              # choose
            path.append(nums[i])
            backtrack()                 # explore
            path.pop()                  # un-choose
            used[i] = False

    backtrack()
    return result


def _test() -> None:
    from collections import Counter
    cases = [
        ([1, 1, 2], [[1, 1, 2], [1, 2, 1], [2, 1, 1]]),
        ([1, 2, 3],
         [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]),
        ([2, 2, 2], [[2, 2, 2]]),       # edge: all identical -> one permutation
        ([], [[]]),                     # edge: empty
    ]
    for nums, expected in cases:
        got = permute_unique(nums)
        # order-independent set comparison; permutations keep internal order
        assert {tuple(s) for s in got} == {tuple(s) for s in expected}, (nums, got)
        # no duplicate orderings emitted
        assert len(got) == len({tuple(s) for s in got}), (nums, "duplicate emitted")
    print("permute_unique: all cases passed")


if __name__ == "__main__":
    _test()
