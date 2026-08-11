"""20. Valid Parentheses — https://leetcode.com/problems/valid-parentheses/

Given a string of only the brackets ()[]{}, decide if every opening bracket is
closed by the matching kind, in the right order (properly nested).
"""
from typing import List


def is_valid(s: str) -> bool:
    """Stack, single pass. O(n) time, O(n) space.

    Key insight: the bracket that must close *next* is always the most recent one
    still open. "Most recent, first to resolve" is exactly a stack (LIFO). So we
    push every opener, and on each closer we check it against the top of the
    stack — the one thing that is allowed to close right now.

    We map each closer to the opener it requires. A closer is valid only if the
    stack is non-empty AND its top is that required opener; then we pop. Any
    mismatch (wrong kind, or nothing open at all) means the string is invalid.
    At the end the stack must be empty — a leftover opener was never closed.
    """
    pairs = {")": "(", "]": "[", "}": "{"}  # closer -> the opener it needs
    stack: List[str] = []
    for ch in s:
        if ch in pairs:  # ch is a closing bracket
            if not stack or stack.pop() != pairs[ch]:
                return False
        else:  # ch is an opening bracket
            stack.append(ch)
    return not stack  # nothing left open == balanced


def _test() -> None:
    cases = [
        ("()", True),
        ("()[]{}", True),
        ("(]", False),
        ("([)]", False),   # interleaved, not nested — order matters
        ("{[]}", True),
        ("", True),        # empty string is trivially balanced
        ("(", False),      # opener never closed -> stack not empty
        (")", False),      # closer with nothing open -> pop on empty
        ("((", False),
    ]
    for s, expected in cases:
        assert is_valid(s) == expected, s
    print("is_valid: all cases passed")


if __name__ == "__main__":
    _test()
