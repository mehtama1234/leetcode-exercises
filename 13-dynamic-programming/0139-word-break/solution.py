"""139. Word Break — https://leetcode.com/problems/word-break/

Given a string `s` and a dictionary of words, decide whether `s` can be split
into a sequence of one or more dictionary words (each word reusable).

Two implementations are kept side by side so the reason the fast one exists is
visible: the memoized recursion is the honest top-down statement, and the
bottom-up table is the same recurrence filled from the end of the string.
"""
from typing import List, Dict, Set


def word_break_memo(s: str, wordDict: List[str]) -> bool:
    """Top-down recursion with memoization. O(n^2 * L) time.

    The recurrence: from position `i`, the rest `s[i:]` is breakable iff some
    dictionary word matches starting at `i` and the remainder after it is also
    breakable. That remainder is an identical subproblem keyed only by its start
    index. Without a cache, the same suffix gets re-solved along many prefix
    choices — that repetition is the waste. `cache[i]` remembers each suffix once.
    """
    words: Set[str] = set(wordDict)
    n = len(s)
    cache: Dict[int, bool] = {}

    def breakable(i: int) -> bool:
        if i == n:
            return True  # consumed the whole string successfully
        if i in cache:
            return cache[i]
        ok = False
        for j in range(i + 1, n + 1):
            if s[i:j] in words and breakable(j):
                ok = True
                break
        cache[i] = ok
        return ok

    return breakable(0)


def word_break(s: str, wordDict: List[str]) -> bool:
    """Bottom-up table. O(n^2 * L) time, O(n) space.

    Same recurrence, filled from the end so every suffix it needs is already
    solved. dp[i] = "can s[i:] be broken into dictionary words?" Base case
    dp[n] = True (the empty suffix is trivially broken). For each i going
    backward, dp[i] is True if some word matches at i and dp after that word is
    True. The answer is dp[0].
    """
    words: Set[str] = set(wordDict)
    n = len(s)
    dp = [False] * (n + 1)
    dp[n] = True  # empty suffix
    for i in range(n - 1, -1, -1):
        for j in range(i + 1, n + 1):
            if s[i:j] in words and dp[j]:
                dp[i] = True
                break
    return dp[0]


def _test() -> None:
    cases = [
        (("leetcode", ["leet", "code"]), True),
        (("applepenapple", ["apple", "pen"]), True),   # reuse "apple"
        (("catsandog", ["cats", "dog", "sand", "and", "cat"]), False),
        (("a", ["a"]), True),                            # single char, present
        (("a", ["b"]), False),                           # single char, absent
        (("aaaaaaa", ["aaaa", "aaa"]), True),            # 3 + 4
    ]
    for (s, wordDict), expected in cases:
        assert word_break(s, wordDict) == expected, (s, wordDict)
        # the top-down version must agree with the table on every case
        assert word_break_memo(s, wordDict) == expected, (s, wordDict)
    print("word_break: all cases passed")


if __name__ == "__main__":
    _test()
