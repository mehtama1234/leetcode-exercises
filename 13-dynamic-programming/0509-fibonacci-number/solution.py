"""509. Fibonacci Number — https://leetcode.com/problems/fibonacci-number/

Return the n-th Fibonacci number, where F(0)=0, F(1)=1, and each later value is
the sum of the two before it.

Three versions are kept side by side to show the standard DP progression:
naive recursion (exponential), the same recursion with memoization (top-down),
and a rolling two-variable loop (bottom-up, O(1) space).
"""
from typing import Dict


def fib_naive(n: int) -> int:
    """Direct translation of the definition. O(phi^n) time — exponential.

    F(n) = F(n-1) + F(n-2). Correct, but it recomputes the same subproblems
    over and over: computing F(5) computes F(3) twice, F(2) three times, and so
    on. That re-computation is the entire waste DP exists to erase.
    """
    if n < 2:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


def fib_memo(n: int) -> int:
    """Same recursion, but remember each answer once. O(n) time, O(n) space.

    The tree of calls only ever asks about n distinct values, F(0)..F(n). Cache
    each the first time it's computed and every later request is a lookup, so the
    branching tree collapses into a straight line.
    """
    cache: Dict[int, int] = {}

    def go(k: int) -> int:
        if k < 2:
            return k
        if k in cache:
            return cache[k]
        cache[k] = go(k - 1) + go(k - 2)
        return cache[k]

    return go(n)


def fib(n: int) -> int:
    """Bottom-up, two rolling variables. O(n) time, O(1) space.

    The recurrence only ever looks back two steps, so we never need the whole
    table — just the previous two values. Walk forward from the base cases,
    sliding the window one step at a time.
    """
    if n < 2:
        return n
    prev, curr = 0, 1  # F(0), F(1)
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr
    return curr


def _test() -> None:
    cases = [(0, 0), (1, 1), (2, 1), (3, 2), (4, 3), (5, 5), (10, 55), (30, 832040)]
    for n, expected in cases:
        assert fib(n) == expected, n
        assert fib_memo(n) == expected, n
    # naive is only checked on small n so the test stays fast
    for n, expected in cases[:6]:
        assert fib_naive(n) == expected, n
    print("fib: all cases passed")


if __name__ == "__main__":
    _test()
