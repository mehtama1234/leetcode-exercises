"""371. Sum of Two Integers — https://leetcode.com/problems/sum-of-two-integers/

Return a + b without using the `+` or `-` operators. Inputs can be negative, and
we treat them as 32-bit signed integers (two's complement).
"""


def get_sum(a: int, b: int) -> int:
    """Add with XOR (sum-without-carry) and AND<<1 (the carry), looping.

    Binary addition of two bits splits cleanly:
      - XOR gives the sum ignoring carry:   1^1=0, 1^0=1, 0^0=0
      - AND gives where a carry is produced: 1&1=1, else 0
        and a carry belongs one column to the LEFT, so shift it left by 1.

    Repeat "add the carry-free sum to the shifted carry" until there's no carry
    left. Worked column example, 3 + 5:

        a = 011 (3), b = 101 (5)
        pass 1: sum = 011 ^ 101 = 110       carry = (011 & 101) << 1 = 001 << 1 = 010
        pass 2: a=110, b=010: sum = 100     carry = (110 & 010) << 1 = 010 << 1 = 100
        pass 3: a=100, b=100: sum = 000     carry = (100 & 100) << 1 = 100 << 1 = 1000
        pass 4: a=000, b=1000: sum = 1000   carry = 0  -> done, answer 1000 = 8

    The 32-bit masking is the subtle part. Python ints are unbounded, so the
    carry could shift off past bit 31 forever and the loop would never end. We
    force fixed-width behavior:
      - MASK = 0xFFFFFFFF keeps only the low 32 bits after every step, mimicking a
        32-bit register that discards overflow.
      - When the loop finishes, `a` holds a 32-bit two's-complement pattern. If
        its sign bit (bit 31) is set, the true value is negative, so we convert
        that pattern back to a Python negative int with `~(a ^ MASK)`.
    """
    MASK = 0xFFFFFFFF          # low 32 bits
    INT_MAX = 0x7FFFFFFF       # largest positive 32-bit signed value

    while b != 0:
        carry = (a & b) << 1        # where carries happen, moved one column left
        a = (a ^ b) & MASK          # add without carry, kept to 32 bits
        b = carry & MASK            # keep the carry to 32 bits too

    # a is now a 32-bit pattern. Interpret the sign bit.
    if a <= INT_MAX:
        return a                    # sign bit clear -> non-negative, as-is
    return ~(a ^ MASK)              # sign bit set -> recover the negative value


def _test() -> None:
    cases = [
        (1, 2, 3),
        (2, 3, 5),
        (3, 5, 8),
        (-1, 1, 0),
        (-2, -3, -5),
        (0, 0, 0),
        (-5, 4, -1),
        (100, -50, 50),
        (2147483647, 0, 2147483647),      # INT_MAX unchanged
        (-2147483648, 0, -2147483648),    # INT_MIN unchanged
        (-1000, -1000, -2000),
    ]
    for a, b, expected in cases:
        assert get_sum(a, b) == expected, (a, b)
    print("get_sum: all cases passed")


if __name__ == "__main__":
    _test()
