"""115. Distinct Subsequences — https://leetcode.com/problems/distinct-subsequences/

Count how many distinct ways `t` appears as a subsequence of `s` — i.e. how many
ways to delete some characters of `s` (keeping order) so that what's left is exactly
`t`.

Shown: the memoized recurrence on (i, j) = suffixes of s and t left to match, then
the 1-D rolled tabulation.
"""
from functools import lru_cache


def num_distinct_memo(s: str, t: str) -> int:
    """Top-down on (i, j) = we still must match t[j:] inside s[i:]. O(m*n) states.

    At each s-character we make a choice: if it equals the current t-character we
    may *use* it (advance both pointers) — but we may also *skip* it and hope a
    later s-character matches instead. Summing "use" + "skip" is what counts every
    distinct alignment separately.
    """
    m, n = len(s), len(t)

    @lru_cache(maxsize=None)
    def count(i: int, j: int) -> int:
        if j == n:
            return 1                 # matched all of t: one complete way
        if i == m:
            return 0                 # s exhausted, t left over: dead end
        skip = count(i + 1, j)       # don't use s[i]
        use = count(i + 1, j + 1) if s[i] == t[j] else 0
        return skip + use

    result = count(0, 0)
    count.cache_clear()
    return result


def num_distinct(s: str, t: str) -> int:
    """Bottom-up, rolled to one row over t. O(m*n) time, O(n) space.

    dp[j] = number of ways t[:j] appears in the prefix of s processed so far.
    For each new s-character c, update j from HIGH to LOW so dp[j-1] still refers
    to the count *before* this character was considered:
        if c == t[j-1]:  dp[j] += dp[j-1]
    dp[0] stays 1: the empty target matches any prefix exactly one way.
    """
    m, n = len(s), len(t)
    dp = [0] * (n + 1)
    dp[0] = 1                        # empty t: one subsequence (delete everything)
    for c in s:
        for j in range(n, 0, -1):    # high->low: dp[j-1] is the pre-c count
            if c == t[j - 1]:
                dp[j] += dp[j - 1]
    return dp[n]


def _test() -> None:
    cases = [
        (("rabbbit", "rabbit"), 3),
        (("babgbag", "bag"), 5),
        (("", ""), 1),
        (("abc", ""), 1),
        (("", "a"), 0),
        (("aaa", "aa"), 3),
        (("abc", "abcd"), 0),   # t longer than s
    ]
    for (s, t), expected in cases:
        assert num_distinct(s, t) == expected, (s, t)
        assert num_distinct_memo(s, t) == expected, (s, t)
    print("distinct_subsequences: all cases passed")


if __name__ == "__main__":
    _test()
