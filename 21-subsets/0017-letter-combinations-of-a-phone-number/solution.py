"""17. Letter Combinations of a Phone Number —
https://leetcode.com/problems/letter-combinations-of-a-phone-number/

Given digits 2-9, return every string you can spell by choosing one letter per
digit from the old telephone keypad ("2"->abc, "3"->def, ...).

This is a Cartesian product built with backtracking: one decision per digit, and
the branches at each level are that digit's letters.
"""
from typing import List

KEYPAD = {
    "2": "abc", "3": "def", "4": "ghi", "5": "jkl",
    "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz",
}


def letter_combinations(digits: str) -> List[str]:
    """Backtracking over the digit positions. O(4^n * n) time.

    Depth of the tree = number of digits. At depth d we branch over the letters of
    digits[d] (up to 4 for 7 and 9). A leaf — path length equals the digit count —
    is one complete word. Same choose / explore / un-choose template as the
    numeric problems, but the choices at each level come from a lookup table
    instead of the input list.
    """
    if not digits:
        return []                       # LeetCode: empty input -> empty list, not [""]

    result: List[str] = []
    path: List[str] = []

    def backtrack(i: int) -> None:
        if i == len(digits):
            result.append("".join(path))    # copy via join
            return
        for letter in KEYPAD[digits[i]]:
            path.append(letter)         # choose
            backtrack(i + 1)            # explore the next digit
            path.pop()                  # un-choose

    backtrack(0)
    return result


def _test() -> None:
    from math import prod
    assert set(letter_combinations("23")) == {
        "ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf",
    }
    assert letter_combinations("") == []            # edge: empty input
    assert set(letter_combinations("2")) == {"a", "b", "c"}   # edge: one digit
    # size check: product of per-digit letter counts
    got = letter_combinations("79")                 # 4 * 4 = 16, both 4-letter keys
    assert len(got) == prod(len(KEYPAD[d]) for d in "79") == 16, len(got)
    assert len(set(got)) == len(got), "duplicates produced"
    print("letter_combinations: all cases passed")


if __name__ == "__main__":
    _test()
