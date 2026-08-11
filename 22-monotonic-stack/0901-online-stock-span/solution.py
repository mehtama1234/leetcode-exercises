"""901. Online Stock Span — https://leetcode.com/problems/online-stock-span/

Stream stock prices one at a time. For each new price, return its "span": how many
consecutive days back (including today) the price was <= today's price, stopping
at the first day it was strictly higher.

This is a design problem: implement `StockSpanner` with a `next(price)` method.
A monotonic stack answers each call in amortized O(1) over the whole stream.
"""
from typing import List, Tuple


class StockSpanner:
    """Monotonic decreasing stack of (price, span) blocks.

    Naive: on each new price, walk backward over stored prices counting days that
    are <= today's until a higher one blocks you. That's O(n) per call, O(n^2)
    total, and it re-walks days that earlier, taller prices already swallowed.

    Insight: when today's price is >= a previous day's price, that previous day can
    never again be the barrier for any future day (today is at least as tall and
    stands in front of it). So we *resolve* it now: pop it and absorb its span into
    today's. Keep a stack whose prices strictly decrease bottom -> top; each entry
    stores the total span it already accounts for.

    Each price is pushed once and popped once across the entire stream, so the
    cost is amortized O(1) per `next` even though a single call may pop many
    entries. Each pop "resolves" a run of days that this price now dominates.
    """

    def __init__(self) -> None:
        # stack of (price, span) with prices strictly decreasing bottom -> top
        self._stack: List[Tuple[int, int]] = []

    def next(self, price: int) -> int:
        span = 1  # today itself always counts
        # absorb every earlier day whose price is <= today's; it's now behind a
        # bar at least as tall, so it can never block a future day again.
        while self._stack and self._stack[-1][0] <= price:
            _, prev_span = self._stack.pop()
            span += prev_span
        self._stack.append((price, span))
        return span


def _test() -> None:
    # Official example: calls with these prices produce these spans.
    prices = [100, 80, 60, 70, 60, 75, 85]
    expected = [1, 1, 1, 2, 1, 4, 6]
    s = StockSpanner()
    assert [s.next(p) for p in prices] == expected

    # All increasing: spans grow 1,2,3,...
    s2 = StockSpanner()
    assert [s2.next(p) for p in [1, 2, 3, 4, 5]] == [1, 2, 3, 4, 5]

    # All decreasing: every span is 1 (each day blocked by the taller day before).
    s3 = StockSpanner()
    assert [s3.next(p) for p in [5, 4, 3, 2, 1]] == [1, 1, 1, 1, 1]

    # Equal prices count as <= today, so they get absorbed.
    s4 = StockSpanner()
    assert [s4.next(p) for p in [30, 30, 30]] == [1, 2, 3]

    # Single price.
    s5 = StockSpanner()
    assert s5.next(42) == 1

    print("online_stock_span: all cases passed")


if __name__ == "__main__":
    _test()
