# 217. Contains Duplicate

**Pattern:** Hashing (membership test)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/contains-duplicate/

## The problem in plain words

You have a list of numbers. Answer a single yes/no question: does any number
show up more than once?

## Start from the obvious

A duplicate means two different positions holding the same value. So compare
every position against every other one:

```
for each i:
    for each j after i:
        if nums[i] == nums[j]: return True
return False
```

That's `O(n^2)`. It's correct, and it's the honest first thought — but looking
at *why* it's slow points straight at the fix.

## Find the waste

For each element the inner loop walks the rest of the array asking "is this same
value sitting somewhere later?". That's a search, and we redo it from scratch for
every element. But we don't actually need to search the tail — we only need to
remember what we've *already passed*. The real question is the cheap one:

> **Have I seen this value before?**

Answering "have I seen this?" in `O(1)` is exactly what a hash set is for.

## The insight

Walk the list once, carrying a set of everything seen so far. At each number:

1. If it's already in the set, we found a repeat — return True.
2. Otherwise add it and move on.

Check **before** you insert, so the very first repeat is caught the instant it
appears and you can stop early.

## Complexity

- **Time:** `O(n)` — one pass, each lookup/insert is `O(1)` average.
- **Space:** `O(n)` — the set can hold up to `n` distinct values.

A one-liner captures the same idea: `len(set(nums)) != len(nums)` — if squashing
duplicates shrinks the list, there were duplicates. It's clean, but it always
builds the whole set even when the answer is decided on element two; the explicit
loop can bail early.

## Pitfalls

- Sorting first (`O(n log n)`) is a valid space-saving alternative, but don't
  reach for it if you're allowed the `O(n)` set — it's slower for no reason here.
- Empty list and single element must return False — there's nothing to pair.
- Inserting before checking still works for *this* problem, but the "check first"
  habit matters in siblings where an element must not match itself.

## Transfer

This is the base case of "replace an inner search with a hash-set membership
test." The same move powers [Two Sum / 1](../0001-two-sum/) (look up the needed
partner) and [Longest Consecutive Sequence / 128](../0128-longest-consecutive-sequence/)
(is `x-1` present?). Whenever a brute force keeps re-scanning for "is value V
present?", reach for a set first.
