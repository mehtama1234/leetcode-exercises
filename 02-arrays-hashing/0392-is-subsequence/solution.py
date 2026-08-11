"""392. Is Subsequence — https://leetcode.com/problems/is-subsequence/

Given strings `s` and `t`, return True if `s` is a subsequence of `t` — i.e. you
can delete some (or no) characters of `t` and be left with exactly `s`, keeping
the remaining characters in order.

One clean two-pointer scan is the natural fit; deleting characters can't reorder
them, so a single left-to-right walk suffices.
"""


def is_subsequence(s: str, t: str) -> bool:
    """Two pointers, one pass over t. O(n) time, O(1) space.

    Key insight: a subsequence keeps order, so we never need to look backwards.
    Walk t once with a pointer `i` into s. Each time t's current character matches
    the next character s is waiting for, advance i. If i reaches the end of s,
    every character of s was found in order — success. If t runs out first, it
    couldn't supply them all.

    Greedy is safe here: matching s[i] against the *earliest* available character
    in t never hurts, because leaving that character unmatched can only shrink the
    remaining tail of t we have to work with.
    """
    i = 0  # index of the next character of s we still need to match
    for ch in t:
        if i < len(s) and ch == s[i]:
            i += 1
    return i == len(s)


def _test() -> None:
    cases = [
        (("abc", "ahbgdc"), True),
        (("axc", "ahbgdc"), False),
        (("", "ahbgdc"), True),    # empty s is a subsequence of anything
        (("", ""), True),
        (("a", ""), False),        # non-empty s cannot fit in empty t
        (("abc", "abc"), True),    # equal strings
        (("aaaa", "aa"), False),   # need more of a letter than t has
    ]
    for (s, t), expected in cases:
        assert is_subsequence(s, t) == expected, (s, t)
    print("is_subsequence: all cases passed")


if __name__ == "__main__":
    _test()
