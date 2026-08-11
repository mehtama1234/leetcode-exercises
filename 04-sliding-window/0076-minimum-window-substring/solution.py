"""76. Minimum Window Substring — https://leetcode.com/problems/minimum-window-substring/

Given strings `s` and `t`, return the shortest substring of `s` that contains
every character of `t` (counting duplicates). If no such window exists, return "".

Two implementations are kept side by side so the reason the fast one exists is
visible: the brute force checks every substring, and the sliding window is what
you get by asking "instead of re-checking coverage from scratch, can I grow until
covered and then shrink while still covered?".
"""
from typing import Dict


def min_window_brute(s: str, t: str) -> str:
    """Check every substring for coverage. O(n^2 * (n + m)) time, O(m) space.

    For each start i and end j, count s[i..j] and test whether it contains every
    character of t with the required multiplicity. Correct, but it re-counts
    overlapping substrings over and over — that redundancy is the waste we remove.
    """
    if not t or not s:
        return ""
    need: Dict[str, int] = {}
    for ch in t:
        need[ch] = need.get(ch, 0) + 1

    def covers(sub: str) -> bool:
        have: Dict[str, int] = {}
        for ch in sub:
            have[ch] = have.get(ch, 0) + 1
        return all(have.get(ch, 0) >= cnt for ch, cnt in need.items())

    n = len(s)
    best = ""
    for i in range(n):
        for j in range(i + 1, n + 1):
            if covers(s[i:j]):
                if best == "" or (j - i) < len(best):
                    best = s[i:j]
                break   # shortest window starting at i found; longer j only grows
    return best


def min_window(s: str, t: str) -> str:
    """Grow to cover, then shrink while still covered. O(n + m) time, O(m) space.

    Key insight: run a window with two moves.

      - Expand `right`, pulling characters in. Track how many of t's *required*
        character slots are currently satisfied via a single counter `formed`.
      - The moment every requirement is met (`formed == required`), the window is
        valid — now shrink from the left as far as possible while it stays valid,
        recording the smallest valid window seen.

    `need` holds the target counts; `window` holds current counts. `formed` counts
    how many distinct characters have reached their required count, so we know
    "fully covered?" in O(1) instead of re-scanning. Both pointers move forward
    only, so the scan is O(n + m).
    """
    if not s or not t:
        return ""

    need: Dict[str, int] = {}
    for ch in t:
        need[ch] = need.get(ch, 0) + 1
    required = len(need)          # number of distinct chars we must satisfy

    window: Dict[str, int] = {}
    formed = 0                    # how many distinct chars are fully satisfied
    left = 0
    best_len = float("inf")
    best_start = 0

    for right, ch in enumerate(s):
        window[ch] = window.get(ch, 0) + 1
        if ch in need and window[ch] == need[ch]:
            formed += 1

        # window is valid: shrink from the left as much as still-valid allows
        while formed == required:
            if right - left + 1 < best_len:
                best_len = right - left + 1
                best_start = left
            left_ch = s[left]
            window[left_ch] -= 1
            if left_ch in need and window[left_ch] < need[left_ch]:
                formed -= 1       # dropping this char broke coverage; stop shrinking
            left += 1

    return "" if best_len == float("inf") else s[best_start:best_start + best_len]


def _test() -> None:
    cases = [
        (("ADOBECODEBANC", "ABC"), "BANC"),
        (("a", "a"), "a"),
        (("a", "aa"), ""),            # need two a's, only one available
        (("", "a"), ""),              # empty source
        (("a", ""), ""),              # empty target
        (("aa", "aa"), "aa"),         # duplicates required
        (("bba", "ab"), "ba"),        # shortest is at the end
        (("ADOBECODEBANC", "ABCD"), "ADOBEC"),
    ]
    for (s, t), expected in cases:
        assert min_window(s, t) == expected, (s, t)
        # brute force must agree with the fast version on every case
        assert min_window_brute(s, t) == expected, (s, t)
    print("min_window: all cases passed")


if __name__ == "__main__":
    _test()
