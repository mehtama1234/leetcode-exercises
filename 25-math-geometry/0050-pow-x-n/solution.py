"""50. Pow(x, n) — https://leetcode.com/problems/powx-n/

Compute x raised to the power n (n can be negative). Return a float.

Two implementations are kept side by side so the reason the fast one exists is
visible: the naive loop multiplies n times, and fast exponentiation is what you
get by asking "which multiplications am I redoing?".
"""


def my_pow_naive(x: float, n: int) -> float:
    """Multiply x by itself |n| times. O(n) time, O(1) space.

    This is the definition of a power turned directly into code. It works, but
    for n = 2_000_000_000 it does two billion multiplications — far too slow.
    Negative n is handled by taking the power of 1/x.
    """
    if n < 0:
        x = 1 / x
        n = -n
    result = 1.0
    for _ in range(n):
        result *= x
    return result


def my_pow(x: float, n: int) -> float:
    """Exponentiation by squaring. O(log n) time, O(1) space.

    Key insight: x^n does not need n multiplications. If we already know
    x^(n/2), then x^n is just that value squared. So each step either squares
    what we have or, for odd exponents, squares and multiplies in one extra x.
    Reading the exponent's binary digits from low to high, we keep a running
    "current power of x" (x, x^2, x^4, x^8, ...) and fold it into the answer only
    where a 1-bit says that power is present.

    Negative n: x^(-n) = (1/x)^n, so flip x and make n positive up front. We
    convert n to a Python int of the same magnitude first; Python ints don't
    overflow, so -(-2^31) is safe here (the classic C pitfall does not bite).
    """
    if n < 0:
        x = 1 / x
        n = -n
    result = 1.0
    current = x  # current holds x^(2^bit) for the bit we are looking at
    while n > 0:
        if n & 1:            # this binary digit of the exponent is 1
            result *= current
        current *= current   # move to the next power of two: x^2, x^4, x^8...
        n >>= 1              # drop the digit we just consumed
    return result


def _test() -> None:
    cases = [
        ((2.0, 10), 1024.0),
        ((2.1, 3), 9.261000000000001),
        ((2.0, -2), 0.25),
        ((1.0, -2147483648), 1.0),   # huge negative exponent, still instant
        ((3.0, 0), 1.0),             # anything to the 0 is 1
        ((5.0, 1), 5.0),
    ]
    for (x, n), expected in cases:
        got = my_pow(x, n)
        assert abs(got - expected) < 1e-9, (x, n, got, expected)
    # naive must agree with the fast version on small exponents
    for (x, n), expected in [((2.0, 10), 1024.0), ((2.0, -2), 0.25), ((3.0, 0), 1.0)]:
        assert abs(my_pow_naive(x, n) - expected) < 1e-9, (x, n)
    print("my_pow: all cases passed")


if __name__ == "__main__":
    _test()
