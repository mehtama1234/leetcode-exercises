"""131. Palindrome Partitioning —
https://leetcode.com/problems/palindrome-partitioning/

Cut a string into pieces so that every piece is a palindrome, and return all such
cuttings. E.g. "aab" -> [["a","a","b"], ["aa","b"]].

The decision at each step is "where does the next piece end?". We only take a
prefix that is itself a palindrome — that's the prune that keeps the search honest.
"""
from typing import List


def is_palindrome(s: str, lo: int, hi: int) -> bool:
    """True if s[lo..hi] reads the same both ways. Two-pointer, O(len) time."""
    while lo < hi:
        if s[lo] != s[hi]:
            return False
        lo += 1
        hi -= 1
    return True


def partition(s: str) -> List[List[str]]:
    """Backtracking over cut positions, pruned to palindromic prefixes. O(n * 2^n).

    Think of the n-1 gaps between characters: a partition is a choice of which gaps
    to cut. That's 2^(n-1) raw partitions. The prune: from position `start`, only
    extend to an `end` where s[start..end] is a palindrome — any other prefix can
    never be part of a valid answer, so we don't recurse into it. Standard choose /
    explore / un-choose, with the palindrome test gating the "choose".
    """
    n = len(s)
    result: List[List[str]] = []
    path: List[str] = []

    def backtrack(start: int) -> None:
        if start == n:
            result.append(path[:])          # reached the end: a full partition
            return
        for end in range(start, n):
            if is_palindrome(s, start, end):    # prune: only palindromic prefixes
                path.append(s[start:end + 1])   # choose this piece
                backtrack(end + 1)              # explore the remaining suffix
                path.pop()                      # un-choose

    backtrack(0)
    return result


def _key(lists: List[List[str]]) -> set:
    """Order-independent key: partitions keep internal order (the cut sequence),
    so tuple each partition but treat the outer collection as a set."""
    return {tuple(p) for p in lists}


def _test() -> None:
    assert _key(partition("aab")) == _key([["a", "a", "b"], ["aa", "b"]])
    assert _key(partition("a")) == _key([["a"]])            # edge: single char
    assert _key(partition("")) == _key([[]])                # edge: empty -> one empty partition
    # "aaa": every partition works because all pieces are palindromes -> 2^(3-1)=4
    assert _key(partition("aaa")) == _key([
        ["a", "a", "a"], ["a", "aa"], ["aa", "a"], ["aaa"],
    ])
    assert len(partition("aaa")) == 4, "expected 2^(n-1) partitions for all-equal"
    print("partition: all cases passed")


if __name__ == "__main__":
    _test()
