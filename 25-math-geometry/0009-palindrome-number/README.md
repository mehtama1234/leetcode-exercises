# 9. Palindrome Number

**Pattern:** Digit manipulation (reverse half to avoid overflow)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/palindrome-number/

## The problem in plain words

Does the number read the same forwards and backwards? `121` yes, `12321` yes,
`123` no. Negative numbers are always "no" (the minus sign has nothing to pair
with at the other end). And you're asked to do it *without* turning the number
into a string.

## Why this matters

Underneath the puzzle is a small but real discipline: *working with a number's
digits using only arithmetic — `% 10` to read the last digit, `// 10` to drop
it — instead of leaning on string conversion.* That matters when strings aren't
available or cheap: embedded firmware, tight numeric kernels, or any place
where allocating a string per check is wasteful.

The sharper lesson is the **overflow-avoidance** move. The obvious solution
reverses the whole number and compares, but the reversed value can exceed a
fixed-width integer even when the input fits — the same trap as Reverse Integer.
The better solution reverses only the back half, so it never builds a number
bigger than half the digits. That "only process half, meet in the middle" idea
recurs whenever you compare a sequence to its mirror.

What the good solution buys is **no risk of overflow** and an early stop: you're
done after processing about half the digits, not all of them.

## Start from the obvious

Reverse the whole number and check if it equals the original:

```
if x < 0: return False
rev = 0
t = x
while t > 0:
    t, d = divmod(t, 10)
    rev = rev * 10 + d
return rev == x
```

Correct and clear. The honest first thought — and it exposes the weakness: in a
fixed-width language `rev` can overflow for a large `x` whose reverse doesn't fit,
even though `x` itself is fine.

## Find the waste

You don't need the *whole* reversed number to decide symmetry. A palindrome's
front half mirrors its back half — so if you rebuild just the back half and
compare it to what's left of the front, that's enough. Building only half the
digits means the reversed value stays small: it can never overflow.

## The insight

Peel digits off the **end** of `x` and grow `reversed_half`, while `x` shrinks
from the front. Stop when `x <= reversed_half` — that's the moment they cross in
the middle.

```
if x < 0 or (x % 10 == 0 and x != 0): return False   # negatives and trailing 0
reversed_half = 0
while x > reversed_half:
    x, d = divmod(x, 10)
    reversed_half = reversed_half * 10 + d
return x == reversed_half or x == reversed_half // 10
```

- **Even digit count** (`1221`): the loop ends with `x == 12` and
  `reversed_half == 12` → equal.
- **Odd digit count** (`12321`): the middle digit ends up alone in
  `reversed_half`; drop it with `reversed_half // 10` so `x == 12 == 123//... `.
- The upfront guard rejects any number ending in `0` (except `0` itself), since
  its reverse would have a leading zero and can't match.

## Complexity

- **Time:** `O(d)` where `d` is the digit count — and we only process about
  `d/2` of them.
- **Space:** `O(1)` — two integers.

## Pitfalls

- **Negatives** — always false; the sign has no mirror.
- **Trailing zero** — `10`, `120`, `1000021` are not palindromes; only `0`
  itself ends in `0` and passes. Guard this up front.
- **Odd vs even length** — forgetting the `reversed_half // 10` correction for
  the lone middle digit is the classic bug.
- **Full reversal overflow** — the whole-number reverse can overflow a
  fixed-width int; reversing only half sidesteps it entirely.

## Transfer

The "reverse via `% 10` / `// 10`" digit loop is shared with
[Reverse Integer / 7](../0007-reverse-integer/). The "compare a sequence to its
mirror, meeting in the middle" idea is the numeric cousin of the two-pointer
string check in
[Valid Palindrome / 125](https://leetcode.com/problems/valid-palindrome/) and
[Palindrome Linked List / 234](https://leetcode.com/problems/palindrome-linked-list/).
