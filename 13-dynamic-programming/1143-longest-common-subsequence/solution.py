"""1143. Longest Common Subsequence — https://leetcode.com/problems/longest-common-subsequence/

Given two strings, return the length of their longest common subsequence: the
longest sequence of characters that appears in both, in the same relative order
(not necessarily contiguous).

A full 2-D tabulation is the clear version; a 1-D rolling variant follows to show
the standard "we only ever read the previous row" space optimization.
"""
from typing import List


def longest_common_subsequence(text1: str, text2: str) -> int:
    """Bottom-up 2-D table. O(m*n) time, O(m*n) space.

    Define dp[i][j] = length of the LCS of the first i characters of text1 and
    the first j characters of text2. Look at the LAST characters of each prefix:

      - If text1[i-1] == text2[j-1], that shared character can end the common
        subsequence, so dp[i][j] = 1 + dp[i-1][j-1] (both prefixes shrink by one).
      - Otherwise at least one of those two characters is NOT in the common
        subsequence, so we drop one and take the better of the two choices:
        dp[i][j] = max(dp[i-1][j], dp[i][j-1]).

    Row 0 and column 0 are all zeros: an empty prefix shares nothing. Filling the
    table in increasing i, j order means every cell we read is already done.
    """
    m, n = len(text1), len(text2)
    dp: List[List[int]] = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]


def longest_common_subsequence_1d(text1: str, text2: str) -> int:
    """Same recurrence, two rows. O(m*n) time, O(min(m, n)) space.

    dp[i][j] only ever reads row i-1 and the current row i. So we never need the
    whole grid — just the previous row and the row being built. We iterate text1
    over the rows and text2 over the columns; making text2 the shorter string
    keeps the row (and the space) as small as possible.

    The one subtlety: dp[i-1][j-1] is the value at the current column BEFORE we
    overwrite it this row, so we stash it in `diag` before assigning.
    """
    if len(text2) > len(text1):
        text1, text2 = text2, text1  # ensure the row (text2) is the shorter one
    n = len(text2)
    prev = [0] * (n + 1)
    for i in range(1, len(text1) + 1):
        curr = [0] * (n + 1)
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                curr[j] = prev[j - 1] + 1
            else:
                curr[j] = max(prev[j], curr[j - 1])
        prev = curr
    return prev[n]


def _test() -> None:
    cases = [
        (("abcde", "ace"), 3),      # "ace"
        (("abc", "abc"), 3),        # identical
        (("abc", "def"), 0),        # nothing in common
        (("", "abc"), 0),           # empty string
        (("bl", "yby"), 1),         # "b"
        (("ezupkr", "ubmrapg"), 2), # "up"
    ]
    for (a, b), expected in cases:
        assert longest_common_subsequence(a, b) == expected, (a, b)
        assert longest_common_subsequence_1d(a, b) == expected, (a, b)
    print("longest_common_subsequence: all cases passed")


if __name__ == "__main__":
    _test()
