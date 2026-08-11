# 242. Valid Anagram

**Pattern:** Hashing (count each letter instead of ordering them)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/valid-anagram/

## The problem in plain words

Two strings are anagrams if you can rearrange one into the other — same letters,
same number of each, just shuffled. Given `s` and `t`, is `t` a rearrangement of
`s`?

```diagram
      s = "anagram"        a:3  n:1  g:1  r:1  m:1
      t = "nagaram"        a:3  n:1  g:1  r:1  m:1
                           ^ every count matches  ->  answer: true
```

## Why this matters

Order is a distraction here. What you actually compare is *how many of each
letter* each string has. Two collections are the same when the tallies match,
whatever order the items came in. Learning to compare by counting — not by
lining things up — is the whole lesson.

Counting how often each thing appears is one of the most reused steps in data
work. Word-count tables are the first step in search indexing and in turning text
into features for machine learning. Checking that two exports hold the same
records in a different order, or that a shuffled file arrived intact, is a "same
contents, order irrelevant" test. Traffic histograms for spotting anomalies —
does today's mix of requests match yesterday's? — are the same tally.

What you're avoiding is the cost of sorting when you only need counts. Sorting
fully orders the letters and then you throw the order away; counting skips
straight to the answer.

## Start from the obvious

If both strings hold the same letters, sorting each one lines those letters up
the same way. So sort both and compare.

```diagram
   s = "rat"   -> sorted -> "art"
   t = "car"   -> sorted -> "acr"
                            "art" != "acr"  ->  false
```

This is correct and it's one line. It costs about n log n — n steps times a small
factor that grows as the string gets longer — because sorting fully orders every
letter. That's the clue: you're computing *more* than the question asks for.

## Find the waste

You don't care what order the letters end up in. You only care *how many* of each
there are — "same letters, same counts" is the whole definition. Sorting produces
a full ordering as a side effect and then discards it. Skip the ordering and
count directly.

## The insight

Use one map from letter to a running tally. Add `+1` for every letter in `s`,
then `-1` for every letter in `t`. If the two strings are anagrams, each letter
was added exactly as many times as it was subtracted, so every count lands back
at zero.

```diagram
   s = "aab"   t = "aba"       counts start empty

   +s:  a:+1 a:+1 b:+1   ->   { a:2,  b:1 }
   -t:  a:-1 b:-1 a:-1   ->   { a:0,  b:0 }
                                  ^     ^
                        every count back to zero  ->  true
```

A length check up front is a free early exit: strings of different lengths can
never be anagrams. And if a count ever drops below zero mid-pass, `t` has a
letter `s` couldn't cover — you can answer false right there.

## Complexity

- **Time: about n steps.** Two straight passes plus a final scan of the counts.
- **Extra memory: a fixed small amount** for lowercase-only input (26 letters cap
  the map). For a general alphabet of `k` distinct characters it's about k.

Beats the sort's n log n because you never order anything.

## Pitfalls

- Forgetting the length check — without it, `("a", "aa")` needs the full count
  scan to reject; with it you bail instantly.
- Assuming lowercase-only. If Unicode or uppercase is allowed, the count map
  still works unchanged; a fixed 26-slot array does not.
- Going negative mid-pass means `t` has a letter `s` can't supply — return false
  right there instead of finishing the loop.

## Transfer

**Turn a string into its letter-count signature** is the core move, and it
scales: in [Group Anagrams / 49](../0049-group-anagrams/) that same signature
becomes a dictionary *key*, so all anagrams fall into one bucket. The general
idea — compare collections by counting, not sorting — shows up wherever "same
elements, order irrelevant" is the real question.
