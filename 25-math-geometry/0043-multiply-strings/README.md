# 43. Multiply Strings

**Pattern:** Grade-school long multiplication on digit arrays
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/multiply-strings/

## The problem in plain words

Two non-negative whole numbers arrive as strings — possibly hundreds of digits
long, far bigger than any machine integer. Multiply them and give back the
product as a string. No cheating by converting to `int` and using `*`; do the
multiplication by hand, the way you learned on paper.

```diagram
        1 2 3
      x 4 5 6
      -------
        7 3 8     <- 123 x 6
      6 1 5       <- 123 x 5, shifted one place left
    4 9 2         <- 123 x 4, shifted two places left
    ---------
    5 6 0 8 8
```

## Why this matters

The point is that numbers too big for a machine word have to be stored as arrays
of digits, and every operation on them is done one digit at a time. Multiplication
is the interesting one because a single digit-times-digit gives a two-digit result
that has to land in the right *place* and carry into the next.

This is the core of every big-number library — Python's own integers, Java's
`BigInteger`, the modular arithmetic under RSA and elliptic-curve crypto. When a
number won't fit in 64 bits, this per-digit multiply with carries is what actually
runs. Learning where each partial product lands, and how carries settle, is
learning how arbitrary-precision math works.

## Start from the obvious

Turn both strings into integers, multiply, turn the result back into a string.

```diagram
   "123" -> 123 ,  "456" -> 456
   123 * 456 = 56088  ->  "56088"
```

Fine for short numbers. But the whole reason the problem hands you strings is that
the numbers might be longer than any native integer can hold. Leaning on `int`
either fails outright on a fixed-width machine or quietly relies on the very
big-number support the problem wants you to build. So do it by hand.

## The insight

Here is the fact that makes it clean. When you multiply digit `i` of the first
number by digit `j` of the second, that partial product always lands in the same
place: position `i + j` counted from the right. A number with `m` digits times one
with `n` digits has at most `m + n` digits, so make a result array of that size,
drop every digit-times-digit product into its `i + j` slot, and settle the carries
at the very end.

```diagram
   num1 = "12"  (positions from right: '2'->0, '1'->1)
   num2 = "34"  (positions from right: '4'->0, '3'->1)

   result[]:   [ .  .  .  . ]   indices 0..3, 0 = units place

   2 x 4 = 8   -> slot 0+0=0     result[0] += 8
   2 x 3 = 6   -> slot 0+1=1     result[1] += 6
   1 x 4 = 4   -> slot 1+0=1     result[1] += 4
   1 x 3 = 3   -> slot 1+1=2     result[2] += 3

   result (before carries): [ 8, 10, 3, 0 ]
                                  ^ 10 is too big for one slot
```

Notice slot 1 holds `10` — bigger than a single digit. That's fine; carries are
resolved in one final left-to-right sweep. Each slot keeps its ones digit and
passes the rest up to the next slot.

```diagram
   settle carries, slot by slot (0 = units):
     slot 0:  8            -> keep 8,  carry 0
     slot 1:  10 + 0 = 10  -> keep 0,  carry 1
     slot 2:  3  + 1 = 4   -> keep 4,  carry 0
     slot 3:  0  + 0 = 0   -> keep 0

   result (little-endian): [ 8, 0, 4, 0 ]
   read big-endian, drop leading zeros:  "408"
   check: 12 x 34 = 408  ok
```

## Complexity

- **Time: about m x n steps.** Every digit of the first number meets every digit
  of the second once, then one linear sweep settles the carries.
- **Extra memory: about m + n.** The result array, the most places the product
  can occupy.

## Pitfalls

- Getting the place wrong. The partial product of digits at positions `i` and `j`
  (counted from the right) lands at slot `i + j`, not `i * j`.
- Forgetting the `"0"` case — if either input is `"0"`, the answer is `"0"`, not a
  string of leading zeros.
- Trimming leading zeros too eagerly (or not at all). The top slot may or may not
  carry, so strip leading zeros but leave a single `0` if that's all there is.

## Transfer

The reusable move is **store a big number as a digit array, place each partial
result by its position, and settle carries in one final pass.** It shares its
carry machinery with [Plus One / 66](../0066-plus-one/) and
[Add Binary / 67](https://leetcode.com/problems/add-binary/), and it's the
schoolbook multiply that every arbitrary-precision integer library is built on.
