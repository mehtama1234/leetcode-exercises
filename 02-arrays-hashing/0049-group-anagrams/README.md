# 49. Group Anagrams

**Pattern:** Hashing (canonical key / signature)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/group-anagrams/

## The problem in plain words

You're given a pile of words. Sort them into groups where every word in a group
is an anagram of the others — same letters rearranged. Return the groups.

## Start from the obvious

The naive read is "compare every word against every other word to see if they're
anagrams," then stitch the matches into groups. That's `O(n^2)` comparisons plus
the bookkeeping of merging matches — fiddly and slow.

Step back. Grouping is what a hash map does for free: things with the *same key*
land in the same bucket. So the real problem isn't comparing pairs — it's finding
a key that is **identical for anagrams and different for everything else**.

## Find the waste

From [Valid Anagram / 242](../0242-valid-anagram/) we know two words are anagrams
exactly when they share the same letters and counts. So any "canonical name" that
depends only on the multiset of letters works as a key.

The easy canonical name is the **sorted word**: `"tea"` and `"eat"` both sort to
`"aet"`. Bucket by that:

```
key = "".join(sorted(word))
buckets[key].append(word)
```

That's clean and correct at `O(n * k log k)` for `n` words of length `k`. The
only waste left is the sort — it fully orders `k` letters when, again, we only
need their counts.

## The insight

Replace the sorted string with the **count signature**: a tuple of 26 numbers
saying how many a's, b's, … the word has. Anagrams have identical signatures, and
building one is a single linear pass with no sorting:

```
counts = [0]*26
for ch in word: counts[ord(ch) - ord('a')] += 1
key = tuple(counts)   # tuples are hashable, lists aren't
```

Now each word is bucketed in `O(k)` instead of `O(k log k)`.

## Complexity

- **Time:** `O(n * k)` for the count-signature version (`n` words, length `k`);
  the sort-key version is `O(n * k log k)`.
- **Space:** `O(n * k)` to hold all the words in their buckets.

## Pitfalls

- Using a **list** as a dict key throws — lists aren't hashable. Convert to a
  `tuple` (or a string) first.
- The `[0]*26` signature bakes in the "lowercase a–z only" constraint. For a
  wider alphabet, key by the sorted string or a `frozenset`/dict of counts.
- The empty string `""` is a valid word and its own anagram group — don't drop it.
- The output order (of groups, and within a group) doesn't matter; the test
  normalizes both sides before comparing.

## Transfer

The move here is **"map each item to a canonical signature, then let a dict do
the grouping."** It generalizes far beyond anagrams: group points by slope,
group numbers by remainder, dedupe shapes by a normalized form. Whenever "these
belong together if some derived key matches," compute the key and bucket.
Directly builds on [Valid Anagram / 242](../0242-valid-anagram/).
