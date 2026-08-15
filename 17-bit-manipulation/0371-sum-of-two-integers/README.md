# 371. Sum of Two Integers

**Pattern:** Bit manipulation (rebuild addition as a hardware adder does)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/sum-of-two-integers/

## The problem in plain words

Compute `a + b`, but you're not allowed to use `+` or `-`. So you have to rebuild
addition out of bitwise operations — the same way a processor's adder does it in
silicon. Inputs may be negative, treated as 32-bit signed integers.

```diagram
   example: 3 + 5
   a = 011  (3)
   b = 101  (5)
   answer = 1000  (8)
```

## Why this matters

This rebuilds addition from **XOR (add without carrying) and AND-then-shift
(where the carries go)** — literally simulating a hardware adder. The core insight
is that arithmetic *is* a fixed sequence of bit operations; this puzzle just makes
that machinery visible instead of hiding it behind the `+` sign.

Where it genuinely matters: it's how processors and FPGAs actually add. Ripple-
carry and carry-lookahead adders are these same XOR and AND relationships in
silicon, so this is the mental model behind digital-logic design. Emulators that
model a target chip implement arithmetic exactly this way. Big-integer and
cryptography libraries build wide addition out of word-by-word carry propagation.
Understanding the carry chain also explains real behavior programmers hit: integer
overflow, two's-complement negatives, and why signed wraparound looks the way it
does.

What you get here isn't speed — it's *understanding the primitive*. Knowing that
addition is XOR-plus-carry demystifies overflow, bit tricks, and hardware timing,
and it's the foundation for building any operation when only bitwise ones are
available.

## Start from the obvious

You can't use `+`, so recall how you add two binary numbers by hand, column by
column. In each column you produce a **sum bit** and maybe a **carry** into the
next column:

```diagram
   a bit | b bit | sum bit | carry out
   ------+-------+---------+----------
     0   |   0   |    0    |    0
     0   |   1   |    1    |    0
     1   |   0   |    1    |    0
     1   |   1   |    0    |    1
             ^^^      ^^^        ^^^
   look at the two output columns:
      sum bit  = a XOR b   (1 exactly when the inputs differ)
      carry    = a AND b   (1 exactly when both inputs are 1)
```

That's the whole trick: XOR gives you the addition *without* carrying, and AND
tells you *where* a carry was produced.

## The insight

A carry produced in one column belongs in the column to its **left**, so shift it:
`(a & b) << 1`. The real sum is now "the carry-free sum" plus "the shifted carry"
— but that's another addition, so repeat the same two operations until no carry is
left:

```
sum   = a ^ b
carry = (a & b) << 1
# now add sum + carry the same way; loop until carry == 0
```

Worked example, `3 + 5`:

```diagram
   a = 011 (3),  b = 101 (5)

   pass | a    | b    | sum = a^b | carry = (a&b)<<1
   -----+------+------+-----------+-----------------
     1  |  011 |  101 |    110    | (001)<<1 = 010
     2  |  110 |  010 |    100    | (010)<<1 = 100
     3  |  100 |  100 |    000    | (100)<<1 = 1000
     4  |  000 | 1000 |   1000    |      0    -> done

   answer = 1000 = 8

   each pass pushes the carries one column further left; they can't
   move left forever within a fixed width, so the loop ends
```

## The 32-bit masking (the part Python forces on us)

On real hardware, integers live in a **fixed 32-bit register** that silently
throws away anything above bit 31, and negatives are stored in *two's complement*
(a way of writing negatives so the same adder handles them). Python's integers are
unbounded — they never overflow — so two things break unless you step in:

1. **The loop might never end.** With negative inputs the carry keeps shifting
   left into ever-higher bits a real register wouldn't have. Fix: after every
   step, mask with `MASK = 0xFFFFFFFF` to keep only the low 32 bits. That mask
   *is* the register discarding overflow, so carries eventually fall off the top
   and `b` reaches `0`.

```diagram
   masking mimics a 32-bit register dropping the overflow

     ...1 0 1 1 0 0   a carry has shifted up past bit 31
     & 0 1 1 1 ...1   MASK keeps only the low 32 bits
     ---------------
       bits above 31 fall off  ->  the carry chain can finally empty
```

2. **The sign comes out wrong.** When the loop ends, `a` is a raw 32-bit pattern.
   If bit 31 (the sign bit) is set, the intended value is negative, but Python
   reads it as a big positive number like `4294967291`. Convert it back:

   ```
   INT_MAX = 0x7FFFFFFF
   if a <= INT_MAX:      # sign bit clear -> genuinely non-negative
       return a
   return ~(a ^ MASK)    # sign bit set -> rebuild the Python negative
   ```

   `a ^ MASK` flips all 32 bits, and `~` finishes the two's-complement negation,
   turning the pattern into the correct signed Python integer. Example: the
   pattern for `-1` is `0xFFFFFFFF`; `~(0xFFFFFFFF ^ 0xFFFFFFFF) = ~0 = -1`.

## Complexity

- **Time: constant.** At most 32 passes — one carry step per bit of width.
- **Extra memory: constant.** A few integer registers.

## Pitfalls

- Skipping the mask: the loop hangs forever on inputs like `-1 + 1`, because the
  carry never falls off Python's infinite-width integer.
- Returning `a` directly for a negative result — you'd get a huge positive number.
  You must reinterpret the sign bit.
- Off-by-one on which value to shift: the **carry** (`a & b`) is shifted left,
  never the sum.

## Transfer

This is "simulate a full adder in software," and the same XOR-is-sum /
AND-is-carry split underlies other carry-free tricks (adding without overflow,
Gray codes). The broader lesson — *when a language's integers don't match the
problem's fixed width, mask to that width and reinterpret the sign bit* — comes
back across bit problems like
[Reverse Bits / 190](../0190-reverse-bits/).
