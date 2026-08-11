# 1. Two Sum

**Pattern:** Hashing (trade space for time)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/two-sum/

## The problem in plain words

You have a list of numbers and a target. Somewhere in the list, exactly two of
them add up to the target. Return *where* they are (their indices), not the
numbers themselves.

## Why this matters

Underneath the puzzle is one fundamental operation: *as data streams past you,
can you ask "have I already seen the thing that completes this one?" in constant
time?* You're not searching — you're remembering, then checking membership. A
hash map turns that check into O(1).

That exact move runs real systems. A database join matching rows on a key builds
a hash table of one side and probes it with the other. Deduplication and
"have-I-processed-this-event" checks in stream pipelines are the same lookup.
Detecting a transaction that pairs with an earlier one (matching a debit to a
credit, a request to its response) is Two Sum with business names.

What the good solution buys is a single pass over data you often can't rewind,
and it replaces an O(n) rescan-per-element with an O(1) lookup — the difference
between a query that finishes and one that times out as the input grows.

## Start from the obvious

The definition itself hands you an algorithm: a "pair that sums to target"
means take every possible pair and test it.

```
for each i:
    for each j after i:
        if nums[i] + nums[j] == target: return [i, j]
```

That's `O(n^2)`. It's correct, and it's the right thing to write first — because
staring at *why* it's slow tells you what to fix.

## Find the waste

For each element `x`, the inner loop scans the rest of the array looking for one
specific value: `target - x`. That value is not a mystery we have to search for
— it is completely determined by `x`. So the real question isn't "which of the
remaining numbers pairs with x?" It is the much cheaper yes/no question:

> **Have I already seen the number `target - x`?**

Answering "have I seen this value?" in `O(1)` is exactly what a hash map is for.

## The insight

Walk the array once. As you arrive at each number `x`:

1. Compute the partner it *needs*: `need = target - x`.
2. If `need` is already in the map, you're done — return its stored index and the
   current index.
3. Otherwise, record `x -> its index` and move on.

You look **before** you insert. That ordering is what stops an element from
pairing with itself, and it correctly handles duplicates like `[3, 3], target 6`.

## Complexity

- **Time:** `O(n)` — one pass, each lookup/insert is `O(1)` average.
- **Space:** `O(n)` — the map may hold up to `n-1` entries.

This is the canonical space-for-time trade: we spend `O(n)` memory to erase the
inner loop.

## Pitfalls

- Returning the values instead of the **indices**.
- Inserting into the map *before* checking — an element can then match itself.
- Assuming the array is sorted (it isn't; that's a different problem — see
  [Two Sum II / 167](../../03-two-pointers/0167-two-sum-ii-input-array-is-sorted/)).

## Transfer

The move "replace an inner search with a hash-map membership test" reappears
constantly: [Contains Duplicate / 217](../0217-contains-duplicate/),
[Valid Anagram / 242](../0242-valid-anagram/),
[Longest Consecutive Sequence / 128](../0128-longest-consecutive-sequence/).
Whenever a brute force keeps re-scanning for "is value V present?", reach for a
set or dict first.
