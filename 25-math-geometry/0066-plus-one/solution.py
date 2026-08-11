"""66. Plus One — https://leetcode.com/problems/plus-one/

A non-negative integer is given as an array of its digits, most-significant
first. Add one to it and return the resulting array of digits.

One clean function is enough here: the whole problem is carrying a +1 through
the digits by hand, exactly as you learned to add on paper.
"""
from typing import List


def plus_one(digits: List[int]) -> List[int]:
    """Add one to a big number stored as a digit array. O(n) time, O(1) extra.

    The insight is that adding one only propagates a carry through a run of
    trailing 9s. Walk from the last digit backward:
      - if the digit is < 9, bump it and we're done (no carry escapes);
      - if it's 9, it becomes 0 and the carry moves left.
    If we fall off the left end still carrying (the number was all 9s, like
    999), the result is one digit longer: a leading 1 followed by all zeros.
    """
    for i in range(len(digits) - 1, -1, -1):
        if digits[i] < 9:
            digits[i] += 1      # no carry past here; done
            return digits
        digits[i] = 0           # 9 + 1 = 10 -> write 0, carry the 1 left
    return [1] + digits         # every digit was 9: 999... -> 1000...


def _test() -> None:
    cases = [
        ([1, 2, 3], [1, 2, 4]),          # 123 -> 124
        ([4, 3, 2, 1], [4, 3, 2, 2]),    # 4321 -> 4322
        ([9], [1, 0]),                   # 9 -> 10, grows a digit
        ([9, 9, 9], [1, 0, 0, 0]),       # all nines
        ([0], [1]),                      # 0 -> 1
        ([1, 9, 9], [2, 0, 0]),          # carry stops partway
    ]
    for digits, expected in cases:
        assert plus_one(list(digits)) == expected, (digits, expected)
    print("plus_one: all cases passed")


if __name__ == "__main__":
    _test()
