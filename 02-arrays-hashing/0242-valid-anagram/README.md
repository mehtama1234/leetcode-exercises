# 242. Valid Anagram

**Pattern:** Hashing (frequency count)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/valid-anagram/

## The problem in plain words

Two strings are anagrams if you can rearrange one into the other — same letters,
same number of each, just shuffled. Given `s` and `t`, is `t` a rearrangement of
`s`?

## Why this matters

The deeper problem is *comparing two multisets — "same elements, same counts,
order irrelevant" — by counting instead of sorting.* The fundamental operation is
building a frequency signature and checking two signatures agree.

Frequency counting is one of the most reused primitives in data work. Word-count
and term-frequency tables are the first step in search indexing and every
bag-of-words ML feature pipeline. Comparing two documents or datasets for "same
contents, different order" — reconciling two exports, checking a shuffled file
transferred intact — is multiset equality. Histograms for anomaly detection
(did today's traffic mix match yesterday's?) are the same tally.

What you're solving for is avoiding the O(n log n) cost of sorting when you only
need counts, not order. Counting is O(n) time and O(1) space for a fixed
alphabet, and the tally can bail early the moment a count goes wrong.

## Start from the obvious

If both strings hold the same letters, then sorting each one lines those letters
up in the same order. So sort both and compare:

```
return sorted(s) == sorted(t)
```

That's correct and only a line. It costs `O(n log n)` because sorting fully
orders the letters. That's the clue: we're computing *more* than the question
asks.

## Find the waste

We don't care what order the letters end up in — we only care *how many* of each
there are. "Same letters, same counts" is the whole definition. Sorting produces
a full ordering as a side effect and throws it away. Skip the ordering and count
directly.

## The insight

Use one map from letter to a running tally. Add `+1` for every letter in `s`,
then `-1` for every letter in `t`. If the two strings are anagrams, every letter
was added exactly as many times as it was subtracted, so every count lands back
at zero.

```
for ch in s: counts[ch] += 1
for ch in t: counts[ch] -= 1
anagram  ⇔  every count == 0
```

A length check up front is a free early exit: strings of different lengths can
never be anagrams.

## Complexity

- **Time:** `O(n)` — two linear passes and a final scan of the counts.
- **Space:** `O(1)` for a fixed alphabet (26 lowercase letters cap the map);
  `O(k)` for an alphabet of `k` distinct characters in general.

Beats the sort's `O(n log n)` because we never order anything.

## Pitfalls

- Forgetting the length check — without it, `("a", "aa")` needs the count scan to
  reject it; with it you bail instantly.
- Assuming lowercase-only. If Unicode or uppercase is allowed, the count map
  still works unchanged; a fixed 26-slot array does not.
- Going negative mid-pass means `t` has a letter `s` can't cover — you can return
  False right there instead of finishing the loop.

## Transfer

"Turn a string into its letter-count signature" is the core trick, and it scales:
in [Group Anagrams / 49](../0049-group-anagrams/) that signature becomes a
dictionary *key* so all anagrams collapse to the same bucket. The general idea —
compare multisets by counting, not sorting — shows up wherever "same elements,
order irrelevant" is the real question.
