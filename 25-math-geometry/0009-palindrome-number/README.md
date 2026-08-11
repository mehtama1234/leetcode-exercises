# 9. Palindrome Number

**Pattern:** Reverse only half the digits and meet in the middle
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/palindrome-number/

## The problem in plain words

Does a number read the same forwards and backwards? `121` does. `-121` does not
(the minus sign has no partner on the other end). `10` does not (backwards it
would be `01`, which is just `1`). Answer yes or no — and do it without turning
the number into text.

```diagram
    1 2 1                 1 2 3 2 1
    ^   ^  same           ^       ^  same
      ^   middle alone      ^   ^  same
                              ^   middle alone
    -> palindrome         -> palindrome

    1 2                   1 0
    ^ ^  differ           ^ ^  differ
    -> no                 -> no
```

## Why this matters

The plain question is symmetry: does the front half mirror the back half? The
lazy way is to build the entire reversed number and compare. But that reversed
number can overflow a fixed-width integer even when the original is fine — and it
does twice the work you need. The real insight is that you only ever need *half*
the digits to decide.

Working from both ends toward the middle is a shape that shows up everywhere:
checking a DNA strand reads the same both ways, validating that a message and its
mirror match, comparing the start of a buffer against its reversed tail. Building
half and stopping at the midpoint is the memory-cheap, overflow-safe version of
that check.

## Start from the obvious

Reverse the whole number and compare to the original.

```diagram
   x = 1221        reversed = 0

   pull 1 -> reversed = 1
   pull 2 -> reversed = 12
   pull 2 -> reversed = 122
   pull 1 -> reversed = 1221

   1221 == 1221  ->  palindrome
```

This is correct and readable. Two costs, though. It touches every digit even
though the two halves carry the same information. And the reversed value can grow
past the machine's integer ceiling — for a wide number, the full reversal
overflows while a half never would.

## The insight

Reverse only the *back* half while chopping digits off the *front*. When the
shrinking front is no longer bigger than the growing back, the two have met in
the middle — that's the moment to compare.

```diagram
   x = 1221        back = 0        (loop while x > back)

   x=1221, back=0   -> pull 1 -> x=122,  back=1
   x=122,  back=1   -> pull 2 -> x=12,   back=12
   x=12,   back=12  -> stop: x is no longer > back

   even length: front (12) == back (12)  ->  palindrome
```

For an odd count of digits, the middle digit ends up stuck on the back half.
Drop it by an integer divide by 10 before comparing:

```diagram
   x = 12321       back = 0

   pull 1 -> x=1232, back=1
   pull 2 -> x=123,  back=12
   pull 3 -> x=12,   back=123     now x (12) <= back (123), stop
                                  middle digit 3 is stuck on back
   compare front to back//10:  12 == 123//10 == 12  ->  palindrome
```

Two quick pre-checks keep it clean: a negative number is never a palindrome, and
any nonzero number ending in `0` can't be one either (its reverse would start
with `0`).

## Complexity

- **Time: about d steps**, where d is the number of digits — and you only walk
  half of them before the loop stops.
- **Extra memory: constant.** A couple of integers. The half you build never
  overflows the way a full reversal can.

## Pitfalls

- Forgetting the odd-length case, where the lone middle digit must be dropped
  with `back // 10` before comparing.
- Not filtering out numbers that end in `0` (except `0` itself), like `10` or
  `120`.
- Reversing the whole number when half is enough — it works, but it can overflow
  on a fixed-width machine.

## Transfer

The reusable move is **process from both ends toward the middle, and stop once
they meet instead of doing the full pass.** The same meeting-in-the-middle shape
drives [Valid Palindrome / 125](https://leetcode.com/problems/valid-palindrome/)
and any two-pointer symmetry check, and the digit-peeling shares its machinery
with [Reverse Integer / 7](../0007-reverse-integer/).
