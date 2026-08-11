"""518. Coin Change II — https://leetcode.com/problems/coin-change-ii/

Given coin denominations and an amount, count how many *distinct combinations*
of coins add up to the amount. Order does not matter: 1+2 and 2+1 are the same
combination. Coins may be reused any number of times.

Three views are kept side by side: a naive top-down count that overcounts,
the fixed memoized recurrence, and the 1-D tabulation that everyone ships.
"""
from functools import lru_cache
from typing import List


def change_naive(amount: int, coins: List[int]) -> int:
    """Count combinations by recursion over (coin index, remaining amount).

    The honest recurrence: for the coin at index `i`, either *skip* it entirely
    (move to i+1 with the same amount) or *take* one more of it (stay at i,
    subtract its value). Fixing an index and never moving backwards is what stops
    us from counting 1+2 and 2+1 separately — order is pinned by index order.

    Without memoization this re-solves the same (i, remaining) states many times,
    so it is exponential. It is here only to show the shape of the recurrence.
    """
    n = len(coins)

    def count(i: int, remaining: int) -> int:
        if remaining == 0:
            return 1            # exact change made — one valid combination
        if remaining < 0 or i == n:
            return 0            # overshot, or ran out of coin types
        # skip coin i entirely  +  use one more of coin i (and stay on i)
        return count(i + 1, remaining) + count(i, remaining - coins[i])

    return count(0, amount)


def change_memo(amount: int, coins: List[int]) -> int:
    """Same recurrence, cached on (i, remaining). O(n * amount) time and space."""
    n = len(coins)

    @lru_cache(maxsize=None)
    def count(i: int, remaining: int) -> int:
        if remaining == 0:
            return 1
        if remaining < 0 or i == n:
            return 0
        return count(i + 1, remaining) + count(i, remaining - coins[i])

    result = count(0, amount)
    count.cache_clear()
    return result


def change(amount: int, coins: List[int]) -> int:
    """Bottom-up 1-D tabulation. O(n * amount) time, O(amount) space.

    dp[a] = number of ways to make amount `a` using the coins considered so far.
    We add coins one at a time (outer loop). Processing amount in increasing
    order lets a coin be reused, and adding coins one at a time (not amounts on
    the outside) is exactly what forbids reordering — each coin's whole
    contribution is folded in before the next coin is even seen.
    """
    dp = [0] * (amount + 1)
    dp[0] = 1                       # one way to make 0: take nothing
    for coin in coins:
        for a in range(coin, amount + 1):
            dp[a] += dp[a - coin]   # ways using this coin at least once
    return dp[amount]


def _test() -> None:
    cases = [
        ((5, [1, 2, 5]), 4),
        ((3, [2]), 0),
        ((10, [10]), 1),
        ((0, [7]), 1),          # empty combination makes 0
        ((5, []), 0),           # no coins, positive amount
        ((500, [1, 2, 5]), 12701),
    ]
    for (amount, coins), expected in cases:
        assert change(amount, coins) == expected, (amount, coins)
        assert change_memo(amount, coins) == expected, (amount, coins)
    # only exercise the exponential naive version on tiny inputs
    for (amount, coins), expected in cases[:4]:
        assert change_naive(amount, coins) == expected, (amount, coins)
    print("coin_change_ii: all cases passed")


if __name__ == "__main__":
    _test()
