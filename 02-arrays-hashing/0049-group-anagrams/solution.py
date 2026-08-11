"""49. Group Anagrams — https://leetcode.com/problems/group-anagrams/

Given a list of strings, group together the ones that are anagrams of each other
(same letters, any order). Return the groups in any order.

The whole problem is choosing a *key* that is identical for anagrams and
different for everything else, so a dict can bucket them in one pass.
"""
from typing import Dict, List, Tuple


def group_anagrams_sortkey(strs: List[str]) -> List[List[str]]:
    """Key each word by its sorted letters. O(n * k log k) time.

    Two words are anagrams exactly when their sorted letters are equal, so the
    sorted string is a canonical name shared by a whole anagram family. Bucket by
    that name. Simple, but sorting each word costs a k log k factor.
    """
    buckets: Dict[str, List[str]] = {}
    for word in strs:
        key = "".join(sorted(word))
        buckets.setdefault(key, []).append(word)
    return list(buckets.values())


def group_anagrams(strs: List[str]) -> List[List[str]]:
    """Key each word by its 26-letter count signature. O(n * k) time.

    Key insight (from Valid Anagram): anagrams share the same letter counts, so
    the tuple of 26 counts is already a canonical name — no sorting needed. Build
    that count vector per word and use it as the dict key.
    """
    buckets: Dict[Tuple[int, ...], List[str]] = {}
    for word in strs:
        counts = [0] * 26  # assumes lowercase a-z, per the problem constraints
        for ch in word:
            counts[ord(ch) - ord("a")] += 1
        buckets.setdefault(tuple(counts), []).append(word)
    return list(buckets.values())


def _normalize(groups: List[List[str]]) -> List[List[str]]:
    """Sort within and across groups so results compare regardless of order."""
    return sorted(sorted(g) for g in groups)


def _test() -> None:
    cases = [
        (["eat", "tea", "tan", "ate", "nat", "bat"],
         [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]]),
        ([""], [[""]]),          # single empty string is its own group
        (["a"], [["a"]]),        # single letter
        (["abc", "bca", "xyz"], [["abc", "bca"], ["xyz"]]),
    ]
    for strs, expected in cases:
        assert _normalize(group_anagrams(strs)) == _normalize(expected), strs
        assert _normalize(group_anagrams_sortkey(strs)) == _normalize(expected), strs
    print("group_anagrams: all cases passed")


if __name__ == "__main__":
    _test()
