"""72. Edit Distance — https://leetcode.com/problems/edit-distance/

Find the minimum number of single-character edits (insert, delete, replace) that
turn word1 into word2.

Shown: the memoized recurrence on (i, j) = prefixes still to reconcile, then the
1-D rolled tabulation.
"""
from functools import lru_cache


def min_distance_memo(word1: str, word2: str) -> int:
    """Top-down on (i, j) = edits to turn word1[:i] into word2[:j]. O(m*n) states.

    Look at the last characters. If they match, they cost nothing and we recurse on
    the shorter prefixes. If they differ, we pay 1 and pick the cheapest of the
    three edits, each of which shrinks the problem by one character on one side:
      replace -> (i-1, j-1)   delete from word1 -> (i-1, j)   insert into word1 -> (i, j-1)
    """
    m, n = len(word1), len(word2)

    @lru_cache(maxsize=None)
    def dist(i: int, j: int) -> int:
        if i == 0:
            return j            # insert the remaining j chars of word2
        if j == 0:
            return i            # delete the remaining i chars of word1
        if word1[i - 1] == word2[j - 1]:
            return dist(i - 1, j - 1)
        return 1 + min(
            dist(i - 1, j - 1),   # replace
            dist(i - 1, j),       # delete from word1
            dist(i, j - 1),       # insert into word1
        )

    result = dist(m, n)
    dist.cache_clear()
    return result


def min_distance(word1: str, word2: str) -> int:
    """Bottom-up, rolled to one row over word2. O(m*n) time, O(n) space.

    dp[j] = edit distance between the current prefix of word1 and word2[:j].
    Filling row i, we need three neighbours: dp[j] (the cell directly above,
    i.e. delete), dp[j-1] just written (insert), and the OLD dp[j-1] from the row
    above (replace) — we stash that in `diag` before overwriting.
    """
    m, n = len(word1), len(word2)
    dp = list(range(n + 1))          # row 0: turn "" into word2[:j] by j inserts
    for i in range(1, m + 1):
        diag = dp[0]                 # old dp[i-1][0]
        dp[0] = i                    # turn word1[:i] into "" by i deletes
        for j in range(1, n + 1):
            old = dp[j]              # this is dp[i-1][j] before overwrite
            if word1[i - 1] == word2[j - 1]:
                dp[j] = diag
            else:
                dp[j] = 1 + min(diag, dp[j - 1], old)  # replace, insert, delete
            diag = old               # becomes dp[i-1][j] for next column's replace
    return dp[n]


def _test() -> None:
    cases = [
        (("horse", "ros"), 3),
        (("intention", "execution"), 5),
        (("", ""), 0),
        (("abc", ""), 3),
        (("", "abc"), 3),
        (("abc", "abc"), 0),
        (("a", "b"), 1),
        (("kitten", "sitting"), 3),
    ]
    for (w1, w2), expected in cases:
        assert min_distance(w1, w2) == expected, (w1, w2)
        assert min_distance_memo(w1, w2) == expected, (w1, w2)
    print("edit_distance: all cases passed")


if __name__ == "__main__":
    _test()
