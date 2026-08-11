"""647. Palindromic Substrings — https://leetcode.com/problems/palindromic-substrings/

Count how many substrings of `s` are palindromes. Each start/end pair counts
separately, so "aaa" has 6 palindromic substrings: a, a, a, aa, aa, aaa.

Two implementations are kept side by side. The 2-D DP table is the classic
teaching form — it makes the recurrence explicit. Expand-around-center is the
optimal one: same idea, but it drops the O(n^2) table down to O(1) space.
"""
from typing import List


def count_substrings_dp(s: str) -> int:
    """2-D table DP. O(n^2) time, O(n^2) space.

    Let dp[i][j] mean "s[i..j] is a palindrome". A stretch of text is a
    palindrome exactly when its two ends match AND the part strictly inside is
    also a palindrome:

        dp[i][j] = (s[i] == s[j]) and (j - i < 2 or dp[i+1][j-1])

    The `j - i < 2` clause covers the base cases directly: single characters
    (i == j) and adjacent pairs (j == i+1) have no interior to check, so they're
    palindromes as soon as the ends match. Everything longer leans on the
    already-solved shorter answer dp[i+1][j-1] — which is why we fill by
    increasing length (equivalently: i descending, j ascending).
    """
    n = len(s)
    dp: List[List[bool]] = [[False] * n for _ in range(n)]
    count = 0
    for i in range(n - 1, -1, -1):          # i from bottom so dp[i+1][*] is ready
        for j in range(i, n):
            if s[i] == s[j] and (j - i < 2 or dp[i + 1][j - 1]):
                dp[i][j] = True
                count += 1
    return count


def count_substrings(s: str) -> int:
    """Expand around center. O(n^2) time, O(1) space.

    Same recurrence, read from the inside out. Every palindrome has a center:
    either a single character (odd length) or the gap between two characters
    (even length). There are 2n - 1 such centers. From each, push the two
    pointers outward while they still match; every successful step is one more
    palindrome. This is exactly dp[i+1][j-1] -> dp[i][j] growth, but we ride a
    single expanding window instead of storing the whole n^2 table.
    """
    n = len(s)
    count = 0

    def expand(left: int, right: int) -> int:
        found = 0
        while left >= 0 and right < n and s[left] == s[right]:
            found += 1
            left -= 1
            right += 1
        return found

    for center in range(n):
        count += expand(center, center)      # odd-length: single-char center
        count += expand(center, center + 1)  # even-length: between two chars
    return count


def _test() -> None:
    cases = [
        ("abc", 3),      # a, b, c
        ("aaa", 6),      # a,a,a, aa,aa, aaa
        ("a", 1),        # single character
        ("", 0),         # empty string edge case
        ("aba", 4),      # a,b,a, aba
    ]
    for s, expected in cases:
        assert count_substrings(s) == expected, s
        assert count_substrings_dp(s) == expected, s
    print("count_substrings: all cases passed")


if __name__ == "__main__":
    _test()
