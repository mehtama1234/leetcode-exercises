# 7. Reverse Integer

**Pattern:** Digit-by-digit math with an overflow guard
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/reverse-integer/

## The problem in plain words

Take a whole number, possibly negative, and flip its digits end to end. `123`
becomes `321`; `-123` becomes `-321`; `120` becomes `21` (the leading zero of the
reversed form just vanishes). One catch: pretend you are on a machine where
numbers only hold 32 bits, so they can't go past about 2.1 billion. If the
flipped number would blow past that limit, return `0`.

```diagram
     123                 -123               120
   [1][2][3]           -[1][2][3]         [1][2][0]
        |  flip             |  flip            |  flip
        v                   v                  v
   [3][2][1] = 321     -[3][2][1] = -321   [0][2][1] = 21
                                            ^ leading 0 drops off
```

## Why this matters

The real lesson here isn't "reverse a number." It's *how do you catch a number
growing too big before it actually does?* On a fixed-width machine, once a value
crosses its ceiling it silently wraps to garbage. You can't check the result
after the fact — the result is already wrong. You have to look one step ahead.

That "test before you commit" habit runs real systems. A bank ledger checks
whether an add would overflow the account field before writing it. A network
counter guards against wrapping a sequence number. Any time a value has a hard
ceiling and passing it corrupts data instead of raising an error, the fix is the
same: predict the overflow from the current state, not from the broken result.

## Start from the obvious

The easy idea: turn the number into text, flip the text, turn it back.

```diagram
   123  ->  "123"  ->  "321"  ->  321
```

This works in a language like Python where integers grow without limit. But it
sidesteps the whole point of the exercise — the 32-bit ceiling. On a real
fixed-width machine you can't lean on unlimited integers, and the text trick also
hides *where* the overflow would happen. We want to build the answer with plain
arithmetic so the danger is out in the open.

## The insight

Peel digits off the back of the number one at a time, and glue each onto the back
of a growing answer. Pull the last digit with divide-and-remainder by 10; push it
on with `answer * 10 + digit`.

```diagram
   x = 123        answer = 0

   x=123  ->  x=12,  digit=3   ->  answer = 0*10 + 3  =   3
   x=12   ->  x=1,   digit=2   ->  answer = 3*10 + 2  =  32
   x=1    ->  x=0,   digit=1   ->  answer = 32*10 + 1 = 321
                                            ^ each step shifts left, drops in digit
```

Now the overflow guard. The reversed value can spill past the ceiling even when
the input fit fine: reversing `1000000003` gives `3000000001`, past the ~2.1
billion limit. The trick is to check *before* the `answer * 10 + digit` step
whether that step would cross the line. The ceiling is `2147483647`, so:

```diagram
   about to do:  answer * 10 + digit
   ceiling // 10 = 214748364   (its last digit is 7)

   if answer  >  214748364              -> *10 already overflows -> return 0
   if answer == 214748364 and digit > 7 -> tie, and this digit pushes over -> 0
   otherwise                            -> safe, do answer = answer*10 + digit
```

You handle the sign by working on the positive size of the number and reattaching
the minus at the end, so the digit math stays uniform.

## Complexity

- **Time: about d steps**, where d is the number of digits (at most 10 for a
  32-bit number). One pass, one cheap check per digit.
- **Extra memory: constant.** A couple of integers, nothing that grows with the
  input.

## Pitfalls

- Checking for overflow *after* building the too-big number. On a real
  fixed-width machine that number is already corrupt — you must look ahead.
- Forgetting that the negative range reaches one further (`-2147483648`) than the
  positive range (`2147483647`).
- Losing the sign. Reverse the magnitude, then put the minus back.

## Transfer

The reusable move is **peel a digit with `divmod` by 10, and guard a
fixed-width limit by predicting the overflow one step early.** The same
digit-peeling drives [Palindrome Number / 9](../0009-palindrome-number/) and
[Happy Number / 202](../0202-happy-number/), and the "check before you commit"
guard shows up anywhere a counter or accumulator has a hard ceiling.
