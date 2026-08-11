"""191. Number of 1 Bits — https://leetcode.com/problems/number-of-1-bits/

Given an unsigned integer, return how many bits are set to 1 in its binary
representation (its "Hamming weight").

Two implementations: the straightforward scan of all bit positions, and the
Brian Kernighan trick that only loops once per set bit.
"""


def hamming_weight_scan(n: int) -> int:
    """Check the lowest bit, then shift right, repeat. O(#bits) time.

    Look at bit 0 with `n & 1`, add it, then shift the number down by one so the
    next bit becomes bit 0. You do one iteration per *bit position*, so for a
    32-bit input this is 32 steps regardless of how many are set.

        n = 1011:  &1=1 (total 1), >>  101
                   &1=1 (total 2), >>   10
                   &1=0 (total 2), >>    1
                   &1=1 (total 3), >>    0  done
    """
    count = 0
    while n:
        count += n & 1
        n >>= 1
    return count


def hamming_weight(n: int) -> int:
    """Brian Kernighan: clear the lowest set bit each step. O(#set bits) time.

    `n & (n - 1)` erases the lowest 1-bit of n (subtracting 1 flips that bit to 0
    and turns the zeros below it into ones; AND-ing keeps the higher bits and
    wipes that bottom run). So each loop removes exactly one set bit, and the
    loop runs only as many times as there are 1s — not once per bit position.

        n = 1100:  n&(n-1) = 1000  (cleared a 1, count 1)
                   n&(n-1) = 0000  (cleared a 1, count 2)  done -> 2

    For a sparse number like 1000...0001 this is 2 steps instead of 32.
    """
    count = 0
    while n:
        n &= n - 1  # clear the lowest set bit
        count += 1
    return count


def _test() -> None:
    # LeetCode examples (given as binary strings in the prompt)
    cases = [
        (0b00000000000000000000000000001011, 3),
        (0b00000000000000000000000010000000, 1),
        (0b11111111111111111111111111111101, 31),
        (0, 0),               # no bits set
        (0xFFFFFFFF, 32),     # all 32 bits set
    ]
    for n, expected in cases:
        assert hamming_weight(n) == expected, n
        assert hamming_weight_scan(n) == expected, n
    print("hamming_weight: all cases passed")


if __name__ == "__main__":
    _test()
