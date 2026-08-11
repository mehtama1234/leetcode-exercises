# 43. Multiply Strings

**Pattern:** Grade-school long multiplication on digit arrays
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/multiply-strings/

## The problem in plain words

You're given two non-negative whole numbers written as strings — possibly
hundreds of digits long — and you must return their product, also as a string.
The catch: you can't just call `int(num1) * int(num2)`; you have to multiply
them the way you were taught on paper.

## Why this matters

Underneath the puzzle is the reality that *the numbers are too big to fit in any
native integer type, so you compute with arrays of digits* — and multiplication,
unlike addition, needs you to place each partial product at the right place
value and then settle all the carries.

That exact move is what big-integer libraries do. Python's unbounded `int`,
Java's `BigInteger`, and every RSA/elliptic-curve crypto routine multiply
multi-hundred-digit numbers as arrays of "limbs" using exactly this
place-value-plus-carry structure (with faster algorithms layered on top for huge
sizes). Financial and scientific systems that need exact, non-floating-point
arithmetic rely on the same core.

What the good solution buys is **correctness at any size** with a predictable
`O(m·n)` cost, and it teaches the one insight everything bigger builds on: the
digit at position `i` times the digit at position `j` always lands in the
product's place `i + j`. Get that placement right and the carries take care of
the rest.

## Start from the obvious

The tempting shortcut:

```
return str(int(num1) * int(num2))
```

It's the honest first thought and it even passes — but only because Python
already implements big-integer multiplication for you. The problem exists to
make you *build* that, so the shortcut sidesteps the entire lesson. We reject it
on purpose.

## The insight

Remember stacking numbers on paper. To multiply `123 × 456`, you compute
`123×6`, then `123×5` shifted one place left, then `123×4` shifted two places —
and add the columns. The shift is the whole trick, and there's a clean rule for
it:

> If you number both inputs' digits **from the right** starting at 0, then digit
> `i` of one times digit `j` of the other contributes to place `i + j` of the
> product.

So allocate a result array of length `m + n` (a product of an `m`-digit and an
`n`-digit number can't be longer than that). For every pair of digits, add their
product into slot `i + j`. Don't worry about carries yet — just accumulate:

```
result = [0] * (m + n)
for i (from right of num1):
    for j (from right of num2):
        result[i + j] += d1 * d2
```

Then make one pass to settle carries: each slot keeps its ones digit, the rest
rolls into the next slot to the left. Finally strip leading zeros and join.

## Complexity

- **Time:** `O(m·n)` — every digit of one number meets every digit of the other
  once, plus an `O(m+n)` carry pass. (Specialized algorithms like Karatsuba beat
  this for very large inputs, but the schoolbook method is the foundation.)
- **Space:** `O(m + n)` for the result array.

## Pitfalls

- **The `"0"` case** — if either input is `"0"`, return `"0"` immediately;
  otherwise you emit `"000..."` from the padded array.
- **Leading zeros** — the result array is fixed at length `m + n`, but the
  product may be shorter, so trim leading zeros (keeping at least one digit).
- **Place-value indexing** — mixing up left-counted vs right-counted indices is
  the classic bug; being explicit that place = `i + j` from the right avoids it.
- **Deferring carries** — accumulating first and normalizing carries in a single
  final pass is cleaner and avoids carrying inside the double loop.
- Don't fall back to `int()` — the exercise is to not need it.

## Transfer

This is the multiplication sibling of the addition problems: carries over digit
arrays appear in
[Add Strings / 415](https://leetcode.com/problems/add-strings/),
[Add Binary / 67](https://leetcode.com/problems/add-binary/), and
[Plus One / 66](../0066-plus-one/). The place = `i + j` accumulation idea also
underlies polynomial multiplication and, taken further, the FFT-based multiply
used for enormous numbers.
