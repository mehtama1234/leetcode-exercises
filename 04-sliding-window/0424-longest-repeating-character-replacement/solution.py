"""424. Longest Repeating Character Replacement — https://leetcode.com/problems/longest-repeating-character-replacement/

Given a string `s` and a budget `k`, you may change up to `k` characters to any
letters. Return the length of the longest run of the *same* letter you can make.

Two implementations are kept side by side so the reason the fast one exists is
visible: the brute force checks every substring, and the sliding window is what
you get by asking "when is a window still fixable, and how do I avoid re-counting
letters from scratch?".
"""
from typing import Dict, List


def character_replacement_brute(s: str, k: int) -> int:
    """Check every substring for fixability. O(n^2 * 26) time, O(1) space.

    For each start i and end j, count the letters in s[i..j]. The substring is
    achievable if the number of characters that are NOT the most common one is at
    most k — those are the ones we'd have to change. It's correct, but it re-scans
    and re-counts overlapping substrings endlessly; that's the waste we remove.
    """
    n = len(s)
    best = 0
    for i in range(n):
        counts: Dict[str, int] = {}
        max_freq = 0
        for j in range(i, n):
            counts[s[j]] = counts.get(s[j], 0) + 1
            max_freq = max(max_freq, counts[s[j]])
            window_len = j - i + 1
            if window_len - max_freq <= k:   # changes needed fit the budget
                best = max(best, window_len)
    return best


def character_replacement(s: str, k: int) -> int:
    """Grow a window; shrink only when it can't be fixed. O(n) time, O(1) space.

    Key insight: a window of length L can be turned into all-one-letter iff the
    letters we must change — everything except the most common letter — number at
    most k. That count is `L - max_freq`, where `max_freq` is the highest single
    letter count in the window. So:

      - extend `right`, updating counts and `max_freq`;
      - if `(window_len - max_freq) > k` the window is unfixable, so slide `left`
        forward by one (never more) to keep it valid.

    Because `left` only ever moves forward, both pointers cross the string once —
    O(n). We keep the best length ever reached. (We don't bother lowering
    `max_freq` when shrinking: the answer can only grow when `max_freq` grows, so
    a stale-but-not-too-high value never inflates the result.)
    """
    counts: Dict[str, int] = {}
    left = 0
    max_freq = 0
    best = 0
    for right, ch in enumerate(s):
        counts[ch] = counts.get(ch, 0) + 1
        max_freq = max(max_freq, counts[ch])
        window_len = right - left + 1
        if window_len - max_freq > k:        # too many changes needed: shrink
            counts[s[left]] -= 1
            left += 1
            window_len -= 1
        best = max(best, window_len)
    return best


def _test() -> None:
    cases = [
        (("ABAB", 2), 4),        # change both B's (or both A's) -> AAAA
        (("AABABBA", 1), 4),     # e.g. AABA A BBA -> window "ABBA"/"BBBB"
        (("AAAA", 0), 4),        # already all same, no changes needed
        (("ABCDE", 1), 2),       # best is any adjacent pair + 1 change
        (("A", 0), 1),           # single char
        (("", 2), 0),            # empty string
        (("BAAAB", 2), 5),       # change both B's -> AAAAA
    ]
    for (s, k), expected in cases:
        assert character_replacement(s, k) == expected, (s, k)
        # brute force must agree with the fast version on every case
        assert character_replacement_brute(s, k) == expected, (s, k)
    print("character_replacement: all cases passed")


if __name__ == "__main__":
    _test()
