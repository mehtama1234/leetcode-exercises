"""91. Decode Ways — https://leetcode.com/problems/decode-ways/

Digits 1..26 map to letters A..Z. Given a digit string, count how many distinct
ways it can be decoded back into letters (e.g. "12" -> "AB" or "L", so 2 ways).

Two implementations are kept side by side so the reason the fast one exists is
visible: the memoized recursion is the honest top-down statement, and the
bottom-up table is the same recurrence, then squeezed to O(1) rolling variables.
"""
from typing import Dict


def num_decodings_memo(s: str) -> int:
    """Top-down recursion with memoization. O(n) time, O(n) space.

    The recurrence: standing at position i, decode either the single digit s[i]
    (if it's 1..9) and recurse from i+1, or the pair s[i:i+2] (if it's 10..26)
    and recurse from i+2. Total ways from i is the sum. The same position i is
    reached along many decode paths, so plain recursion re-solves it repeatedly —
    that repetition is the waste. cache[i] remembers each position once.
    """
    n = len(s)
    cache: Dict[int, int] = {}

    def ways(i: int) -> int:
        if i == n:
            return 1  # reached the end cleanly = one complete decoding
        if s[i] == "0":
            return 0  # no letter starts with 0, this path is dead
        if i in cache:
            return cache[i]
        total = ways(i + 1)  # take s[i] as a single digit (1..9)
        if i + 1 < n and int(s[i:i + 2]) <= 26:
            total += ways(i + 2)  # take s[i:i+2] as a pair (10..26)
        cache[i] = total
        return total

    return ways(0)


def num_decodings(s: str) -> int:
    """Bottom-up, two rolling variables. O(n) time, O(1) space.

    Same recurrence, filled from the end. Let dp[i] = ways to decode s[i:], with
    dp[n] = 1. dp[i] only ever reads dp[i+1] and dp[i+2], so we don't need the
    whole table — just those two values, slid backward as we go. `ahead1` plays
    dp[i+1], `ahead2` plays dp[i+2].
    """
    n = len(s)
    ahead2 = 0        # dp[i+2], unused until we have two lookahead slots
    ahead1 = 1        # dp[n] = 1
    for i in range(n - 1, -1, -1):
        if s[i] == "0":
            curr = 0
        else:
            curr = ahead1  # single digit
            if i + 1 < n and int(s[i:i + 2]) <= 26:
                curr += ahead2  # valid pair
        ahead2, ahead1 = ahead1, curr
    return ahead1


def _test() -> None:
    cases = [
        ("12", 2),        # "AB" or "L"
        ("226", 3),       # "BZ", "VF", "BBF"
        ("06", 0),        # leading zero can't be decoded
        ("0", 0),         # a lone zero is invalid
        ("10", 1),        # only "J"; "1","0" fails on the zero
        ("100", 0),       # "10" then a dangling "0"
        ("2101", 1),      # "U","10","1" -> the trailing "01" forces the split
        ("11106", 2),     # "AAJF" or "KJF"
        ("27", 1),        # 27 > 26, so only "B","G"
    ]
    for s, expected in cases:
        assert num_decodings(s) == expected, s
        # the top-down version must agree with the rolling one on every case
        assert num_decodings_memo(s) == expected, s
    print("num_decodings: all cases passed")


if __name__ == "__main__":
    _test()
