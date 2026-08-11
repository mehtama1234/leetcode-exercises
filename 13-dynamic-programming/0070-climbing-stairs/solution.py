"""70. Climbing Stairs — https://leetcode.com/problems/climbing-stairs/

You climb a staircase of n steps, taking either 1 or 2 steps at a time. Count how
many distinct sequences of moves reach the top.

Three versions show the standard DP progression: naive recursion (exponential),
the same recursion with memoization (top-down), and a rolling two-variable loop
(bottom-up, O(1) space).
"""
from typing import Dict


def climb_naive(n: int) -> int:
    """Direct translation of the choice. O(2^n) time — exponential.

    From step 0 your last move landed here either from step n-1 (a 1-step) or
    from step n-2 (a 2-step). So ways(n) = ways(n-1) + ways(n-2). Correct, but it
    re-solves the same subproblems in every branch — that repetition is the waste.
    """
    if n <= 2:
        return n
    return climb_naive(n - 1) + climb_naive(n - 2)


def climb_memo(n: int) -> int:
    """Same recursion, cache each answer once. O(n) time, O(n) space.

    There are only n distinct subproblems, ways(1)..ways(n). Remember each the
    first time it's computed and the exponential call tree collapses to a line.
    """
    cache: Dict[int, int] = {}

    def go(k: int) -> int:
        if k <= 2:
            return k
        if k in cache:
            return cache[k]
        cache[k] = go(k - 1) + go(k - 2)
        return cache[k]

    return go(n)


def climb(n: int) -> int:
    """Bottom-up, two rolling variables. O(n) time, O(1) space.

    The recurrence only reaches back two steps, so keep just the last two counts.
    Base cases: ways(1) = 1, ways(2) = 2. Slide the window forward from there.
    """
    if n <= 2:
        return n
    prev, curr = 1, 2  # ways(1), ways(2)
    for _ in range(3, n + 1):
        prev, curr = curr, prev + curr
    return curr


def _test() -> None:
    cases = [(1, 1), (2, 2), (3, 3), (4, 5), (5, 8), (10, 89), (20, 10946)]
    for n, expected in cases:
        assert climb(n) == expected, n
        assert climb_memo(n) == expected, n
    # naive only on small n so the test stays fast
    for n, expected in cases[:5]:
        assert climb_naive(n) == expected, n
    print("climb: all cases passed")


if __name__ == "__main__":
    _test()
