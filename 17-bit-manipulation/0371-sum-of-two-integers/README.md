# 371. Sum of Two Integers

**Pattern:** Bit manipulation (add by simulating a hardware adder)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/sum-of-two-integers/

## The problem in plain words

Compute `a + b`, but you're not allowed to use `+` or `-`. So you have to
rebuild addition out of bitwise operations — the same way a CPU's adder actually
does it in silicon. Inputs may be negative, treated as 32-bit signed integers.

## Start from the obvious

We can't use `+`, so recall how you add two binary numbers by hand, column by
column. In each column you produce a **sum bit** and maybe a **carry** into the
next column:

```
  a bit | b bit | sum bit | carry out
    0   |   0   |    0    |    0
    0   |   1   |    1    |    0
    1   |   0   |    1    |    0
    1   |   1   |    0    |    1
```

Stare at those two output columns:

- The **sum bit** column is exactly `a XOR b`.
- The **carry out** column is exactly `a AND b`.

That's the whole trick: XOR gives you the addition *without* carrying, and AND
tells you *where* a carry was generated.

## The insight

A carry generated in one column belongs in the column to its **left**, so shift
it: `(a & b) << 1`. Now the real sum is "the carry-free sum" plus "the shifted
carry" — but that's another addition, so we repeat the same two operations until
no carry is left:

```
sum   = a ^ b
carry = (a & b) << 1
# now add sum + carry the same way, loop until carry == 0
```

Worked example, `3 + 5`:

```
a = 011 (3), b = 101 (5)
pass 1: sum = 011 ^ 101 = 110,   carry = (011 & 101)<<1 = 001<<1 = 010
pass 2: a=110, b=010:  sum = 100, carry = (110 & 010)<<1 = 010<<1 = 100
pass 3: a=100, b=100:  sum = 000, carry = (100 & 100)<<1 = 100<<1 = 1000
pass 4: a=000, b=1000: sum = 1000, carry = 0  -> done
answer = 1000 = 8
```

Each pass pushes the carries one column further left; since they can't move left
forever within a fixed width, the loop terminates.

## The 32-bit masking (the part Python forces on us)

On real hardware, integers live in a **fixed 32-bit register** that silently
throws away anything above bit 31, and negatives are stored in *two's
complement*. Python's integers are unbounded — they never overflow — so two
things break unless we intervene:

1. **The loop might never end.** With negative inputs the carry keeps shifting
   left into ever-higher bits that a real register wouldn't have. Fix: after
   every step mask with `MASK = 0xFFFFFFFF` to keep only the low 32 bits. That
   *is* the register discarding overflow, so carries eventually fall off the top
   and `b` reaches `0`.

2. **The sign comes out wrong.** When the loop ends, `a` is a raw 32-bit
   pattern. If bit 31 (the sign bit) is set, the intended value is negative, but
   Python sees a big positive number like `4294967291`. Convert it back:

   ```
   INT_MAX = 0x7FFFFFFF
   if a <= INT_MAX:   # sign bit clear -> genuinely non-negative
       return a
   return ~(a ^ MASK) # sign bit set -> rebuild the Python negative
   ```

   `a ^ MASK` flips all 32 bits, and `~` finishes the two's-complement negation,
   turning the pattern into the correct signed Python integer. Example: the
   pattern for `-1` is `0xFFFFFFFF`; `~(0xFFFFFFFF ^ 0xFFFFFFFF) = ~0 = -1`.

## Complexity

- **Time:** `O(1)` — at most 32 passes (one carry propagation per bit width).
- **Space:** `O(1)` — a few integer registers.

## Pitfalls

- Skipping the mask: the loop hangs forever on inputs like `-1 + 1` because the
  carry never falls off Python's infinite-width integer.
- Returning `a` directly for negative results — you'd get a huge positive number.
  You must reinterpret the sign bit.
- Off-by-one on which value to shift: the **carry** (`a & b`) is shifted left,
  never the sum.

## Transfer

This is "simulate a full adder in software," and the same XOR-is-sum /
AND-is-carry decomposition underlies other carry-free tricks (e.g. adding
without overflow, Gray codes). The broader lesson — *when a language's integers
don't match the problem's fixed width, mask to that width and reinterpret the
sign bit* — recurs across bit-manipulation problems like
[Reverse Bits / 190](../0190-reverse-bits/).
