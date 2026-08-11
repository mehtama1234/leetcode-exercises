# 125. Valid Palindrome

**Pattern:** Two pointers (compare the two ends inward)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/valid-palindrome/

## The problem in plain words

Throw away everything that isn't a letter or a digit, treat upper- and lowercase
as the same, and ask: does what's left read the same forwards and backwards?
`"A man, a plan, a canal: Panama"` becomes `"amanaplanacanalpanama"`, which reads
the same both ways. Return true or false.

```diagram
   "A man, a plan, a canal: Panama"
        drop spaces/punctuation, lowercase
   ->  "amanaplanacanalpanama"
        a m a n a p ... p a n a m a
        ^ first == last, second == second-to-last, ... all the way in
```

## Why this matters

Strip the wordplay and this is: *check a mirror by comparing paired positions from
both ends inward, while ignoring the pieces that don't count* — and doing it
without building a cleaned-up copy first. It can quit the instant one pair
disagrees.

That "compare from both ends, skip the noise" shape shows up in real checks.
Validating a serial number or code that reads the same after you drop dashes and
spaces. Finding reverse-complement regions in DNA. Confirming two ends of a buffer
agree without allocating a reversed clone.

What you're solving for is memory and early exit. The plain "clean it, reverse it,
compare" is also one pass but builds two throwaway strings. The two-pointer version
drops to constant extra space and stops on the first mismatch.

## Start from the obvious

"Palindrome" means "equals its reverse," so write exactly that: clean the string,
compare it to its own reverse.

```diagram
   kept = [c.lower() for c in s if c is a letter or digit]
   return kept == reversed(kept)
```

Correct and easy to read. But look at what it *builds*: a filtered copy, then a
second reversed copy of that. Two new sequences to answer one yes/no question.

## Find the waste

We never actually need the reversed string as a *thing*. Being a palindrome is a
claim about pairs: character 0 must match the last, character 1 must match the
second-to-last, and so on toward the middle. That's a claim about the two ends,
checked as you move inward.

So instead of building a reversed copy, compare the ends directly. One index at the
far left, one at the far right, stepping toward each other — filtering *while* you
compare.

## The insight

Keep `left` at the start and `right` at the end. Each round: slide `left` right
past any non-letter/digit, slide `right` left past any non-letter/digit, compare
the two lowercased characters, and step both inward.

```diagram
   "0P"                          "race a car"
   0 P                           r a c e   a   c a r
   L R   '0' vs 'p'              L               R    'r' vs 'r'  ok, step in
   -> different -> return False    a c e   a   c a
                                   L           R      'a' vs 'a'  ok
                                     c e   a   c
                                     L       R        'c' vs 'c'  ok
                                       e   a
                                       L   R          'e' vs 'a'  DIFFERENT
                                   -> return False
```

The skipping happens in place — nothing is allocated, so extra space drops to a
handful of integers.

## Complexity

- **Time: about n steps.** Each pointer only moves inward, so together they touch
  each character at most once.
- **Extra memory: constant.** Just two indices; no copies of the string.

The plain version is also one pass, but this trades its scratch string for constant
space and can bail out on the first mismatched pair.

## Pitfalls

- Forgetting to skip non-letter/digit characters on **both** sides — a comma on the
  left will never match a letter on the right.
- Guard the inner skip loops with `left < right` so the pointers don't cross when
  the string is all punctuation.
- The `"0P"` trap: after lowercasing, `'0'` (digit) and `'p'` (letter) are still
  different — case-folding does not merge digits with letters.
- `isalnum()` correctly rejects `_`; a hand-rolled "is letter or digit" check often
  lets underscores through.

## Transfer

Converging two pointers from both ends is the core trick for
[Two Sum II / 167](../0167-two-sum-ii-input-array-is-sorted/) and
[Container With Most Water / 11](../0011-container-with-most-water/), and the "walk
inward comparing mirrored positions, skipping what doesn't count" shape shows up in
palindrome variants like *Valid Palindrome II* (allow one deletion). Reach for it
whenever a question is really about the relationship between the two ends of a
sequence.
