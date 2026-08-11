"""338. Counting Bits — https://leetcode.com/problems/counting-bits/

Given `n`, return an array `ans` of length `n+1` where `ans[i]` is the number of
1-bits in the binary representation of `i`, for every `i` from 0 to n.

Two implementations are kept side by side: the honest per-number count, and the
dynamic-programming trick that reuses answers we already computed.
"""
from typing import List


def count_bits_brute(n: int) -> List[int]:
    """Count the 1-bits of each number independently. O(n log n) time.

    For each i we peel off bits one at a time (`i & (i-1)` clears the lowest set
    bit). A number has at most ~log2(i) set bits, so each count is O(log n) and
    the whole thing is O(n log n). This is the obvious, correct starting point —
    but every number is counted from scratch, ignoring work we already did.
    """
    ans: List[int] = []
    for i in range(n + 1):
        count = 0
        x = i
        while x:
            x &= x - 1  # drop the lowest set bit
            count += 1
        ans.append(count)
    return ans


def count_bits(n: int) -> List[int]:
    """DP using the lowest bit. O(n) time, O(1) extra (beyond the output).

    Insight: writing i in binary, if you drop its lowest set bit you get a
    *smaller* number whose answer you've already computed. The relation:

        ans[i] = ans[i & (i - 1)] + 1

    `i & (i - 1)` is i with its lowest 1-bit cleared. That removed bit is exactly
    one 1, so ans[i] is "the smaller number's count, plus 1". Concretely:

        i = 6 = 110  ->  i & (i-1) = 100 = 4,  ans[6] = ans[4] + 1 = 1 + 1 = 2
        i = 7 = 111  ->  i & (i-1) = 110 = 6,  ans[7] = ans[6] + 1 = 2 + 1 = 3

    Each entry is O(1), so the whole array is O(n) — no per-number log factor.
    """
    ans = [0] * (n + 1)
    for i in range(1, n + 1):
        ans[i] = ans[i & (i - 1)] + 1
    return ans


def _test() -> None:
    cases = [
        (0, [0]),
        (2, [0, 1, 1]),
        (5, [0, 1, 1, 2, 1, 2]),
    ]
    for n, expected in cases:
        assert count_bits(n) == expected, n
        assert count_bits_brute(n) == expected, n
    # both methods must agree on a larger range
    for n in (1, 16, 100):
        assert count_bits(n) == count_bits_brute(n), n
    # spot-check a known value: 255 = 11111111 has 8 ones
    assert count_bits(255)[255] == 8
    print("count_bits: all cases passed")


if __name__ == "__main__":
    _test()
