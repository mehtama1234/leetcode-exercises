"""3. Longest Substring Without Repeating Characters — https://leetcode.com/problems/longest-substring-without-repeating-characters/

Given a string `s`, return the length of the longest run of characters that
contains no repeated character.

Two implementations are kept side by side so the reason the fast one exists is
visible: the brute force checks every substring for uniqueness, and the sliding
window is what you get by asking "when I hit a repeat, how far do I actually have
to move to make the window clean again?".
"""
from typing import Dict, List


def length_of_longest_substring_brute(s: str) -> int:
    """Check every substring for all-unique. O(n^2) time (amortized), O(n) space.

    For each start i, extend j rightward adding characters to a set; the moment a
    character is already in the set, this window has a repeat, so stop and try the
    next start. Correct, but each new start rebuilds the set from scratch and
    re-walks characters it already examined — that redundant work is the waste.
    """
    n = len(s)
    best = 0
    for i in range(n):
        seen = set()
        for j in range(i, n):
            if s[j] in seen:
                break
            seen.add(s[j])
            best = max(best, j - i + 1)
    return best


def length_of_longest_substring(s: str) -> int:
    """Sliding window with last-seen index. O(n) time, O(min(n, alphabet)) space.

    Key insight: keep a window `s[left..right]` that is always repeat-free. When
    the new character at `right` was seen *inside the current window*, the window
    is only clean again once `left` jumps to just past that previous occurrence —
    we can skip straight there instead of inching forward. Store each character's
    last index in a dict so that jump is O(1). `left` only moves forward, so both
    pointers cross the string once — O(n).
    """
    last_seen: Dict[str, int] = {}   # character -> most recent index
    left = 0
    best = 0
    for right, ch in enumerate(s):
        prev = last_seen.get(ch)
        if prev is not None and prev >= left:
            left = prev + 1          # jump past the earlier copy, clean again
        last_seen[ch] = right
        best = max(best, right - left + 1)
    return best


def _test() -> None:
    cases = [
        ("abcabcbb", 3),   # "abc"
        ("bbbbb", 1),      # "b"
        ("pwwkew", 3),     # "wke" (note: "pwke" is a subsequence, not substring)
        ("", 0),           # empty
        ("au", 2),         # all unique
        ("dvdf", 3),       # "vdf" — left must jump past first d, not to start
        ("abba", 2),       # left must not move backward when 'a' repeats
        (" ", 1),          # single space counts as a character
    ]
    for s, expected in cases:
        assert length_of_longest_substring(s) == expected, repr(s)
        # brute force must agree with the fast version on every case
        assert length_of_longest_substring_brute(s) == expected, repr(s)
    print("length_of_longest_substring: all cases passed")


if __name__ == "__main__":
    _test()
