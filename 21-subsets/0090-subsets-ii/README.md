# 90. Subsets II

**Pattern:** Backtracking with duplicate skipping (sort, then skip equal siblings)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/subsets-ii/

## The problem in plain words

Same as [Subsets](../0078-subsets/), but the input can repeat values, like
`[1,2,2]`. Return every *distinct* subset. Here `[2]` must appear once even though
there are two 2s, and `[1,2]` must appear once even though it could be built two
ways. The answer is a set of subsets, not a list that happens to have repeats.

## Why this matters

The new operation this teaches is **de-duplicating a search without a hash set**.
The naive fix — generate everything, then throw the answers into a set — works but
is wasteful: you do full work producing identical results just to discard them,
and hashing `2^n` lists costs real time and memory. The interesting question is:
can you *avoid generating* the duplicate in the first place?

This exact problem shows up whenever a search space has interchangeable items.
Picking a team from a roster where several players share a role, choosing toppings
where you have three identical slices of the same thing, enumerating distinct
multiset selections in a configuration solver — all have "these two choices are
indistinguishable, don't explore both" at their heart.

What the good solution buys is pruning *at the source*: entire duplicate branches
of the decision tree are never entered, so runtime tracks the number of *distinct*
answers, not the number of ways to reach them. That gap can be enormous when a
value repeats many times.

## Start from the obvious

Run plain Subsets, then filter:

```
all = every subset of nums          # includes duplicates
answer = dedupe(all)                # e.g. put sorted tuples in a set
```

Honest, correct, and it makes the redundancy obvious: for `[2,2]` it builds `[2]`
twice (once from each 2) before merging them. We're paying to make garbage. The
goal is to never emit the second `[2]`.

## The insight

Two moves together kill duplicates at the source.

**1. Sort the array.** Now equal values sit next to each other, so "is this a
repeat?" becomes "is it equal to my left neighbor?" — a local, O(1) check.

**2. Skip equal siblings at the same depth.** Build subsets by position: at each
recursion, a loop picks the next number to append from the tail `start..n`. The
rule:

```
for i from start to n-1:
    if i > start and nums[i] == nums[i-1]: continue   # <-- the skip
    choose nums[i]; recurse(i+1); un-choose
```

The condition `i > start` is the subtle part. Two equal values *may* both be used
when they're chosen at **different depths** (that's how `[2,2]` gets built — the
first 2 at this level, the second 2 one level deeper via `recurse(i+1)`). What we
forbid is picking the *same value twice as alternatives at the same level*,
because the branch that used the earlier copy already generated every subset the
later copy could. Every node in this tree is itself a valid subset, so we record
`path` on entry, not only at leaves.

## Complexity

- **Time:** `O(n * 2^n)` worst case (all distinct — degenerates to Subsets), but
  far less when values repeat, since duplicate branches are pruned. Copying each
  emitted subset is the `O(n)` factor.
- **Space:** `O(n)` extra — recursion depth plus `path`. Sorting is `O(n log n)`,
  dominated by the enumeration.

## Pitfalls

- **Not sorting first.** The skip check relies on equal values being adjacent; on
  unsorted input it silently misses duplicates.
- **Writing `if nums[i] == nums[i-1]` without `i > start`.** That wrongly blocks
  the legitimate deeper use of the second copy, so you lose subsets like `[2,2]`.
- Reaching for a global `set` to dedupe — it works but defeats the lesson and
  costs extra memory; the local skip is cheaper.

## Transfer

"Sort, then skip a value equal to the previous sibling at this depth" is the
canonical duplicate-handling move for backtracking. It's the exact change that
turns [Permutations / 46](../0046-permutations/) into
[Permutations II / 47](../0047-permutations-ii/), and it reappears in Combination
Sum II. Whenever a search has interchangeable elements, sort and skip equal
siblings.
