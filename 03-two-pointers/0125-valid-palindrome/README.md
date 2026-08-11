# 125. Valid Palindrome

**Pattern:** Two pointers (converging from both ends)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/valid-palindrome/

## The problem in plain words

Throw away everything that isn't a letter or a digit, treat upper- and lowercase
as the same, and ask: does what's left read the same forwards and backwards?
So `"A man, a plan, a canal: Panama"` becomes `"amanaplanacanalpanama"`, which is
a palindrome. Return true/false.

## Start from the obvious

The word "palindrome" literally means "equals its reverse", so turn that straight
into code: clean the string, then compare it to its own reverse.

```
kept = [c.lower() for c in s if c.isalnum()]
return kept == kept[::-1]
```

That's correct and easy to read. It's `O(n)` time — but look at what it *builds*:
a filtered copy of the string, and then a second reversed copy of that. We create
two new sequences just to answer a single yes/no question.

## Find the waste

We never actually need the reversed string as a *thing*. Being a palindrome is a
statement about pairs: character 0 must match the last character, character 1
must match the second-to-last, and so on toward the middle. That's a claim about
the two ends, checked repeatedly as you move inward.

So instead of materializing a reversed copy and comparing, compare the ends
directly. That's the two-pointer move: one index at the far left, one at the far
right, stepping toward each other.

## The insight

Keep a `left` index at the start and a `right` index at the end. Each round:

1. Slide `left` rightward past any non-alphanumeric character.
2. Slide `right` leftward past any non-alphanumeric character.
3. Compare the two lowercased characters they land on. If they differ, return
   false immediately.
4. Step both inward and repeat until they meet.

The skipping happens in place — we filter *while* we compare instead of building
a filtered string first. Nothing is allocated, so the extra space drops to `O(1)`.

## Complexity

- **Time:** `O(n)` — each pointer moves inward only, so together they touch each
  character at most once.
- **Space:** `O(1)` — just two integer indices; no copies of the string.

The naive version is also `O(n)` time, but this trades its `O(n)` scratch space
for constant space, and it can bail out early on the first mismatched pair.

## Pitfalls

- Forgetting to skip non-alphanumeric characters on **both** sides — a comma on
  the left will never match a letter on the right.
- Guarding the inner skip loops with `left < right` so the pointers don't cross
  past each other when the string is all punctuation.
- The `"0P"` trap: after lowercasing, `'0'` (digit) and `'p'` (letter) are still
  different — case-folding does not merge digits with letters.
- Treating characters like `_` as "part of a word": `isalnum()` correctly rejects
  underscores; a hand-rolled "is letter or digit" check often gets this wrong.

## Transfer

Converging two pointers from both ends is the core trick for
[Two Sum II / 167](../0167-two-sum-ii-input-array-is-sorted/) and
[Container With Most Water / 11](../0011-container-with-most-water/), and the
"walk inward comparing mirrored positions, skipping what doesn't count" shape
shows up in palindrome variants like *Valid Palindrome II* (allow one deletion).
Reach for it whenever a question is really about the relationship between the two
ends of a sequence.
