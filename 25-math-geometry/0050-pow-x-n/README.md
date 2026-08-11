# 50. Pow(x, n)

**Pattern:** Fast exponentiation by squaring (divide the exponent)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/powx-n/

## The problem in plain words

Given a number `x` and an integer exponent `n`, compute `x^n`. The exponent can
be negative (which means one over the positive power), zero, or very large.
Return the answer as a float.

## Why this matters

Underneath the puzzle is one idea: *you can compute a repeated operation in a
number of steps proportional to the logarithm of how many times it repeats,
instead of doing it that many times.* The trick is that `x^n` contains `x^(n/2)`
twice — so if you compute the half once and square it, you've halved the work,
and halving repeatedly is what gives you `log n` steps.

That exact move runs real systems. RSA and Diffie-Hellman encryption raise
numbers to enormous exponents (hundreds of digits) modulo a prime — the naive
"multiply n times" would never finish, so every crypto library uses modular
exponentiation by squaring. Computing a graph's reachability or a Markov chain's
long-run state uses matrix power by squaring. Even Fibonacci in `O(log n)` comes
from raising a 2×2 matrix to a power the same way.

What the good solution buys is turning an `O(n)` loop into `O(log n)` — for an
exponent of two billion, that's the difference between two billion multiplies
and about 31. It also buys correctness on the negative-exponent and
integer-overflow edges that trip up the obvious code.

## Start from the obvious

The definition of a power is "multiply x by itself n times", so write exactly
that:

```
result = 1
for _ in range(abs(n)):
    result *= x
if n < 0: result = 1 / result
```

That's `O(n)`. It's correct and it's the honest first thought — and staring at
what it repeats tells you the fix.

## Find the waste

To get `x^8`, the loop multiplies: `x·x·x·x·x·x·x·x`. But `x^8 = (x^4)^2`, and
`x^4 = (x^2)^2`. The loop recomputes the same partial products the squaring
version could reuse. The waste is treating the exponent as a tally of ones when
it's really a *binary number*.

## The insight

Read the exponent in binary. Keep a running value `current` that starts at `x`
and gets squared each step, so it walks through `x, x^2, x^4, x^8, ...` — the
`x` raised to each power of two. Look at the exponent's binary digits from the
low end: wherever there's a `1`, that power of two is part of the sum in the
exponent, so fold `current` into the answer.

```
result = 1
current = x
while n > 0:
    if n & 1: result *= current   # this power-of-two is present
    current *= current            # x, x^2, x^4, x^8, ...
    n >>= 1                        # consume that binary digit
```

Because `13 = 1101` in binary means `x^13 = x^8 · x^4 · x^1`, we only multiply
in the powers whose bit is set. Negative `n`: replace `x` with `1/x` and make
`n` positive first.

## Complexity

- **Time:** `O(log n)` — the `while` loop runs once per binary digit of `n`, and
  `n` has about `log2(n)` digits.
- **Space:** `O(1)` — a couple of accumulators, no recursion needed.

## Pitfalls

- **Overflow on `-n`.** In C/Java, `n = -2^31` and then `n = -n` overflows,
  because `+2^31` doesn't fit in a signed 32-bit int. Python ints are unbounded
  so it's safe here, but the idiomatic guard is to work with the negation
  carefully (or use a wider type). This problem is *about* that edge.
- Forgetting `x^0 = 1` (the loop handles it: it never runs, result stays 1).
- Doing `1/x` but forgetting to also make `n` positive, or vice versa.
- Recursion depth: a recursive squaring version is fine at `log n` depth, but
  the iterative one avoids the call stack entirely.

## Transfer

The move "halve the exponent by squaring" reappears whenever you repeat an
*associative* operation many times: modular exponentiation in crypto, matrix
power for linear recurrences (Fibonacci, path counts), and repeated function
composition. Sibling problems:
[Sqrt(x) / 69](https://leetcode.com/problems/sqrtx/) (binary search on the
answer) and
[Super Pow / 372](https://leetcode.com/problems/super-pow/) (the same trick
under a modulus).
