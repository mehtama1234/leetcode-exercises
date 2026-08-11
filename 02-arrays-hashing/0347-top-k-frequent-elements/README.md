# 347. Top K Frequent Elements

**Pattern:** Hashing + bucket sort (counting by frequency)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/top-k-frequent-elements/

## The problem in plain words

Given a list of numbers, find the `k` values that show up the most. If `k` is 2
and `1` appears three times while `2` appears twice, the answer is `[1, 2]`.

## Why this matters

The core problem is *finding the top-K items by a score without fully sorting
everything* — and, when that score is a small bounded integer, placing items
directly by score (counting sort) instead of comparing them. The fundamental
operations are tally-then-rank.

"Most frequent" queries are everywhere. Trending topics, top search queries, most
viewed products, and "heavy hitters" in network traffic monitoring are all
top-K-by-count. Analytics dashboards showing top referrers or top error messages
run this. Word-frequency ranking feeds autocomplete and stopword lists. At large
scale these become streaming/approximate versions (count-min sketch, top-K heaps),
but the shape is identical.

What you're solving for is not paying O(n log n) to sort the whole set when you
want only K, and exploiting a bounded key so the rank step is O(n). A size-K heap
is the alternative when K is tiny; bucketing by frequency is strictly linear here.

## Start from the obvious

Two clear steps. First count how often each value appears — that's a hash map,
one linear pass. Then pick the `k` biggest counts.

The lazy way to "pick the biggest" is to sort the distinct values by their count
and take the first `k`:

```
counts = tally(nums)
ordered = sorted(counts, key=count, reverse=True)
return ordered[:k]
```

Correct, `O(n log n)`. The sort is the only expensive part — and it's doing more
than we need.

## Find the waste

Sorting fully orders *every* distinct value even though we only want the top `k`.
More importantly, the thing we're sorting by — a frequency — isn't an arbitrary
number. A value can appear at most `n` times and at least once. That's a small,
bounded range of integers. Whenever your sort key is a bounded integer, a
comparison sort is overkill: you can place things directly by that key.

## The insight

Index by frequency. Build `buckets` where `buckets[f]` is the list of values that
occur exactly `f` times:

```
buckets = [[] for _ in range(n+1)]
for value, freq in counts.items():
    buckets[freq].append(value)
```

Now the most frequent values sit at the highest indices. Walk `buckets` from `n`
down to `1`, scooping up values until you've collected `k`:

```
for freq from n down to 1:
    for value in buckets[freq]:
        collect value; stop once you have k
```

This is counting-sort logic: the frequency *is* the position, so no comparisons
happen at all.

## Complexity

- **Time:** `O(n)` — count pass, bucket-fill pass, and a walk over `n+1` buckets.
- **Space:** `O(n)` — the count map plus the buckets hold at most `n` values.

Beats the sort's `O(n log n)`.

## Pitfalls

- Off-by-one on the bucket array: frequencies run `1..n`, so size it `n+1` and
  leave index `0` empty.
- Don't sort inside the buckets — you'd reintroduce the cost you just removed.
- The answer order is unspecified; comparing against an expected *set* (as the
  test does) avoids brittle order assumptions.
- A heap of size `k` is the other classic answer at `O(n log k)` — better when
  `k` is tiny relative to `n`, but the bucket method is strictly linear here.

## Transfer

"Sort key is a bounded integer → bucket / counting sort instead of comparison
sort" is the reusable idea. It reappears in [Sort Colors / 75](../../misc/) and
any "rank by a small integer score" task. The first-half move — tally with a hash
map — is the same one behind [Valid Anagram / 242](../0242-valid-anagram/) and
[Group Anagrams / 49](../0049-group-anagrams/).
