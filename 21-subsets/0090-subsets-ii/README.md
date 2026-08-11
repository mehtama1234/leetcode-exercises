# 90. Subsets II

**Pattern:** Backtracking with duplicate skipping (sort, then skip equal siblings)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/subsets-ii/

## The problem in plain words

Same as [Subsets](../0078-subsets/), but the input can repeat, like `[1,2,2]`.
Return every *distinct* subset. `[2]` should appear once even though there are
two 2s, and `[1,2]` should appear once even though you could build it two ways.
The answer is a set of subsets, not a list that happens to have repeats.

```diagram
   nums = [1, 2, 2]

   distinct subsets we want:
     []   [1]   [1,2]   [1,2,2]   [2]   [2,2]

   the trap: [2] can be built from the first 2 OR the second 2
             -> plain Subsets would emit it twice
```

## Why this matters

The new move this teaches is **de-duplicating a search without a hash set**. The
lazy fix — generate everything, then dump the answers into a set — works but
throws away real work: you build identical results just to discard them, and
hashing `2^n` lists costs time and memory. The better question is: can you avoid
*making* the duplicate in the first place?

This shows up wherever a search space has interchangeable items. Picking a team
from a roster where several players share a role, choosing toppings when three
slices are identical, listing distinct multiset selections in a config solver —
all have "these two choices are the same, don't explore both" at their heart.

What the good solution buys is cutting the branch *at the source*: whole
duplicate subtrees are never entered, so runtime tracks the number of *distinct*
answers, not the number of ways to reach them. That gap can be large when a value
repeats a lot.

## Start from the obvious

Run plain Subsets, then filter:

```diagram
   all = every subset of [2,2]           includes duplicates
       -> []  [2]  [2]  [2,2]
                 ^    ^
                 built twice, once per 2

   answer = dedupe(all)  ->  []  [2]  [2,2]
```

Honest and correct, and it makes the waste obvious: `[2]` gets built twice before
the merge. We're paying to make garbage. The goal is to never emit the second
`[2]` at all.

## The insight

Two moves together kill duplicates at the source.

**1. Sort the array.** Now equal values sit next to each other, so "is this a
repeat?" becomes "is it the same as my left neighbor?" — a one-step check.

**2. Skip equal siblings at the same level.** Build subsets by position: at each
recursion a loop picks the next number to add from the tail `start..n`. The rule:

```
for i from start to n-1:
    if i > start and nums[i] == nums[i-1]: continue   # <-- the skip
    choose nums[i]; recurse(i+1); un-choose
```

The `i > start` part is the subtle bit. Two equal values *may* both be used —
but only when they're chosen at **different levels**, one nested under the other.
What we forbid is choosing the same value twice as *alternatives at the same
level*, because the branch that used the earlier copy already produced every
subset the later copy could.

```diagram
   choice tree from start=1 on sorted [1, 2, 2]   (index in parens)

              start=1
          /              \
     take 2 (i=1)      take 2 (i=2)  <-- i>start AND nums[2]==nums[1]
        |                   X  PRUNED: this whole branch is a
     recurse start=2            re-run of the branch on the left
        |
     take 2 (i=2)  <-- i==start here, so allowed
        -> this is how [2,2] still gets built (deeper level, not sibling)
```

Every node in this tree is itself a valid subset (not only the leaves), so we
record `path` on entry to each call, not just at the bottom.

## Complexity

- **Time: about `n * 2^n` worst case** (all distinct — this becomes plain
  Subsets), but far less when values repeat, since duplicate branches are cut.
  Copying each emitted subset is the extra factor of `n`.
- **Extra memory: about `n`** — recursion depth plus `path`. Sorting is
  `n log n`, smaller than the enumeration.

## Pitfalls

- **Not sorting first.** The skip relies on equal values being adjacent; on
  unsorted input it quietly misses duplicates.
- **Writing `if nums[i] == nums[i-1]` without `i > start`.** That wrongly blocks
  the legitimate deeper use of the second copy, so you lose subsets like `[2,2]`.
- Reaching for a global `set` to dedupe — it works but defeats the lesson and
  costs extra memory; the local skip is cheaper.

## Transfer

"Sort, then skip a value equal to the previous sibling at this level" is the
canonical duplicate-handling move for backtracking. It's the exact change that
turns [Permutations / 46](../0046-permutations/) into
[Permutations II / 47](../0047-permutations-ii/), and it reappears in Combination
Sum II. Whenever a search has interchangeable items, sort and skip equal
siblings.
