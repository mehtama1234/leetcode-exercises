# 7. Reverse Integer

**Pattern:** Digit manipulation with fixed-width overflow guarding
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/reverse-integer/

## The problem in plain words

Take a signed integer and reverse its digits: `123 → 321`, `-123 → -321`,
`120 → 21` (the trailing zero vanishes). But the result must fit in a signed
32-bit integer — the range `-2147483648 … 2147483647`. If reversing pushes it
outside that range, return `0`.

## Why this matters

Underneath the puzzle is a truth every systems programmer lives with: *machine
integers have a fixed width, and arithmetic that steps past the top wraps around
silently into a wrong (often negative) answer.* The skill being tested is
detecting overflow **before** it corrupts your value, not after.

That exact concern runs real systems. C, Java, Go, and Rust all have fixed-width
ints; a bounds check that comes one operation too late is a genuine bug class —
the Ariane 5 rocket was lost to an integer overflow, and signed-overflow
undefined behavior is a perennial source of security holes. Parsing untrusted
numeric input (a length field, a price, a timestamp) means validating the range
as you build the number. Hashing and checksums deliberately let ints wrap, so
you have to know exactly when it happens.

What the good solution buys is a **pre-emptive check** — comparing against
`INT_MAX / 10` before you multiply — so you never actually compute the
out-of-range value. In a real fixed-width language, computing it first is
already too late; the bits are gone.

## Start from the obvious

In a language with big integers (like Python) the naive idea is: flip it to a
string, reverse, parse back, reattach the sign, then check the range at the end:

```
r = int(str(abs(x))[::-1]) * sign
return r if INT_MIN <= r <= INT_MAX else 0
```

This *works in Python* only because Python ints never overflow, so the
"compute then check" is safe. It's the honest first thought — but it dodges the
actual lesson, because in C or Java that intermediate result would already have
wrapped before your check ran.

## The insight

Build the reversed number digit by digit, and check for overflow *before* each
multiply. Peel the last digit with `divmod(x, 10)`, then push it:
`result = result * 10 + digit`. The dangerous step is `result * 10 + digit`, so
guard it:

```
if result > LIMIT // 10 or (result == LIMIT // 10 and digit > LIMIT % 10):
    return 0
result = result * 10 + digit
```

If `result` already exceeds `LIMIT // 10`, then `result * 10` alone blows the
limit. If it *equals* `LIMIT // 10`, only the final digit decides it — compare
against `LIMIT % 10` (the last digit of the limit, `7` for `2147483647`). We
work with the magnitude and reapply the sign at the end, using `2**31` as the
limit for negatives and `2**31 - 1` for positives.

## Complexity

- **Time:** `O(d)` where `d` is the digit count — at most 10 for a 32-bit int.
- **Space:** `O(1)` — just the running `result` and the sign.

## Pitfalls

- **Checking overflow after the fact** — in a fixed-width language the value has
  already wrapped, so the check must come *before* the multiply.
- **The asymmetric range** — `INT_MIN` (`-2147483648`) has a larger magnitude
  than `INT_MAX` (`2147483647`), so `abs(INT_MIN)` itself overflows in C/Java.
  Use the correct limit per sign.
- **Trailing zeros** — `divmod`/`* 10` handles them for free (`120 → 21`); don't
  special-case them.
- **The tie case** — when `result == LIMIT // 10`, you must compare the incoming
  digit against `LIMIT % 10`, not just bail or just proceed.

## Transfer

The pre-multiply overflow guard is the reusable core, and it's exactly what a
safe string-to-int parser needs:
[String to Integer (atoi) / 8](https://leetcode.com/problems/string-to-integer-atoi/)
uses the identical `result > LIMIT/10` check. Digit-peeling by `divmod(_, 10)`
also drives
[Palindrome Number / 9](../0009-palindrome-number/) and
[Add Digits / 258](https://leetcode.com/problems/add-digits/).
