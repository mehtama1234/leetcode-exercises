"""198. House Robber — https://leetcode.com/problems/house-robber/

Houses in a row each hold some money. You cannot rob two adjacent houses. Return
the maximum total you can rob.

Two versions show the DP progression: memoized recursion (top-down) expressing the
rob/skip choice directly, and a rolling two-variable loop (bottom-up, O(1) space).
"""
from typing import Dict, List


def rob_memo(nums: List[int]) -> int:
    """Top-down: from each house, choose to rob it or skip it. O(n) time/space.

    Standing at house i, you either:
      - rob it: take nums[i], then you must jump to i+2, or
      - skip it: move to i+1 and decide there.
    best(i) = max(nums[i] + best(i+2), best(i+1)).
    The naive form recomputes best(i) in many branches, so cache each once.
    """
    cache: Dict[int, int] = {}

    def best(i: int) -> int:
        if i >= len(nums):
            return 0
        if i in cache:
            return cache[i]
        cache[i] = max(nums[i] + best(i + 2), best(i + 1))
        return cache[i]

    return best(0)


def rob(nums: List[int]) -> int:
    """Bottom-up, two rolling variables. O(n) time, O(1) space.

    Walk left to right tracking two running totals:
      - `take`: best if we are free to rob the current house,
      - `skip`: best total already locked in from houses before it.
    At each house the new best-including-this = skip + money, and the new
    carry-forward = max(old take, old skip). Only the last two states matter, so
    no full table is needed.
    """
    take, skip = 0, 0  # take = best if we rob current house; skip = best if we don't
    for money in nums:
        take, skip = skip + money, max(take, skip)
    return max(take, skip)


def _test() -> None:
    cases = [
        ([1, 2, 3, 1], 4),        # rob houses 0 and 2 -> 1 + 3
        ([2, 7, 9, 3, 1], 12),    # rob houses 0, 2, 4 -> 2 + 9 + 1
        ([2, 1, 1, 2], 4),        # rob houses 0 and 3 -> 2 + 2
        ([5], 5),                 # single house
        ([], 0),                  # no houses
    ]
    for nums, expected in cases:
        assert rob(nums) == expected, nums
        assert rob_memo(nums) == expected, nums
    print("rob: all cases passed")


if __name__ == "__main__":
    _test()
