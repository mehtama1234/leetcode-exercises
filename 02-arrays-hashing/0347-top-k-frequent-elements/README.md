# 347. Top K Frequent Elements

**Pattern:** Hashing + bucket by count (place items by score instead of sorting)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/top-k-frequent-elements/

## The problem in plain words

Given a list of numbers, find the `k` values that show up the most. If `k` is 2,
`1` appears three times, and `2` appears twice, the answer is `[1, 2]`.

```diagram
   nums = [1,1,1,2,2,3]     k = 2

   counts:   1 -> 3
             2 -> 2
             3 -> 1
   two biggest counts  ->  [1, 2]
```

## Why this matters

Two moves live here. First, tally how often each value appears — a hash map, one
pass. Second, pick the top few by that tally *without fully sorting everything.*
And when the thing you're ranking by is a small whole number, you can place items
directly at that number instead of comparing them.

"Most frequent" questions are everywhere. Trending topics, top search queries,
best-selling products, and the "heavy hitters" in network traffic are all top-K
by count. Dashboards showing top referrers or top error messages run this.
Word-frequency ranking feeds autocomplete and stopword lists. At huge scale these
turn into streaming, approximate versions (count-min sketch, a running top-K
heap), but the shape is the same: count, then rank.

What you're avoiding is paying to sort the whole set when you only want K of it,
and using a bounded score to make the ranking step one straight pass.

## Start from the obvious

Two clear steps. Count how often each value appears — a hash map, one pass. Then
pick the `k` biggest counts.

The lazy way to "pick the biggest" is to sort the distinct values by their count
and take the first `k`.

```diagram
   counts:  1->3  2->2  3->1
   sort by count, high to low:   [1, 2, 3]
   take first k=2            ->   [1, 2]
```

Correct, about n log n. The sort is the only expensive part — and it does more
than the question needs.

## Find the waste

Sorting puts *every* distinct value in order even though you only want the top
`k`. And the thing you're sorting by — a frequency — isn't an arbitrary number. A
value appears at most `n` times and at least once. That's a small range of whole
numbers. When your sort key is a bounded whole number, a comparison sort is
overkill: you can place things straight at their key.

## The insight

Index by frequency. Build `buckets` where `buckets[f]` is the list of values that
occur exactly `f` times. The frequency *is* the slot number.

```diagram
   nums = [1,1,1,2,2,3]      counts: 1->3  2->2  3->1

   bucket index (frequency):
      0:  []
      1:  [3]
      2:  [2]
      3:  [1]
          ^ most frequent values sit at the highest indices
```

Now walk the buckets from the highest frequency down, scooping up values until
you've collected `k`.

```diagram
   want k=2, walk indices 3,2,1:

   index 3:  take 1     collected [1]
   index 2:  take 2     collected [1,2]  -> have k, stop
```

No comparisons happen at all — the frequency told you where each value goes. This
is counting-sort logic: sort by placing, not by comparing.

## Complexity

- **Time: about n steps.** Count pass, bucket-fill pass, and a walk over the
  n+1 buckets.
- **Extra memory: about n.** The count map plus the buckets hold at most n
  values between them.

Beats the sort's n log n.

## Pitfalls

- Off-by-one on the bucket array: frequencies run `1..n`, so make it size `n+1`
  and leave index `0` empty.
- Don't sort inside the buckets — you'd add back the cost you just removed.
- The answer order is unspecified; comparing against an expected *set* (as the
  test does) avoids brittle order assumptions.
- A heap (a structure that keeps the smallest of the top few on top) of size `k`
  is the other classic answer, about n log k — better when `k` is tiny next to
  `n`. The bucket method is a straight n here.

## Transfer

**Sort key is a small whole number → place items in buckets instead of comparing
them** is the reusable idea. It reappears in any "rank by a small integer score"
task, like sorting a handful of color values in one pass. The first half — tally
with a hash map — is the same move behind
[Valid Anagram / 242](../0242-valid-anagram/) and
[Group Anagrams / 49](../0049-group-anagrams/).
