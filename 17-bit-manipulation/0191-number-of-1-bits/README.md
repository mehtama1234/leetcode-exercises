# 191. Number of 1 Bits

**Pattern:** Bit manipulation (clear the lowest set bit, one step per one)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/number-of-1-bits/

## The problem in plain words

Take a number, write it in binary, and count how many of its bits are `1`. That
count has a name: the *Hamming weight* (the number of ones).

Example: `11` in binary is `1011`, which has three `1`s, so the answer is `3`.

```diagram
   11 in binary:

     8 4 2 1     place values
     1 0 1 1     -> the set places are 8, 2, 1  ->  three ones
```

## Why this matters

Counting the `1` bits — often called *popcount* (population count) — is one of the
most-used low-level operations, and the `n & (n - 1)` trick makes it cost one step
per set bit instead of one step per bit position. The underlying question is "how
many things are switched on in this bitmask?"

It shows up everywhere bitsets are used. Databases and search engines store sets
of rows as bitmaps and popcount them to size the result of an AND or OR and to
estimate how many rows match. Hamming distance (the popcount of an XOR) drives
error-correcting codes, similarity search, and image fingerprinting. Chess engines
keep the board as a 64-bit mask and popcount to count pieces or available moves.
Memory allocators count free slots in a bitmask; networking counts the set bits in
a subnet mask.

What you get is speed: fewer iterations, no per-bit branch, and on real hardware
this collapses to a single `POPCNT` instruction. In hot paths that run billions of
times, that difference is the whole point.

## Start from the obvious

Look at the bottom bit, count it, then slide everything down one position so the
next bit becomes the bottom bit. Repeat until nothing is left.

```diagram
   walk n = 1011, checking the lowest bit each time

   n     | n & 1 | count | shift
   ------+-------+-------+------
   1011  |   1   |   1   | -> 101
    101  |   1   |   2   | ->  10
     10  |   0   |   2   | ->   1
      1  |   1   |   3   | ->   0   done, answer 3
```

Correct. But notice: it takes one step per *bit position*. A 32-bit number always
costs 32 iterations, even if only a single bit is set.

## Find the waste

Most of those 32 steps hit a `0` bit and do nothing but shift. If a number is
`1000...0001` (two set bits, one at each end), you still grind through all 32
positions to find the two ones. You're paying for the width of the number, not for
the work that matters — the count of `1`s.

## The insight

There's a single operation that deletes exactly the lowest set bit: `n & (n - 1)`.

Why it works: subtracting `1` flips the lowest `1` to `0` and turns every `0`
below it into `1`. AND-ing that back with the original keeps every higher bit
unchanged and clears that whole bottom run — the net effect is that the lowest `1`
disappears.

```diagram
   why n & (n-1) erases the lowest set bit

     n      = 1 1 0 0
     n - 1  = 1 0 1 1     (lowest 1 flipped to 0, zeros below flipped to 1)
     -------------------
     n & .. = 1 0 0 0     the bottom 1 is gone; higher bits untouched
              ^ ^
              kept  cleared
```

So loop `n &= n - 1` and count how many times you can do it before `n` reaches
`0`. Each step removes one `1`, so the loop runs exactly as many times as there
are set bits.

```diagram
   n = 1100:

     1100  --(& n-1)-->  1000   count 1
     1000  --(& n-1)-->  0000   count 2   done, answer 2
```

For a sparse number that's a handful of steps instead of a full 32.

## Complexity

- **Scan version:** about `w` steps, where `w` is the bit width (32 here) — a
  fixed cost every time.
- **Clear-lowest-bit version:** about `k` steps, where `k` is the number of set
  bits — never more than `w`, often far fewer.
- **Extra memory:** constant for both.

## Pitfalls

- Using an *arithmetic* right shift on a negative number in languages that copy
  the sign bit in — you'd loop forever. Use an unsigned/logical shift, or the
  `n & (n - 1)` form, which never shifts at all.
- In Python, integers are unbounded, so treat the input as the 32-bit unsigned
  value it stands for; the tests use exact 32-bit patterns like `0xFFFFFFFF`.

## Transfer

`n & (n - 1)` is a workhorse. It powers the linear-time table fill in
[Counting Bits / 338](../0338-counting-bits/) and the classic power-of-two check
`n > 0 and (n & (n - 1)) == 0` (a power of two has a single set bit, so clearing
it leaves `0`). Whenever you want to touch set bits one at a time rather than scan
every position, reach for it.
