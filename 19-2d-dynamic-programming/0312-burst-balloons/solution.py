"""312. Burst Balloons — https://leetcode.com/problems/burst-balloons/

Each balloon holds a number. Bursting balloon i earns `nums[left]*nums[i]*nums[right]`
where left/right are its *current* neighbours (missing ends count as 1). Burst them
all in some order to maximize total coins.

Shown: the memoized interval recurrence keyed on "which balloon in this range bursts
LAST", then the bottom-up interval tabulation by increasing length.
"""
from functools import lru_cache
from typing import List


def max_coins_memo(nums: List[int]) -> int:
    """Top-down over open intervals (l, r), asking which balloon bursts LAST.

    The trap is thinking about which balloon to pop FIRST — then its neighbours keep
    changing and subproblems overlap messily. Flip it: in an interval, decide which
    balloon `k` is the LAST to pop. When k pops, everything else in the interval is
    already gone, so its neighbours are exactly the fixed walls l and r. That makes
    the two sides independent subintervals (l, k) and (k, r).

    We pad with virtual 1s at both ends and treat (l, r) as the OPEN interval
    strictly between balloons l and r.
    """
    balloons = [1] + nums + [1]
    n = len(balloons)

    @lru_cache(maxsize=None)
    def best(l: int, r: int) -> int:
        if r - l < 2:
            return 0            # no balloons strictly between l and r
        return max(
            balloons[l] * balloons[k] * balloons[r]  # k bursts last, walls l & r
            + best(l, k) + best(k, r)
            for k in range(l + 1, r)
        )

    result = best(0, n - 1)
    best.cache_clear()
    return result


def max_coins(nums: List[int]) -> int:
    """Bottom-up interval DP by increasing gap. O(n^3) time, O(n^2) space.

    dp[l][r] = most coins from bursting every balloon strictly between l and r.
    Fill shortest intervals first so both dp[l][k] and dp[k][r] are ready when we
    compute dp[l][r]. Same "k bursts last" split, just tabulated.
    """
    balloons = [1] + nums + [1]
    n = len(balloons)
    dp = [[0] * n for _ in range(n)]

    for gap in range(2, n):                 # distance between the two walls
        for l in range(0, n - gap):
            r = l + gap
            dp[l][r] = max(
                balloons[l] * balloons[k] * balloons[r] + dp[l][k] + dp[k][r]
                for k in range(l + 1, r)
            )
    return dp[0][n - 1]


def _test() -> None:
    cases = [
        ([3, 1, 5, 8], 167),
        ([1, 5], 10),
        ([5], 5),
        ([], 0),
        ([1, 1, 1], 3),
        ([7, 9, 8, 0, 7, 1, 3, 5, 5, 2, 3], 1654),
    ]
    for nums, expected in cases:
        assert max_coins(nums) == expected, nums
        assert max_coins_memo(nums) == expected, nums
    print("burst_balloons: all cases passed")


if __name__ == "__main__":
    _test()
