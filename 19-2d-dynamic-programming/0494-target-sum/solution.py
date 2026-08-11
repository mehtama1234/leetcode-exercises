"""494. Target Sum — https://leetcode.com/problems/target-sum/

Given an array of non-negative integers and a target, put a `+` or `-` in front
of each number and count how many sign assignments make the expression equal the
target.

Shown: the exponential branch-on-every-sign recursion, the memoized recurrence
on (index, running sum), and the subset-sum reduction that shrinks it to a 1-D
count.
"""
from functools import lru_cache
from typing import List


def find_target_sum_ways_naive(nums: List[int], target: int) -> int:
    """Branch on the sign of each number. O(2^n) time.

    For each index we recurse twice: once adding nums[i], once subtracting it.
    When we run off the end, we scored one valid assignment iff the running sum
    landed on the target. This is the literal definition — and it explores an
    exponential tree because two different prefixes can reach the same running
    sum yet each spawns its own subtree.
    """
    n = len(nums)

    def go(i: int, running: int) -> int:
        if i == n:
            return 1 if running == target else 0
        return go(i + 1, running + nums[i]) + go(i + 1, running - nums[i])

    return go(0, 0)


def find_target_sum_ways_memo(nums: List[int], target: int) -> int:
    """Same recurrence, cached on (index, running sum). O(n * sum) states."""
    n = len(nums)

    @lru_cache(maxsize=None)
    def go(i: int, running: int) -> int:
        if i == n:
            return 1 if running == target else 0
        return go(i + 1, running + nums[i]) + go(i + 1, running - nums[i])

    result = go(0, 0)
    go.cache_clear()
    return result


def find_target_sum_ways(nums: List[int], target: int) -> int:
    """Reduce to subset-sum counting, then 1-D tabulate. O(n * S) time, O(S) space.

    Split the numbers into a positive group P and a negative group N.
      sum(P) - sum(N) = target      and      sum(P) + sum(N) = total
    Add them:  2*sum(P) = target + total, so sum(P) = (target + total) / 2.

    So the question becomes: how many subsets of `nums` sum to that value?
    That's a classic 0/1 subset-sum *count*: dp[s] = number of subsets summing
    to s. Iterate s downward so each number is used at most once.
    """
    total = sum(nums)
    # need = required positive-group sum; must be a non-negative even split
    if (total + target) % 2 != 0 or abs(target) > total:
        return 0
    need = (total + target) // 2

    dp = [0] * (need + 1)
    dp[0] = 1                       # one subset sums to 0: the empty subset
    for x in nums:
        for s in range(need, x - 1, -1):
            dp[s] += dp[s - x]      # count subsets that include x
    return dp[need]


def _test() -> None:
    cases = [
        (([1, 1, 1, 1, 1], 3), 5),
        (([1], 1), 1),
        (([1], 2), 0),
        (([0, 0, 0, 0, 0, 0, 0, 0, 1], 1), 256),  # zeros each double the count
        (([100], -200), 0),
    ]
    for (nums, target), expected in cases:
        assert find_target_sum_ways(nums, target) == expected, (nums, target)
        assert find_target_sum_ways_memo(nums, target) == expected, (nums, target)
        assert find_target_sum_ways_naive(nums, target) == expected, (nums, target)
    print("target_sum: all cases passed")


if __name__ == "__main__":
    _test()
