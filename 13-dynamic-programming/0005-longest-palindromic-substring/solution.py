"""5. Longest Palindromic Substring — https://leetcode.com/problems/longest-palindromic-substring/

Return the longest contiguous substring of `s` that reads the same forwards and
backwards. Any one answer is fine if several tie for longest.

Two implementations sit side by side. The 2-D DP table makes the recurrence
explicit and is the classic teaching form. Expand-around-center is the optimal
version: identical idea, but it drops the O(n^2) table to O(1) extra space.
"""
from typing import List


def longest_palindrome_dp(s: str) -> str:
    """2-D table DP. O(n^2) time, O(n^2) space.

    Let dp[i][j] mean "s[i..j] is a palindrome". A stretch is a palindrome
    exactly when its ends match and the strictly-inside part is a palindrome:

        dp[i][j] = (s[i] == s[j]) and (j - i < 2 or dp[i+1][j-1])

    The `j - i < 2` clause is the base case (single char or adjacent pair: no
    interior to check). We fill i descending / j ascending so dp[i+1][j-1] is
    always ready, and remember the widest True span as we go.
    """
    n = len(s)
    if n == 0:
        return ""
    dp: List[List[bool]] = [[False] * n for _ in range(n)]
    start, best = 0, 1  # best-known palindrome: s[start : start+best]
    for i in range(n - 1, -1, -1):
        for j in range(i, n):
            if s[i] == s[j] and (j - i < 2 or dp[i + 1][j - 1]):
                dp[i][j] = True
                if j - i + 1 > best:
                    start, best = i, j - i + 1
    return s[start:start + best]


def longest_palindrome(s: str) -> str:
    """Expand around center. O(n^2) time, O(1) space.

    Same recurrence read from the inside out. Every palindrome has a center: a
    single character (odd length) or the gap between two characters (even
    length) — 2n - 1 centers in all. From each, push outward while the ends
    match; the widest window any center reaches is the answer. This walks a
    single expanding window instead of storing the whole n^2 table.
    """
    n = len(s)
    if n == 0:
        return ""
    start, end = 0, 0  # best window s[start : end+1]

    def expand(left: int, right: int) -> None:
        nonlocal start, end
        while left >= 0 and right < n and s[left] == s[right]:
            left -= 1
            right += 1
        # loop overshoots by one step on each side; pull back in
        left += 1
        right -= 1
        if right - left > end - start:
            start, end = left, right

    for center in range(n):
        expand(center, center)      # odd-length center
        expand(center, center + 1)  # even-length center
    return s[start:end + 1]


def _test() -> None:
    # "bab" and "aba" both valid for the first case; check via a set of answers
    multi = {
        ("babad",): {"bab", "aba"},
        ("cbbd",): {"bb"},
        ("a",): {"a"},
        ("",): {""},
        ("ac",): {"a", "c"},   # no multi-char palindrome; any single char is fine
        ("aaaa",): {"aaaa"},
    }
    for (s,), valid in multi.items():
        assert longest_palindrome(s) in valid, s
        assert longest_palindrome_dp(s) in valid, s
    print("longest_palindrome: all cases passed")


if __name__ == "__main__":
    _test()
