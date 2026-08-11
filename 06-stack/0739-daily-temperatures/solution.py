"""739. Daily Temperatures — https://leetcode.com/problems/daily-temperatures/

Given daily temperatures, for each day return how many days you must wait until a
warmer day. If no warmer day ever comes, that day's answer is 0.
"""
from typing import List


def daily_temperatures_brute(temperatures: List[int]) -> List[int]:
    """For each day, scan forward for the next warmer day. O(n^2) time, O(1) extra.

    This is the definition turned into code: stand on day i and walk forward until
    you find a hotter day, recording the gap. Correct, but a long run of cooling
    days makes every earlier day re-scan that same tail — the waste we remove next.
    """
    n = len(temperatures)
    answer = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if temperatures[j] > temperatures[i]:
                answer[i] = j - i
                break
    return answer


def daily_temperatures(temperatures: List[int]) -> List[int]:
    """Monotonic decreasing stack, single pass. O(n) time, O(n) space.

    Key insight: today's temperature is the "next warmer day" for every earlier
    day that has been *waiting* and is now beaten. So we keep a stack of the
    indices of days still waiting for something warmer, and because each new day
    resolves the ones it's warmer than, the temperatures on that stack are always
    decreasing (top = coolest, most recent waiter).

    For each new day i: while the day on top of the stack is cooler than today,
    it just found its warmer day (today) — pop it and record the gap i - top.
    Then push i to wait for its own warmer day. Each index is pushed and popped at
    most once, so the whole thing is linear despite the inner while loop.
    """
    n = len(temperatures)
    answer = [0] * n
    stack: List[int] = []  # indices of days still waiting, temps strictly decreasing
    for i, temp in enumerate(temperatures):
        while stack and temperatures[stack[-1]] < temp:
            prev = stack.pop()
            answer[prev] = i - prev
        stack.append(i)
    # whatever is left on the stack never found a warmer day -> stays 0
    return answer


def _test() -> None:
    cases = [
        ([73, 74, 75, 71, 69, 72, 76, 73], [1, 1, 4, 2, 1, 1, 0, 0]),
        ([30, 40, 50, 60], [1, 1, 1, 0]),
        ([30, 60, 90], [1, 1, 0]),
        ([50, 50, 50], [0, 0, 0]),        # ties are NOT warmer -> all 0
        ([90, 80, 70, 60], [0, 0, 0, 0]), # strictly cooling -> nobody waits fills
        ([100], [0]),                     # single day, no future
    ]
    for temps, expected in cases:
        assert daily_temperatures(temps) == expected, temps
        # brute force must agree with the fast version on every case
        assert daily_temperatures_brute(temps) == expected, temps
    print("daily_temperatures: all cases passed")


if __name__ == "__main__":
    _test()
