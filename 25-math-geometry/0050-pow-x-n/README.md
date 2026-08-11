# 50. Pow(x, n)

**Pattern:** Fast exponentiation by squaring (halve the work each step)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/powx-n/

## The problem in plain words

Compute `x` raised to the power `n`, and return a float. The exponent `n` can be
negative — `x^(-2)` means `1 / (x*x)`. The exponent can also be huge, like two
billion, so multiplying `x` by itself that many times is out of the question.

```diagram
   pow(2, 10) = 2*2*2*2*2*2*2*2*2*2 = 1024
   pow(2, -2) = 1 / (2*2) = 0.25
   pow(x, 0) = 1  for any x
```

## Why this matters

The naive definition — multiply `n` times — is a straight line of work: double the
exponent, double the multiplications. The insight is that powers hide a huge
amount of repeated work, and you can fold the exponent in half at every step
instead of subtracting one. That turns two billion multiplications into about
thirty.

Halving instead of decrementing is one of the biggest speedups in computing.
Binary search halves a search space; merge sort halves an array; this halves an
exponent. The same squaring trick is what makes modular exponentiation in RSA and
Diffie-Hellman fast enough to be practical — raising a number to a 2048-bit power
would be impossible one multiply at a time.

## Start from the obvious

Multiply `x` by itself `n` times. It's the definition turned straight into code.

```diagram
   pow(2, 10):
   result = 1
   x1  x2  x3  x4  x5  x6  x7  x8  x9  x10
   2   4   8   16  32  64  128 256 512 1024
       ^ ten separate multiplications
```

Correct, and fine for small `n`. But for `n = 2000000000` this does two billion
multiplications. The waste is that it never reuses any product — computing `x^10`
throws away everything it learned computing `x^5`.

## The insight

To get `x^10`, you don't need ten multiplies. If you already have `x^5`, then
`x^10` is just `x^5` squared — one multiply. And `x^5` is `x^2` squared times one
more `x`. Each step either squares what you have (doubling the exponent) or
squares and tacks on one extra `x` (for an odd exponent). That's driven by the
*binary digits* of the exponent.

```diagram
   10 in binary = 1010

   walk the exponent's bits from low to high, keeping a
   running power of x:  x, x^2, x^4, x^8, ...

   bit  power-of-x   this bit set?   result so far
   ---  ----------   -------------   -------------
    0    x^1  = 2       0 (no)        1
    1    x^2  = 4       1 (yes)       1 * 4      = 4
    2    x^4  = 16      0 (no)        4
    3    x^8  = 256     1 (yes)       4 * 256    = 1024

   10 = 8 + 2, so x^10 = x^8 * x^2 = 256 * 4 = 1024
```

Each pass squares the running power (`x -> x^2 -> x^4 -> x^8`) and folds it into
the answer only where the exponent has a `1` bit. About `log2(n)` steps total
instead of `n`.

```diagram
   n=10 (1010):  fold in x^2 and x^8    -> 4 * 256 = 1024
   n=13 (1101):  fold in x^1, x^4, x^8

   squaring chain:  x -> x^2 -> x^4 -> x^8   (only ~4 multiplies for exp 13)
```

Negative `n` is handled up front: `x^(-n)` is `(1/x)^n`, so flip `x` to its
reciprocal and make `n` positive.

## Complexity

- **Time: about log2(n) steps.** The exponent halves every pass (one bit dropped),
  so a billion becomes roughly thirty multiplications.
- **Extra memory: constant.** A running result and a running power of `x`.

## Pitfalls

- The naive `n`-multiply loop times out on large exponents — the whole reason the
  squaring trick exists.
- Handling negative `n`. Flip `x` to `1/x` and negate `n` before the loop.
- In fixed-width languages, negating the most-negative exponent overflows;
  convert its magnitude carefully. (Python integers don't overflow, so this trap
  doesn't bite here.)

## Transfer

The reusable move is **halve the problem each step instead of shaving one off,
driven by the binary digits of a count.** The same square-and-multiply idea
powers modular exponentiation in cryptography, and the halving instinct connects
to [Binary Search / 704](https://leetcode.com/problems/binary-search/) and any
divide-in-half algorithm.
