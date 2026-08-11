# 49. Group Anagrams

**Pattern:** Hashing (give each item a name so equal names fall together)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/group-anagrams/

## The problem in plain words

You're given a pile of words. Sort them into groups where every word in a group
is an anagram of the others — same letters rearranged. Return the groups.

```diagram
   ["eat","tea","tan","ate","nat","bat"]

        ["eat","tea","ate"]     (all the letters a,e,t)
        ["tan","nat"]           (all the letters a,n,t)
        ["bat"]                 (a,b,t)
```

## Why this matters

The real task is: *give each word a name that is the same for all its anagrams
and different for everything else, then let a hash map collect words by name.* A
map already groups for free — things with the same key land in the same bucket.
So you never compare word against word; you compute one name per word.

This shape shows up constantly. Deduplication systems fingerprint each file with
a content hash, so identical files collapse no matter what they're named. Record
cleanup pipelines normalize a record — lowercase it, strip punctuation, sort the
fields — before hashing, so "the same customer entered twice" merges. Compilers
reduce an expression like `a+b` to a canonical form so it and `b+a` share one
node. Near-duplicate image detection maps each picture to a signature and groups
by it.

What you're saving is the messy work of comparing every pair and merging the
matches. Compute one key per item and the map does the clustering.

## Start from the obvious

The naive read is "compare every word against every other word to see if they're
anagrams," then stitch matches into groups. That's about n × n comparisons plus
fiddly merge bookkeeping.

Step back. Grouping is what a hash map does for you: same key, same bucket. So the
real problem isn't comparing pairs — it's finding a **name that's identical for
anagrams and different for everything else.**

## Find the waste

From [Valid Anagram / 242](../0242-valid-anagram/) you know two words are anagrams
exactly when they share the same letters and counts. So any name that depends only
on the letters-and-counts works as a key.

The easy name is the **sorted word**: `"tea"` and `"eat"` both sort to `"aet"`.
Bucket by that.

```diagram
   word     sorted key     bucket
   ----     ----------     ------
   "eat"      "aet"    ->  aet: ["eat"]
   "tea"      "aet"    ->  aet: ["eat","tea"]
   "tan"      "ant"    ->  ant: ["tan"]
   "ate"      "aet"    ->  aet: ["eat","tea","ate"]
   "bat"      "abt"    ->  abt: ["bat"]
```

That's correct at about n × k log k for n words of length k. The only waste left
is the sort inside each word — it fully orders k letters when, again, you only
need their counts.

## The insight

Replace the sorted string with a **count signature**: 26 numbers saying how many
a's, b's, … the word has. Anagrams produce identical signatures, and building one
is a single pass with no sorting.

```diagram
   "tea"                       "eat"
   a b c d e ... t ...         a b c d e ... t ...
   1 0 0 0 1     1             1 0 0 0 1     1
   \_____ same 26-number key _____/   ->  same bucket
```

A list can't be a dictionary key, so store the 26 numbers as a tuple (a fixed,
unchangeable list). Now each word is filed in about k steps instead of k log k.

## Complexity

- **Time: about n × k** for the count-signature version (n words, length k); the
  sorted-key version is about n × k log k.
- **Extra memory: about n × k** to hold all the words in their buckets.

## Pitfalls

- Using a plain **list** as a dict key throws — lists can change, so they can't be
  keys. Convert to a `tuple` (or a string) first.
- The 26-slot signature bakes in "lowercase a–z only." For a wider alphabet, key
  by the sorted string or a set/dict of counts instead.
- The empty string `""` is a valid word and its own group — don't drop it.
- The order of the groups, and of words within a group, doesn't matter; the test
  normalizes both sides before comparing.

## Transfer

The move is **map each item to a canonical name, then let a dict do the
grouping.** It reaches far past anagrams: group points by slope, group numbers by
remainder, dedupe shapes by a normalized form. Whenever "these belong together if
some derived key matches," compute the key and bucket. Builds directly on
[Valid Anagram / 242](../0242-valid-anagram/).
