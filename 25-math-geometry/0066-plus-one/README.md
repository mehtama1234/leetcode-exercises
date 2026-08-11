# 66. Plus One

**Pattern:** Carry propagation across a digit array
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/plus-one/

## The problem in plain words

A number is handed to you as a list of its digits, biggest place first — so
`[1, 2, 3]` means one hundred twenty-three. Add one to the number and give back
the new list of digits.

```diagram
   [1][2][3]  + 1  ->  [1][2][4]     easy: last digit had room

   [1][9][9]  + 1  ->  [2][0][0]     carry ripples left through the 9s

   [9][9][9]  + 1  ->  [1][0][0][0]  all nines: the number grows a digit
```

## Why this matters

Numbers bigger than a machine word don't fit in an `int`, so you store them as
arrays of digits and do arithmetic one place at a time — exactly like you add on
paper. The only interesting part is the **carry**: when a place fills past 9, the
extra unit ripples into the next place, and sometimes all the way off the end.

That move runs real systems. Arbitrary-precision integers — Python's own `int`,
Java's `BigInteger`, the math under cryptographic keys — are digit arrays with
carry propagation at their core. A hardware ripple-carry adder does the same
thing in silicon. Odometers and page counters roll `999 -> 1000` the identical
way.

## Start from the obvious

Turn the array into an integer, add one, split it back into digits.

```diagram
   [1,2,3]  ->  123  ->  124  ->  [1,2,4]
```

That's the honest first thought and it works for small inputs — but only *because*
the number happens to fit in a machine int. The whole reason the problem hands you
digits is that the number might be hundreds of digits long, at which point the
shortcut is either impossible or quietly leaning on the big-integer support the
problem wants you to implement yourself.

## The insight

Do the grade-school add directly. Adding one can only affect the digits from the
right until it hits something that isn't a `9`. Walk from the last digit backward:

- If the digit is `< 9`, bump it and stop — no carry escapes, nothing to the left
  changes.
- If it's a `9`, it becomes `0` and the carry moves one place left. Repeat.

```diagram
   [1][9][9]   walk from the right, carrying a +1

   i=2:  9  -> becomes 0, carry left     [1][9][0]
   i=1:  9  -> becomes 0, carry left     [1][0][0]
   i=0:  1  -> < 9, bump to 2, STOP      [2][0][0]
                ^ carry stops here
```

If you walk off the left edge still carrying — the number was all nines — the
answer is one digit longer: a leading `1` in front of all zeros.

```diagram
   [9][9][9]   every digit is 9

   i=2: 9 -> 0, carry     [9][9][0]
   i=1: 9 -> 0, carry     [9][0][0]
   i=0: 9 -> 0, carry     [0][0][0]   fell off the left edge, still carrying
   prepend 1:             [1][0][0][0]
```

## Complexity

- **Time: about n steps** in the worst case — all nines forces a walk across every
  digit. In the common case it stops at the last digit right away.
- **Extra memory: constant** (changing the array in place). The all-nines case
  adds one new leading slot, which is unavoidable — the result genuinely has one
  more digit.

## Pitfalls

- The all-nines grow case (`[9,9,9] -> [1,0,0,0]`) — forgetting the length can
  increase is the classic bug.
- Adding the carry to the *front* of the array instead of the back — the
  least-significant digit is at the end.
- Building a full carry variable when you don't need one: since you only ever add
  one, "digit < 9" already tells you whether the carry continues.

## Transfer

The reusable move is **walk a digit array from the least-significant end,
propagating a carry until it dies.** It generalizes to
[Add Binary / 67](https://leetcode.com/problems/add-binary/) (base 2 instead of
10), [Add Two Numbers / 2](https://leetcode.com/problems/add-two-numbers/) (digits
in a linked list), and [Multiply Strings / 43](../0043-multiply-strings/) (many
carries at once). Whenever a number is too big for a native type, you fall back to
per-digit arithmetic with carries.
