# 190. Reverse Bits

**Pattern:** Bit manipulation (build a result bit-by-bit)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/reverse-bits/

## The problem in plain words

Write the number in binary using exactly 32 bits, then flip it end-for-end. The
bit that was at position `0` (the rightmost) moves to position `31` (the
leftmost), position `1` swaps with position `30`, and so on. Return the number
that spelling produces.

Using a small 4-bit example so the bits are visible: `1011` reversed is `1101`.

## Start from the obvious

You could turn it into a string, reverse the string, and parse it back:

```
s = format(n, "032b")   # 32-char binary string
return int(s[::-1], 2)  # reverse and re-parse
```

That's correct and easy to reason about. It also makes the mechanic obvious:
we're reading bits from one end and writing them to the other. We can do that
same thing with pure arithmetic and no string allocation.

## The insight

Keep a `result` that we build from the bottom up while we consume `n` from the
bottom down. Repeat 32 times:

1. Shift `result` left by one — this opens an empty slot at its bottom.
2. Copy `n`'s current lowest bit (`n & 1`) into that slot with OR.
3. Shift `n` right by one, so its next bit becomes the new lowest.

Why this reverses: the *first* bit we pull off `n` (its bit 0) then gets carried
along by 31 more left-shifts of `result`, so it finishes at the top. The *last*
bit we pull off (bit 31) is placed when `result` has stopped shifting, so it
settles at the bottom. First-read lands highest, last-read lands lowest — that's
exactly a reversal.

Walk `n = 1011` (its bits from the bottom are 1, 1, 0, 1):

```
step 1: result = (0   << 1) | 1 = 1        (0001)
step 2: result = (1   << 1) | 1 = 11       (0011)
step 3: result = (11  << 1) | 0 = 110      (0110)
step 4: result = (110 << 1) | 1 = 1101     (1101)
```

`1011 -> 1101`. Reversed, as promised.

## Complexity

- **Time:** `O(32)` = `O(1)` — a fixed 32 iterations no matter the input.
- **Space:** `O(1)` — two integer registers, no string.

## Pitfalls

- **Python's unbounded ints.** Real hardware has a fixed 32-bit register that
  drops overflow; Python's integers just keep growing. Mask the answer with
  `& 0xFFFFFFFF` so it stays a genuine 32-bit unsigned value.
- Doing exactly 32 iterations, not `n.bit_length()`. Leading zeros matter: they
  become trailing zeros after reversal, so every one of the 32 positions counts.
- Confusing arithmetic vs. logical right shift on negative inputs; treat `n` as
  the unsigned 32-bit pattern it represents.

## Transfer

The "consume from one end, build onto the other" loop is the same skeleton used
to reverse a linked list (move nodes from `head` onto a growing `prev`) and to
reverse digits of an integer (`res = res*10 + n%10`). Recognize it as *pour bits
from one register into another to flip their order*.
