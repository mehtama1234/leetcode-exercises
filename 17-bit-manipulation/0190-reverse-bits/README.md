# 190. Reverse Bits

**Pattern:** Bit manipulation (pour bits from one register into another)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/reverse-bits/

## The problem in plain words

Write the number in binary using exactly 32 bits, then flip it end for end. The
bit at position `0` (the rightmost) moves to position `31` (the leftmost),
position `1` swaps with position `30`, and so on. Return the number that new
spelling produces.

Using a small 4-bit example so the bits are easy to see: `1011` reversed is
`1101`.

```diagram
   position:  3 2 1 0            3 2 1 0
   bits:      1 0 1 1    -->     1 1 0 1

   bit at 0 (a 1) travels to position 3
   bit at 3 (a 1) travels to position 0
   the two middle bits swap:  0 <-> 1
```

## Why this matters

The core operation is **reordering bits inside a fixed-width word using only
shifts and masks** — reading from one end while writing to the other, with no
memory beyond a couple of registers (a register is a small fixed slot of bits the
processor works in). It stands in for the byte-order and bit-order shuffling that
hardware and low-level code do all the time.

Where it actually shows up: converting between big-endian network order and
little-endian processors (reversing the byte order of an integer) is this same
shift-and-place move. The FFT — a workhorse of signal processing — reorders its
inputs by *bit-reversed* index, which is exactly this. Some cryptography and
hashing steps permute bits inside a word. Certain communication protocols send a
field lowest-bit-first and must reverse it on the other end. Graphics and
compression code pack and unpack bit fields the same way.

What you get is constant time and constant memory — a fixed 32 iterations, no
string built, no heap used — which maps cleanly onto a single processor
instruction or a tiny loop in a hot path where you can't afford to allocate.

## Start from the obvious

You could turn the number into a string, reverse the string, and parse it back:

```diagram
   n = 43  ->  "00000000000000000000000000101011"   (32-char binary)
                reverse the string
           ->  "11010100000000000000000000000000"
                parse back as a number
```

That's correct and easy to follow. It also makes the mechanic plain: you're
reading bits from one end and writing them to the other. You can do that same
thing with pure arithmetic and no string.

## The insight

Keep a `result` you build from the bottom up, while you eat `n` from the bottom
down. Repeat 32 times:

1. Shift `result` left by one — this opens an empty slot at its bottom.
2. Copy `n`'s current lowest bit (`n & 1`) into that slot with OR.
3. Shift `n` right by one, so its next bit becomes the new lowest.

Why this reverses the order: the *first* bit you pull off `n` (its bit 0) then
gets carried along by 31 more left-shifts of `result`, so it finishes at the top.
The *last* bit you pull off (bit 31) is placed after `result` has stopped
shifting, so it settles at the bottom. First-read lands highest, last-read lands
lowest — that's a reversal.

Walk `n = 1011` (its bits, read from the bottom, are 1, 1, 0, 1):

```diagram
   step | n    | n&1 | result before | result after
   -----+------+-----+---------------+-------------
     1  | 1011 |  1  |     0000      |  0001   (0<<1 | 1)
     2  |  101 |  1  |     0001      |  0011   (1<<1 | 1)
     3  |   10 |  0  |     0011      |  0110   (11<<1 | 0)
     4  |    1 |  1  |     0110      |  1101   (110<<1 | 1)

   1011 -> 1101,  reversed as promised
```

## Complexity

- **Time: constant.** A fixed 32 iterations no matter the input — write it as
  `O(32)` = `O(1)`.
- **Extra memory: constant.** Two integer registers, no string.

## Pitfalls

- **Python's unbounded integers.** Real hardware has a fixed 32-bit register that
  drops anything above bit 31; Python's integers just keep growing. Mask the
  answer with `& 0xFFFFFFFF` so it stays a genuine 32-bit unsigned value.
- Do exactly 32 iterations, not `n.bit_length()`. Leading zeros matter: they
  become trailing zeros after the flip, so every one of the 32 positions counts.
- Watch out for arithmetic versus logical right shift on negative inputs; treat
  `n` as the unsigned 32-bit pattern it stands for.

## Transfer

The "eat from one end, build onto the other" loop is the same skeleton used to
reverse a linked list (move nodes from `head` onto a growing `prev`) and to
reverse the digits of an integer (`res = res*10 + n%10`). Recognize it as *pour
bits from one register into another to flip their order.* The 32-bit masking
lesson comes back in [Sum of Two Integers / 371](../0371-sum-of-two-integers/).
