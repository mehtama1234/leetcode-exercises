"""322. Coin Change — https://leetcode.com/problems/coin-change/

Given coin denominations and an amount, return the fewest coins that sum to that
amount (coins reusable, unlimited supply), or -1 if no combination works.

Two implementations are kept side by side so the reason the fast one exists is
visible: the memoized recursion is the honest top-down statement of the problem,
and the bottom-up table is the same recurrence filled in order.
"""
from typing import List, Dict


def coin_change_memo(coins: List[int], amount: int) -> int:
    """Top-down recursion with memoization. O(amount * len(coins)) time.

    The recurrence: to make `rem`, try every coin `c` as the *last* coin used.
    That leaves `rem - c` to make with the same coins, an identical subproblem.
    So fewest(rem) = 1 + min over usable c of fewest(rem - c). Without a cache
    this recomputes the same `rem` values along many different paths — that
    repetition is the waste. The dict remembers each `rem` once.
    """
    cache: Dict[int, int] = {}

    def fewest(rem: int) -> int:
        if rem == 0:
            return 0
        if rem < 0:
            return float("inf")  # this path overshot; unusable
        if rem in cache:
            return cache[rem]
        best = float("inf")
        for c in coins:
            best = min(best, 1 + fewest(rem - c))
        cache[rem] = best
        return best

    result = fewest(amount)
    return result if result != float("inf") else -1


def coin_change(coins: List[int], amount: int) -> int:
    """Bottom-up table (unbounded knapsack). O(amount * len(coins)) time, O(amount) space.

    Same recurrence, filled smallest-first so every subproblem it needs is
    already solved. dp[a] = fewest coins to make amount `a`. Start dp[0] = 0
    (making zero needs no coins) and everything else = "impossible" (inf). For
    each amount a, try each coin c: if c <= a, using c once means we need
    dp[a - c] + 1 coins. Take the minimum. Because coins are reusable we scan
    amounts upward, so dp[a - c] may itself already include that same coin.
    """
    dp = [0] + [float("inf")] * amount  # dp[a] = fewest coins to make a
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                dp[a] = min(dp[a], dp[a - c] + 1)
    return dp[amount] if dp[amount] != float("inf") else -1


def _test() -> None:
    cases = [
        (([1, 2, 5], 11), 3),   # 5 + 5 + 1
        (([2], 3), -1),         # impossible: odd amount from a single even coin
        (([1], 0), 0),          # zero amount needs zero coins
        (([1], 1), 1),
        (([2, 5, 10, 1], 27), 4),  # 10 + 10 + 5 + 2
        (([186, 419, 83, 408], 6249), 20),
    ]
    for (coins, amount), expected in cases:
        assert coin_change(coins, amount) == expected, (coins, amount)
        # the top-down version must agree with the table on every case
        assert coin_change_memo(coins, amount) == expected, (coins, amount)
    print("coin_change: all cases passed")


if __name__ == "__main__":
    _test()
