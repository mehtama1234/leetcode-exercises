"""43. Multiply Strings — https://leetcode.com/problems/multiply-strings/

Two non-negative integers are given as strings. Return their product as a
string. No converting to int and multiplying — do the grade-school algorithm
by hand so it works for numbers far larger than a machine word.
"""


def multiply(num1: str, num2: str) -> str:
    """Grade-school long multiplication on digit arrays. O(m*n) time.

    The key fact that makes this clean: the digit at position i of num1 times
    the digit at position j of num2 contributes to the product's place value
    (i + j) from the right — a partial product of at most two digits. So we
    allocate an array of size m + n (the most places the product can have),
    accumulate every digit-by-digit product into position (i + j), and let the
    carries settle at the end.

    Concretely, using indices counted from the *right*: multiplying the units
    digit of one number by the units digit of the other lands in the units place
    (0 + 0); tens-by-units lands in the tens place (1 + 0); and so on — exactly
    the place-shifting you do when you stack numbers on paper.
    """
    if num1 == "0" or num2 == "0":
        return "0"

    m, n = len(num1), len(num2)
    # result[k] holds the running total for the k-th place counted from the RIGHT.
    # A product of an m-digit and an n-digit number has at most m + n digits.
    result = [0] * (m + n)

    for i in range(m - 1, -1, -1):
        d1 = ord(num1[i]) - ord("0")
        for j in range(n - 1, -1, -1):
            d2 = ord(num2[j]) - ord("0")
            # place from the right for this partial product
            low = (m - 1 - i) + (n - 1 - j)
            result[low] += d1 * d2  # accumulate; we normalize carries below

    # Resolve carries: each slot keeps its ones digit, the rest carries left.
    carry = 0
    for k in range(m + n):
        total = result[k] + carry
        result[k] = total % 10
        carry = total // 10

    # result is little-endian (place 0 = units); build the string big-endian,
    # dropping leading zeros in the high places.
    digits = result[::-1]
    start = 0
    while start < len(digits) - 1 and digits[start] == 0:
        start += 1
    return "".join(str(d) for d in digits[start:])


def _test() -> None:
    cases = [
        (("2", "3"), "6"),
        (("123", "456"), "56088"),
        (("0", "52"), "0"),
        (("9", "99"), "891"),
        (("999", "999"), "998001"),
        # far beyond a 64-bit int — this is the whole point of doing it by hand
        (("123456789", "987654321"), "121932631112635269"),
    ]
    for (a, b), expected in cases:
        got = multiply(a, b)
        assert got == expected, (a, b, got, expected)
        # cross-check against Python's own big-int multiply
        assert got == str(int(a) * int(b)), (a, b)
    print("multiply: all cases passed")


if __name__ == "__main__":
    _test()
