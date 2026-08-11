# 17. Letter Combinations of a Phone Number

**Pattern:** Backtracking (Cartesian product — one choice per position)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/letter-combinations-of-a-phone-number/

## The problem in plain words

On the old phone keypad, each digit maps to letters: `2`→`abc`, `3`→`def`, and so
on. Given a string of digits like `"23"`, spell out every word you can make by
choosing one letter for each digit. `"23"` gives `ad, ae, af, bd, be, bf, cd, ce,
cf` — nine words. Empty input gives an empty answer.

## Why this matters

This is the **Cartesian product** made concrete: independent choice-sets, one per
position, and you want every way to pick one from each. If digit 1 offers 3
letters and digit 2 offers 3, there are `3 × 3 = 9` outcomes; the total is the
product of the per-position counts. Recognizing a problem as "a product of
independent choices" tells you the answer size up front and hands you the loop
structure for free.

Products-of-choices are the honest shape of many generators. Expanding a template
with several `{a|b|c}`-style slots, enumerating a test matrix where each parameter
has a few values, generating SKU variants from options (size × color × material),
building every path through a small branching config — all are "one choice per
slot, take every combination."

What backtracking buys over nested loops is that the number of slots (`len(digits)`)
is only known at runtime, so you can't hand-write the loops — recursion gives you a
loop-per-level automatically, at `O(depth)` memory.

## Start from the obvious

You can't write `n` nested `for` loops when `n` varies, but you can grow the set
one digit at a time: keep the words-so-far, and for each new digit replace each
word with every extension of it.

```
words = [""]
for d in digits:
    words = [w + ch for w in words for ch in keypad[d]]
```

That's honest and correct, and it makes the product visible — each digit multiplies
the count by that key's letter count. Backtracking is the same computation phrased
as a recursive tree, which makes the "choose / explore / un-choose" spine explicit
and keeps only one partial word in memory at a time.

## The insight

Model it as a decision tree whose **depth is the number of digits** and whose
**branches at level `i` are the letters of `digits[i]`**. Walk it with the standard
template:

1. **Choose** — append one letter for the current digit to `path`.
2. **Explore** — recurse to the next digit.
3. **Un-choose** — pop that letter so the sibling letter can take its place.

A leaf (path length equals the digit count) is one finished word; record it.
There's nothing to prune — every path down the tree spells a legal word — so this
is the pure product with no dead branches. The only twist versus the numeric
problems is that the choices at each level come from a fixed **lookup table**
(`KEYPAD`) rather than the input array.

## Complexity

- **Time:** `O(4^n * n)` where `n = len(digits)`. Digits `7` and `9` each offer 4
  letters, so the number of words is at most `4^n`; building each `n`-length string
  costs `O(n)`.
- **Space:** `O(n)` extra — the recursion is `n` deep and `path` holds `n`
  characters. The result list is the required output, `O(4^n * n)`.

## Pitfalls

- **Empty input.** LeetCode wants `[]`, *not* `[""]`. Guard it explicitly — the
  recursion would otherwise emit one empty string.
- **Reusing a mutable `path` without joining/copying** at the leaf — append
  `"".join(path)`, a fresh string, so later mutations don't corrupt stored words.
- Assuming exactly 3 letters per key — `7` (`pqrs`) and `9` (`wxyz`) have 4, which
  is why the bound is `4^n`, not `3^n`.

## Transfer

The "one independent choice per position, take the product" shape recurs whenever
slots are filled independently: generating all IP-address splits, expanding brace
patterns, and any config/template matrix. When each position's choices don't depend
on earlier picks, it's a Cartesian product — reach for this level-per-position
recursion (or nested loops if the depth is fixed and small).
