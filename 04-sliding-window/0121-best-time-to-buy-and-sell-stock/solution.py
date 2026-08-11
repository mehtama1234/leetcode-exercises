"""121. Best Time to Buy and Sell Stock — https://leetcode.com/problems/best-time-to-buy-and-sell-stock/

Given daily prices, buy on one day and sell on a *later* day to make the largest
profit. Return that profit, or 0 if no profitable trade exists.

Two implementations are kept side by side so the reason the fast one exists is
visible: the brute force tries every buy/sell pair, and the single pass is what
you get by asking "for today's sell, what's the only thing I actually need to
know about the past?".
"""
from typing import List


def max_profit_brute(prices: List[int]) -> int:
    """Try every buy day paired with every later sell day. O(n^2) time, O(1) space.

    This is the definition turned directly into code: for each buy day i, look at
    every later day j and see what selling there earns. It's correct, but for
    each sell day it re-scans all earlier days to find a good buy price — that
    repeated scanning is the waste we remove next.
    """
    best = 0
    n = len(prices)
    for i in range(n):
        for j in range(i + 1, n):
            best = max(best, prices[j] - prices[i])
    return best


def max_profit(prices: List[int]) -> int:
    """Track the cheapest price seen so far, one pass. O(n) time, O(1) space.

    Key insight: on the day you sell, the only thing you want from the past is the
    *single* lowest price before today — nothing else about history matters. So
    walk left to right, remember the minimum price seen so far, and at each day
    ask "sell here against that minimum: how much would I make?". Keep the best.
    We never look back, so it's one pass.
    """
    min_price = float("inf")   # cheapest buy price seen so far
    best = 0                   # best profit found so far (0 = don't trade)
    for price in prices:
        if price < min_price:
            min_price = price          # a new, cheaper day to have bought
        else:
            best = max(best, price - min_price)  # sell today against the min
    return best


def _test() -> None:
    cases = [
        ([7, 1, 5, 3, 6, 4], 5),      # buy at 1, sell at 6
        ([7, 6, 4, 3, 1], 0),         # only falls: no profitable trade
        ([1, 2, 3, 4, 5], 4),         # only rises: buy first, sell last
        ([2, 4, 1], 2),               # best is early, min comes after it
        ([5], 0),                     # one day: can't buy and sell
        ([3, 3, 3], 0),               # flat prices
    ]
    for prices, expected in cases:
        assert max_profit(prices) == expected, prices
        # brute force must agree with the fast version on every case
        assert max_profit_brute(prices) == expected, prices
    print("max_profit: all cases passed")


if __name__ == "__main__":
    _test()
