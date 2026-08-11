# 66. Plus One

**Pattern:** Digit-array arithmetic (carry propagation)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/plus-one/

## The problem in plain words

A number is handed to you as a list of its digits, biggest place first — so
`[1, 2, 3]` means one hundred twenty-three. Add one to the number and give back
the new list of digits. `[1,2,3] → [1,2,4]`, but `[9,9] → [1,0,0]`.

## Why this matters

Underneath the puzzle is the fact that *numbers bigger than a machine word don't
fit in an `int`, so you store them as arrays of digits and do arithmetic one
place at a time* — exactly like you add on paper. The only interesting part is
the **carry**: when a place overflows, the extra unit ripples into the next
place, and sometimes all the way off the end.

That exact move runs real systems. Arbitrary-precision integers (Python's own
`int`, Java's `BigInteger`, cryptographic key math) are digit/limb arrays with
carry propagation at their core. Incrementing a version or sequence counter
stored as digits, or a hardware ripple-carry adder, is this same operation. Odometers
and page counters roll over `999 → 1000` the identical way.

What the good solution buys is doing the add in a **single backward pass with
constant extra space**, and — crucially — handling the case where the number
grows a digit (`999 → 1000`) without special-casing every length.

## Start from the obvious

You might reach for "turn the array into an integer, add one, split back into
digits":

```
n = int("".join(map(str, digits))) + 1
return [int(c) for c in str(n)]
```

That's the honest first thought and it works for small inputs — but it only
works *because* the number happens to fit in a machine int. The whole reason the
problem hands you digits is that the number might be hundreds of digits long, at
which point that shortcut is either impossible or is quietly leaning on
big-integer support the problem wants you to implement yourself.

## The insight

Do the grade-school add directly. Adding one can only affect the digits from the
right until it hits something that isn't a `9`:

- Start at the last digit. If it's `< 9`, add one and stop — no carry escapes,
  so nothing to the left changes.
- If it's a `9`, it becomes `0` and the carry moves one place left. Repeat.

If you walk off the left edge still carrying (the number was all nines), the
answer is one digit longer: prepend a `1`.

```
for i from last down to 0:
    if digits[i] < 9: digits[i] += 1; return digits
    digits[i] = 0
return [1] + digits
```

## Complexity

- **Time:** `O(n)` worst case — all nines forces a walk across every digit. In
  the common case it stops at the last digit in `O(1)`.
- **Space:** `O(1)` extra (mutating in place). The all-nines case allocates one
  new leading slot, which is unavoidable since the result genuinely has one more
  digit.

## Pitfalls

- **The all-nines grow case** (`[9,9,9] → [1,0,0,0]`) — forgetting the length
  can increase is the classic bug.
- Adding the carry to the *front* of the array instead of the back — remember
  the least-significant digit is at the end.
- Building a whole carry variable when you don't need one: since you only ever
  add one, "digit < 9" is enough to decide whether the carry continues.

## Transfer

Carry propagation over a digit array is the reusable core. It generalizes to
[Add Binary / 67](https://leetcode.com/problems/add-binary/) (base 2 instead of
10),
[Add Two Numbers / 2](https://leetcode.com/problems/add-two-numbers/) (digits in
a linked list, least-significant first), and
[Multiply Strings / 43](../0043-multiply-strings/) (many carries at once).
Whenever a number is too big for a native type, you fall back to per-digit
arithmetic with carries.
