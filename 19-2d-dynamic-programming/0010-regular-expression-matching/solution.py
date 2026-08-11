"""10. Regular Expression Matching —
https://leetcode.com/problems/regular-expression-matching/

Match string `s` against pattern `p`, where `.` matches any single character and
`*` matches zero or more of the character immediately before it. The match must
cover the ENTIRE string.

Shown: the memoized recurrence on (i, j) = suffixes still to match, then the 2-D
bottom-up tabulation.
"""
from functools import lru_cache


def is_match_memo(s: str, p: str) -> bool:
    """Top-down on (i, j) = does s[i:] match p[j:]? O(m*n) states.

    Compare the front of each suffix. A single char (letter or '.') must match and
    then both advance. The only real branch is '*': the pattern piece `x*` can be
    used ZERO times (skip the pair `x*` in the pattern) or, if `x` matches s[i],
    used one MORE time (consume s[i], keep the `x*` for possible reuse). Summing
    these two options with OR is the whole algorithm.
    """
    m, n = len(s), len(p)

    @lru_cache(maxsize=None)
    def match(i: int, j: int) -> bool:
        if j == n:
            return i == m               # pattern used up: match iff s is too
        first = i < m and (p[j] == s[i] or p[j] == ".")
        if j + 1 < n and p[j + 1] == "*":
            # zero copies: skip 'x*'  OR  one+ copy: consume s[i], keep 'x*'
            return match(i, j + 2) or (first and match(i + 1, j))
        return first and match(i + 1, j + 1)

    result = match(0, 0)
    match.cache_clear()
    return result


def is_match(s: str, p: str) -> bool:
    """Bottom-up 2-D table. O(m*n) time, O(m*n) space.

    dp[i][j] = does s[i:] match p[j:]. Fill from the bottom-right (empty suffixes)
    back to (0, 0), mirroring the recurrence: dp[m][n] = True, and each cell reads
    dp[i][j+2] (skip x*), dp[i+1][j] (consume via x*), or dp[i+1][j+1] (plain char).
    """
    m, n = len(s), len(p)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[m][n] = True                     # empty string matches empty pattern

    for i in range(m, -1, -1):
        for j in range(n - 1, -1, -1):
            first = i < m and (p[j] == s[i] or p[j] == ".")
            if j + 1 < n and p[j + 1] == "*":
                dp[i][j] = dp[i][j + 2] or (first and dp[i + 1][j])
            else:
                dp[i][j] = first and dp[i + 1][j + 1]
    return dp[0][0]


def _test() -> None:
    cases = [
        (("aa", "a"), False),
        (("aa", "a*"), True),
        (("ab", ".*"), True),
        (("aab", "c*a*b"), True),
        (("mississippi", "mis*is*p*."), False),
        (("", ""), True),
        (("", "a*"), True),
        (("", ".*"), True),
        (("abc", ""), False),
        (("a", ".*..a*"), False),
        (("aaa", "a*a"), True),
        (("aaa", "ab*a*c*a"), True),
    ]
    for (s, p), expected in cases:
        assert is_match(s, p) == expected, (s, p)
        assert is_match_memo(s, p) == expected, (s, p)
    print("regular_expression_matching: all cases passed")


if __name__ == "__main__":
    _test()
