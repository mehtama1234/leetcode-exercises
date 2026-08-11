# 47. Permutations II

**Pattern:** Backtracking with duplicate skipping (sort, then fix an order among equal copies)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/permutations-ii/

## The problem in plain words

Same as [Permutations](../0046-permutations/), but the input can repeat, like
`[1,1,2]`. Return every *distinct* ordering. `[1,1,2]` has only 3 unique
permutations, not 6, because swapping the two identical 1s gives back the same
arrangement.

```diagram
   nums = [1, 1, 2]

   distinct orderings we want:
     [1,1,2]   [1,2,1]   [2,1,1]

   plain Permutations would list each twice
   (once per way of assigning the two 1s) -> 6, half of them repeats
```

## Why this matters

This is duplicate handling for *orderings*, the sibling of Subsets II's duplicate
handling for *selections*. The lazy route — permute as if every element were
distinct, then dedupe — does real wasted work: for `k` identical copies it builds
each true arrangement `k!` times before merging. With several repeated values that
overcount is large.

The pattern shows up wherever interchangeable items get arranged. Scheduling jobs
when several are identical, seating with indistinguishable guests, dealing hands
from a deck with repeated ranks, generating test sequences over events where some
are the same — all need "these two orderings are literally the same, produce it
once."

What the good solution buys is the same as Subsets II: cut the duplicate branches
*before entering them*, so the running time follows the number of *distinct*
permutations rather than the number of ways to build them.

## Start from the obvious

Run plain Permutations, then filter out repeats:

```diagram
   all = every ordering of [1a, 1b, 2] treating the two 1s as different

     1a 1b 2   1b 1a 2      both spell [1,1,2]
     1a 2 1b   1b 2 1a      both spell [1,2,1]
     2 1a 1b   2 1b 1a      both spell [2,1,1]

   dedupe -> [1,1,2] [1,2,1] [2,1,1]   (each built twice, half thrown away)
```

Correct, and it lays the waste bare: with two 1s, every arrangement is generated
twice, once per way of assigning the two identical 1s to their two slots. We want
each arrangement exactly once.

## The insight

Sort so equal values are adjacent, then set a **fixed placement order on equal
copies**: among identical values, you may only place a copy *after* its identical
left-neighbor has already been placed. That collapses the `k!` interchangeable
orderings of `k` equal items down to exactly one.

The rule, when filling the current slot:

```
if nums[i] == nums[i-1] and used[i-1] is False:
    skip nums[i]
```

Read it slowly: we skip a duplicate value only when its earlier equal copy is
**not currently in use**. If that earlier copy *is* placed, then placing this
copy next is the one legal way to use both — allowed. If the earlier copy is
free, then using this later copy first would only re-create an arrangement the
earlier copy will (or already did) make — forbidden.

```diagram
   filling slot 0 from sorted [1, 1, 2]  (the two 1s at index 0 and 1)

              slot 0 choices
         /          |           \
   take 1(i=0)  take 1(i=1)   take 2(i=2)
       |            X            |
       |     PRUNED: nums[1]==nums[0]
       |     and used[0]==False -> its twin
       |     isn't placed yet, so this is a
       |     re-run of the i=0 branch
       v
   later, DEEPER, once index 0 is used, index 1 IS allowed:
     path=[1(i0)] , now slot 1: take 1(i=1) ok because used[0]==True
```

Everything else is the ordinary permutation template: choose (mark `used`, push),
explore, un-choose (pop, clear `used`), recording a copy at a full-length leaf.

## Complexity

- **Time: about `n * n!` worst case** (all distinct — becomes plain
  Permutations), but with repeats it drops toward `n * n! / (k1! k2! ...)`, the
  count of distinct permutations, since duplicate branches are never entered.
- **Extra memory: about `n`** — recursion depth, `path`, and `used`, each `n`.
  Sorting adds `n log n`.

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
