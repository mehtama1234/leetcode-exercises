"""213. House Robber II — https://leetcode.com/problems/house-robber-ii/

Same as House Robber, but the houses are arranged in a circle, so the first and
last house are also adjacent. Return the maximum you can rob without hitting two
neighbors.

The trick: reduce the circular problem to two ordinary linear House-Robber runs.
"""
from typing import List


def _rob_line(nums: List[int]) -> int:
    """Plain House Robber on a straight row. O(n) time, O(1) space.

    Two rolling states: `take` = best if we may rob the current house, `skip` =
    best already locked in without it. (This is problem 198's optimal solution.)
    """
    take, skip = 0, 0
    for money in nums:
        take, skip = skip + money, max(take, skip)
    return max(take, skip)


def rob(nums: List[int]) -> int:
    """Circular row: break the loop into two linear cases. O(n) time, O(1) space.

    The circle only adds one constraint: house 0 and house n-1 are neighbors, so
    they can't both be robbed. That splits every valid plan into two families:
      - plans that never rob the last house  -> houses[0 .. n-2] as a line,
      - plans that never rob the first house -> houses[1 .. n-1] as a line.
    Every legal circular plan lives in at least one family (a plan can't include
    both ends), so the best circular answer is the max of the two linear answers.
    The n == 1 case has no "other end", so handle it directly.
    """
    if len(nums) == 1:
        return nums[0]
    return max(_rob_line(nums[:-1]), _rob_line(nums[1:]))


def _test() -> None:
    cases = [
        ([2, 3, 2], 3),           # can't take both 2s (ends touch) -> take middle 3
        ([1, 2, 3, 1], 4),        # rob houses 0 and 2 -> 1 + 3
        ([1, 2, 3], 3),           # take the single 3
        ([5], 5),                 # single house, no circle constraint
        ([1, 3, 1, 3, 100], 103), # rob house 1 and 4 -> 3 + 100
    ]
    for nums, expected in cases:
        assert rob(nums) == expected, nums
    print("rob_circular: all cases passed")


if __name__ == "__main__":
    _test()
