"""125. Valid Palindrome — https://leetcode.com/problems/valid-palindrome/

Given a string, decide whether it reads the same forwards and backwards once you
keep only letters and digits (ignoring case and everything else).
"""
from typing import List


def is_palindrome_clean(s: str) -> bool:
    """Filter into a clean string, then compare it to its reverse. O(n) time, O(n) space.

    This is the honest first thought: "palindrome" means "equals its reverse", so
    strip the junk, lowercase, and test `t == t[::-1]`. It's correct and readable,
    but it allocates two whole new strings (the filtered copy and its reversed
    copy) just to answer a yes/no question — that's the waste we remove next.
    """
    kept = [c.lower() for c in s if c.isalnum()]
    return kept == kept[::-1]


def is_palindrome(s: str) -> bool:
    """Two pointers walking inward. O(n) time, O(1) extra space.

    Key insight: a palindrome is defined by a mirror relationship — the first
    kept character must equal the last, the second must equal the second-to-last,
    and so on. We don't need to build anything to check that; we can compare the
    two ends directly and step inward. A left pointer moves right, a right pointer
    moves left, each skipping non-alphanumeric characters, and we compare the
    lowercased characters where they land. If any mirrored pair disagrees, it's
    not a palindrome.
    """
    left, right = 0, len(s) - 1
    while left < right:
        # Skip anything that isn't a letter or digit.
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1
        if s[left].lower() != s[right].lower():
            return False
        left += 1
        right -= 1
    return True


def _test() -> None:
    cases = [
        ("A man, a plan, a canal: Panama", True),
        ("race a car", False),
        (" ", True),            # only spaces -> empty after filtering -> palindrome
        ("0P", False),          # '0' vs 'P': digit != letter (case-fold trap)
        ("ab_a", True),         # underscore is skipped, not a letter/digit
    ]
    for s, expected in cases:
        assert is_palindrome(s) == expected, s
        # the simple filtered version must agree on every case
        assert is_palindrome_clean(s) == expected, s
    print("is_palindrome: all cases passed")


if __name__ == "__main__":
    _test()
