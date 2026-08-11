# 47. Permutations II

**Pattern:** Backtracking with duplicate skipping (sort, then fix an order among equal copies)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/permutations-ii/

## The problem in plain words

Same as [Permutations](../0046-permutations/), but the input can repeat, like
`[1,1,2]`. Return every *distinct* ordering. `[1,1,2]` has only 3 unique
permutations, not 6, because swapping the two identical 1s produces the same
arrangement.

## Why this matters

This is duplicate handling for *orderings*, the sibling of Subsets II's duplicate
handling for *selections*. The naive route — permute as if all elements were
distinct, then dedupe — does real, wasted work: for `k` identical copies it builds
each true arrangement `k!` times before merging. With several repeated values that
overcount is huge.

The pattern is everywhere interchangeable items get arranged. Scheduling jobs where
several are identical, seating arrangements with indistinguishable guests, dealing
distinct hands from a deck with repeated ranks, generating test sequences over
events where some are the same — all need "these two orderings are literally the
same, produce it once."

What the good solution buys is the same as Subsets II: prune the duplicate
branches *before entering them*, so the running time follows the number of
*distinct* permutations rather than the number of ways to build them.

## Start from the obvious

Run plain Permutations, then filter out repeats:

```
all = every ordering treating positions as distinct   # overcounts
answer = dedupe(all)
```

Correct, and it lays the waste bare: with two 1s, every arrangement is generated
twice — once for each way of assigning the two identical 1s to their two slots.
We want to emit each arrangement exactly once.

## The insight

Sort so equal values are adjacent, then impose a **fixed placement order on equal
copies**: among identical values, you may only place a copy *after* its identical
left-neighbor has already been placed. That collapses the `k!` interchangeable
orderings of `k` equal items into exactly one.

The rule, when filling the current slot:

```
if nums[i] == nums[i-1] and used[i-1] is False:
    skip nums[i]
```

Read it carefully: we skip a duplicate value only when its earlier equal copy is
**not currently in use**. If the earlier copy *is* placed (used[i-1] is True), then
placing this copy next is the one legal way to use both — allowed. If the earlier
copy is free, then using this later copy first would just re-create an arrangement
the earlier copy will (or already did) produce — forbidden.

Everything else is the ordinary permutation template: choose (mark `used`, push),
explore (recurse), un-choose (pop, clear `used`), recording a copy at a full-length
leaf.

## Complexity

- **Time:** `O(n * n!)` worst case (all distinct — degenerates to Permutations),
  but with repeats it drops toward `O(n * n! / (k1! k2! ...))`, the count of
  distinct permutations, since duplicate branches are never entered.
- **Space:** `O(n)` extra — recursion depth, `path`, and `used`, each `O(n)`.
  Sorting adds `O(n log n)`.

## Pitfalls

- **The subtle `used[i-1]` direction.** `not used[i-1]` is correct here; flipping
  it to `used[i-1]` still runs but produces wrong counts. The mnemonic: *place a
  duplicate only right after its twin.*
- **Not sorting** — adjacency is what makes the neighbor check valid.
- **Deduping with a global set** instead — works, but does the wasteful work the
  skip is meant to avoid.

## Transfer

This is the Subsets II duplicate-skip adapted to the `used[]`-mask permutation
loop. The pairing is worth memorizing:
[Subsets](../0078-subsets/) → [Subsets II](../0090-subsets-ii/) and
[Permutations](../0046-permutations/) → [Permutations II](../0047-permutations-ii/)
are the same "add sort + skip equal siblings" edit applied to two templates.
