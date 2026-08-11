"""242. Valid Anagram — https://leetcode.com/problems/valid-anagram/

Given two strings `s` and `t`, return True if `t` is an anagram of `s` — that
is, they use exactly the same letters the same number of times.

Two implementations are kept side by side: sorting is the obvious first thought,
and the count map is what you get by asking "what does sorting compute that I
don't need?".
"""
from typing import Dict


def is_anagram_sort(s: str, t: str) -> bool:
    """Sort both strings and compare. O(n log n) time, O(n) space.

    An anagram is the same multiset of letters. Sorting forces both strings into
    one canonical order, so two anagrams become the identical string. Correct and
    short, but it pays a log-n factor to fully order the letters when all we care
    about is how many of each there are.
    """
    return sorted(s) == sorted(t)


def is_anagram(s: str, t: str) -> bool:
    """Count letters with a hash map. O(n) time, O(1) space.

    Key insight: two strings are anagrams exactly when every letter's count
    matches. So tally s's letters (+1) and t's letters (-1) in one map; if they
    are anagrams every count cancels back to zero. Different lengths can't match,
    so we reject those up front.
    """
    if len(s) != len(t):
        return False
    counts: Dict[str, int] = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    for ch in t:
        counts[ch] = counts.get(ch, 0) - 1
        if counts[ch] < 0:  # t has a letter s never had enough of
            return False
    return all(v == 0 for v in counts.values())


def _test() -> None:
    cases = [
        (("anagram", "nagaram"), True),
        (("rat", "car"), False),
        (("", ""), True),            # two empty strings are trivially anagrams
        (("a", "ab"), False),        # length differs
        (("aacc", "ccac"), False),   # same letters, wrong counts
    ]
    for (s, t), expected in cases:
        assert is_anagram(s, t) == expected, (s, t)
        assert is_anagram_sort(s, t) == expected, (s, t)
    print("is_anagram: all cases passed")


if __name__ == "__main__":
    _test()
