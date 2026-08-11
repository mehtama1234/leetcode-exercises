"""9. Palindrome Number — https://leetcode.com/problems/palindrome-number/

Return whether a signed integer reads the same forwards and backwards, without
converting it to a string.

Two implementations are kept side by side so the reason the better one exists is
visible: reversing the whole number is the obvious idea, and reversing only
*half* is what you get by asking "how do I avoid overflow and stop early?".
"""


def is_palindrome_full_reverse(x: int) -> bool:
    """Reverse the whole number and compare. O(d) time, O(1) space.

    Negatives are never palindromes (the '-' has no matching digit at the end).
    We rebuild the reversed integer digit by digit and check equality. Simple,
    but the reversed value can overflow a fixed-width int even when x doesn't —
    which is exactly what the half-reversal below avoids.
    """
    if x < 0:
        return False
    original, reversed_num = x, 0
    while x > 0:
        x, digit = divmod(x, 10)
        reversed_num = reversed_num * 10 + digit
    return original == reversed_num


def is_palindrome(x: int) -> bool:
    """Reverse only the second half, then compare against the first. O(d) time.

    Key insight: to test a palindrome we don't need the whole reversed number —
    we can build up the reversed *back half* while chopping digits off the
    front, and stop when the remaining front is <= the reversed back. At that
    point they've met in the middle.

      - x != reversed and x > reversed keeps looping: pull one digit off x's end
        onto `reversed`.
      - When x <= reversed we've crossed the midpoint.
      - Even length (1221): x == reversed (12 == 12).
      - Odd length (12321): the middle digit sits alone, so drop it with
        reversed // 10 (x == 121//10 == 12).

    This never builds a number larger than half the digits, so it can't overflow
    the way a full reversal can — the reason to prefer it in a fixed-width world.
    """
    # Negative, or ends in 0 but isn't 0 itself (e.g. 10, 120): not a palindrome.
    if x < 0 or (x % 10 == 0 and x != 0):
        return False
    reversed_half = 0
    while x > reversed_half:
        x, digit = divmod(x, 10)
        reversed_half = reversed_half * 10 + digit
    # Even count: x == reversed_half. Odd count: drop the middle via // 10.
    return x == reversed_half or x == reversed_half // 10


def _test() -> None:
    cases = [
        (121, True),
        (-121, False),   # negative sign breaks symmetry
        (10, False),     # reversed would be 01 -> 1, not equal
        (0, True),
        (1221, True),    # even length
        (12321, True),   # odd length
        (12345, False),
        (1000021, False),
    ]
    for x, expected in cases:
        assert is_palindrome(x) == expected, (x, expected)
        assert is_palindrome_full_reverse(x) == expected, (x, expected)  # agree
    print("is_palindrome: all cases passed")


if __name__ == "__main__":
    _test()
