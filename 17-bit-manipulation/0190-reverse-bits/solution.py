"""190. Reverse Bits — https://leetcode.com/problems/reverse-bits/

Reverse the bits of a 32-bit unsigned integer: the bit at position 0 ends up at
position 31, position 1 at position 30, and so on. Return the resulting number.
"""


def reverse_bits(n: int) -> int:
    """Peel the lowest bit off n, push it onto the top of the result.

    Think of two 32-bit registers. On each of 32 steps:
      - make room in the result by shifting it left one position,
      - copy n's current lowest bit into the freshly opened slot,
      - drop that bit from n by shifting n right.

    Because the result grows from the bottom while n shrinks from the bottom, the
    first bit we read (n's bit 0) ends up shifted left 31 times — landing at the
    top, exactly where reversal wants it. The last bit we read (n's bit 31) is
    added when the result is done shifting, so it lands at the bottom.

    Walk a 4-bit example, n = 1011 (read right-to-left: bits 1,1,0,1):

        step 1: res = 0<<1 | 1 = 1        (000...0001)
        step 2: res = 1<<1 | 1 = 11
        step 3: res = 11<<1 | 0 = 110
        step 4: res = 110<<1 | 1 = 1101   reversed 1011 -> 1101  correct
    """
    result = 0
    for _ in range(32):
        result = (result << 1) | (n & 1)
        n >>= 1
    return result & 0xFFFFFFFF  # keep it a clean 32-bit value


def _test() -> None:
    # LeetCode's two examples, given as 32-bit binary literals
    n1 = 0b00000010100101000001111010011100
    r1 = 0b00111001011110000010100101000000
    n2 = 0b11111111111111111111111111111101
    r2 = 0b10111111111111111111111111111111
    assert reverse_bits(n1) == r1
    assert reverse_bits(n2) == r2
    # edge cases
    assert reverse_bits(0) == 0
    assert reverse_bits(0xFFFFFFFF) == 0xFFFFFFFF   # all ones reverses to itself
    # bit 0 set should land at bit 31
    assert reverse_bits(1) == 0x80000000
    # applying twice returns the original (reversal is its own inverse)
    assert reverse_bits(reverse_bits(n1)) == n1
    print("reverse_bits: all cases passed")


if __name__ == "__main__":
    _test()
