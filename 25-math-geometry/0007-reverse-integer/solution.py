"""7. Reverse Integer — https://leetcode.com/problems/reverse-integer/

Reverse the digits of a signed 32-bit integer. If the reversed value would fall
outside the signed 32-bit range, return 0.

One clean function is enough: the whole difficulty is peeling digits off and
detecting overflow *before* it happens, since the reversed number can exceed
the 32-bit range even when the input didn't.
"""

INT_MAX = 2**31 - 1   #  2147483647
INT_MIN = -(2**31)    # -2147483648


def reverse(x: int) -> int:
    """Reverse digits with an overflow guard. O(d) time, O(1) space, d = #digits.

    Build the reversed number one digit at a time: pop the last digit of x with
    divmod by 10, and push it onto `result` as result*10 + digit.

    The real problem is the 32-bit limit. The reversed value can overflow even
    when x fits: reversing 1_000_000_003 gives 3_000_000_001, past INT_MAX. We
    check *before* multiplying: if result is already past INT_MAX // 10 (or would
    tie it with a digit that pushes over), the next result*10 + digit would
    overflow, so we bail with 0.

    We reduce to the non-negative case first and reapply the sign at the end, so
    the digit math is uniform. Python ints don't actually overflow, but the point
    of the exercise is to emulate a fixed-width machine, so we enforce the bound
    by hand.
    """
    sign = -1 if x < 0 else 1
    x = abs(x)
    result = 0
    while x != 0:
        x, digit = divmod(x, 10)  # peel the last digit
        # Would result * 10 + digit exceed INT_MAX (2147483647)?
        # Its last digit is 7, so a tie at INT_MAX // 10 (== 214748364) with
        # digit > 7 also overflows. We treat the signed magnitude uniformly:
        # the max magnitude is 2**31 for negatives, 2**31 - 1 for positives.
        limit = 2**31 if sign == -1 else INT_MAX
        if result > limit // 10 or (result == limit // 10 and digit > limit % 10):
            return 0
        result = result * 10 + digit
    return sign * result


def _test() -> None:
    cases = [
        (123, 321),
        (-123, -321),
        (120, 21),               # trailing zero disappears
        (0, 0),
        (1534236469, 0),         # reversed 9646324351 overflows -> 0
        (-2147483648, 0),        # reversed 8463847412 overflows -> 0
        (2147483647, 0),         # reversed 7463847412 overflows -> 0
        (1463847412, 2147483641),# reverses to exactly within range
        (-100, -1),
    ]
    for x, expected in cases:
        got = reverse(x)
        assert got == expected, (x, got, expected)
        # every returned value must itself be within the 32-bit range
        assert INT_MIN <= got <= INT_MAX, (x, got)
    print("reverse: all cases passed")


if __name__ == "__main__":
    _test()
