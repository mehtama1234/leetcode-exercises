"""309. Best Time to Buy and Sell Stock with Cooldown —
https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-cooldown/

You may buy and sell a stock as many times as you like, but after you *sell* you
must skip (cool down for) one day before buying again. Maximize total profit.

Shown: the memoized state machine on (day, do-I-hold-a-share), then the O(1)-space
three-variable roll that ships in interviews.
"""
from functools import lru_cache
from typing import List


def max_profit_memo(prices: List[int]) -> int:
    """Top-down over (day, holding). O(n) states, O(n) time and space.

    State is exactly two things: which day we're on and whether we currently hold
    a share. From "not holding" we may rest or buy; from "holding" we may rest or
    sell — and selling jumps us to day+2, which is the cooldown baked straight
    into the transition. We take the max over the choices at each state.
    """
    n = len(prices)

    @lru_cache(maxsize=None)
    def best(day: int, holding: bool) -> int:
        if day >= n:
            return 0
        rest = best(day + 1, holding)          # do nothing today
        if holding:
            sell = prices[day] + best(day + 2, False)  # sell, then cooldown day
            act = sell
        else:
            buy = -prices[day] + best(day + 1, True)   # spend cash to buy
            act = buy
        return max(rest, act)

    result = best(0, False)
    best.cache_clear()
    return result


def max_profit(prices: List[int]) -> int:
    """Bottom-up rolled to O(1) space via three running maxima.

    Track the best profit achievable *ending* in each state after the current day:
      hold  = we hold a share
      sold  = we just sold today (so tomorrow is a forced cooldown)
      rest  = we hold nothing and are free to buy (not fresh off a sale)
    Transitions per day with price p:
      hold' = max(hold, rest - p)   # keep holding, or buy today from a free day
      sold' = hold + p              # sell today
      rest' = max(rest, sold)       # stay free, or the cooldown after a sale ends
    Cooldown lives in the wall between `sold` and `rest`: you can only reach a
    fresh buy through `rest`, and you only enter `rest` a day after selling.
    """
    if not prices:
        return 0
    hold = float("-inf")   # impossible to hold before any day starts
    sold = 0.0
    rest = 0.0
    for p in prices:
        prev_sold = sold
        sold = hold + p
        hold = max(hold, rest - p)
        rest = max(rest, prev_sold)
    return int(max(sold, rest))   # never end holding a share


def _test() -> None:
    cases = [
        ([1, 2, 3, 0, 2], 3),
        ([1], 0),
        ([], 0),
        ([1, 2, 4], 3),
        ([6, 1, 3, 2, 4, 7], 6),
        ([2, 1], 0),          # only losses available
    ]
    for prices, expected in cases:
        assert max_profit(prices) == expected, prices
        assert max_profit_memo(prices) == expected, prices
    print("stock_with_cooldown: all cases passed")


if __name__ == "__main__":
    _test()
