"""97. Interleaving String — https://leetcode.com/problems/interleaving-string/

Given strings s1, s2, s3, decide whether s3 can be formed by interleaving s1 and
s2 — keeping the internal order of each, but freely alternating which one you draw
the next character from.

Shown: the memoized recurrence on (i, j) = how much of s1 and s2 is used, then the
1-D rolled tabulation.
"""
from functools import lru_cache


def is_interleave_memo(s1: str, s2: str, s3: str) -> bool:
    """Top-down on (i, j). O(m*n) states, O(m*n) time and space.

    State (i, j) means we've consumed s1[:i] and s2[:j]; since every character of
    s3 must come from one of them, we've necessarily filled s3[:i+j]. The next s3
    char is s3[i+j]; it must be matched by advancing whichever string offers it.
    The third pointer is *derived* (k = i + j), which is why two dimensions suffice.
    """
    m, n = len(s1), len(s2)
    if m + n != len(s3):
        return False

    @lru_cache(maxsize=None)
    def solve(i: int, j: int) -> bool:
        if i == m and j == n:
            return True
        k = i + j
        take1 = i < m and s1[i] == s3[k] and solve(i + 1, j)
        take2 = j < n and s2[j] == s3[k] and solve(i, j + 1)
        return take1 or take2

    result = solve(0, 0)
    solve.cache_clear()
    return result


def is_interleave(s1: str, s2: str, s3: str) -> bool:
    """Bottom-up, rolled to a single row. O(m*n) time, O(n) space.

    dp[j] = can s1[:i] and s2[:j] interleave to s3[:i+j], for the current i.
    Sweeping i as the outer loop lets each row overwrite the previous one: the
    "came from s1" term reads the same j in the old row (dp[j]); the "came from
    s2" term reads dp[j-1] in the row we're building.
    """
    m, n = len(s1), len(s2)
    if m + n != len(s3):
        return False

    dp = [False] * (n + 1)
    dp[0] = True                                    # empty + empty makes empty
    for j in range(1, n + 1):                       # first row: only s2 used
        dp[j] = dp[j - 1] and s2[j - 1] == s3[j - 1]

    for i in range(1, m + 1):
        # j == 0 column: only s1 used so far
        dp[0] = dp[0] and s1[i - 1] == s3[i - 1]
        for j in range(1, n + 1):
            from_s1 = dp[j] and s1[i - 1] == s3[i + j - 1]      # old row, same j
            from_s2 = dp[j - 1] and s2[j - 1] == s3[i + j - 1]  # new row, j-1
            dp[j] = from_s1 or from_s2
    return dp[n]


def _test() -> None:
    cases = [
        (("aabcc", "dbbca", "aadbbcbcac"), True),
        (("aabcc", "dbbca", "aadbbbaccc"), False),
        (("", "", ""), True),
        (("", "abc", "abc"), True),
        (("abc", "", "abc"), True),
        (("a", "b", "ab"), True),
        (("a", "b", "ba"), True),
        (("aa", "ab", "aaba"), True),
        (("ab", "cd", "abdc"), False),   # right length, order impossible
    ]
    for (s1, s2, s3), expected in cases:
        assert is_interleave(s1, s2, s3) == expected, (s1, s2, s3)
        assert is_interleave_memo(s1, s2, s3) == expected, (s1, s2, s3)
    print("interleaving_string: all cases passed")


if __name__ == "__main__":
    _test()
