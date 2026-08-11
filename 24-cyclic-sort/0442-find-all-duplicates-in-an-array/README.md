# 442. Find All Duplicates in an Array

**Pattern:** Index-as-hash / sign marking (the array is its own lookup table)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/find-all-duplicates-in-an-array/

## The problem in plain words

You have a list of length `n` where every value is between 1 and `n`. Some values show
up once, some show up exactly twice. Return the list of values that appear twice — in
one linear pass and with no extra memory.

```diagram
   nums = [4, 3, 2, 7, 8, 2, 3, 1]

   2 appears at index 2 and index 5   -> duplicate
   3 appears at index 1 and index 6   -> duplicate
   answer = [2, 3]
```

## Why this matters

The heart of this problem is the same one behind counting sort and bitmap bookkeeping:
when values are known to live in a tight range `1..n`, you don't need a separate counter
table — the array's own slots can carry the "have I seen this?" mark. Value `v` maps to
home index `v-1`, and you record a visit by *flipping the sign* of the number parked
there. The data and its own bookkeeping share one array.

That "hide a flag inside a value you already store" trick is a real memory-saving tool.
Mark-and-sweep garbage collectors flip a bit inside each object's header to record
"reachable" during a traversal — no side table. Union-find and in-place graph algorithms
stash visited/parent info directly in the node array. Databases lean on the same
bounded-range insight for bitmap indexes and dictionary encoding.

What the good solution buys: constant extra memory and a single pass — you find every
repeat without a lookup table the size of the input, the difference between a routine
that scales and one whose memory doubles the data.

## Start from the obvious

Keep a set of what you've seen; when a value reappears, it's a duplicate.

```diagram
   seen = {}          out = []
   x=4: new, add 4
   x=3: new, add 3
   x=2: new, add 2
   ...
   x=2: already in seen -> out = [2]
   x=3: already in seen -> out = [2, 3]
```

Correct and readable. But the set is extra memory that grows with the input — the very
thing we're asked to avoid. Can the input array itself remember what we've seen?

## Find the waste

The set only ever answers one yes/no question: "have I already visited value `v`?".
We're paying for a whole lookup table to store a single bit per value. But we're handed a
strong constraint: **every value is in `1..n`**, so every value has a private home index
`v-1` in the array we already own. Stash the visited-mark at that home slot and the set
becomes pointless.

Where do we hide a mark inside an integer we still need to read later? The **sign**. The
magnitudes stay intact (so `abs` always recovers which value a slot represents), while a
negative sign quietly means "this home has been visited."

## The insight

**Use the sign at index `v-1` as the visited-flag for value `v`.**

Walk the array. For each entry, recover the real value `v = abs(x)` and look at its home
slot `nums[v-1]`. If that slot is still **positive**, this is the first sighting of `v` —
flip it negative to record the visit. If it's already **negative**, we've been to `v`'s
home before, so `v` is a duplicate. Emit it.

```diagram
   nums = [4, 3, 2, 7, 8, 2, 3, 1]     mark visited-value-v at index v-1

   x=4: v=4, home idx 3. nums[3]=7 >0 -> flip.   [4, 3, 2, -7, 8, 2, 3, 1]
   x=3: v=3, home idx 2. nums[2]=2 >0 -> flip.   [4, 3, -2, -7, 8, 2, 3, 1]
   x=2: v=2, home idx 1. nums[1]=3 >0 -> flip.   [4, -3, -2, -7, 8, 2, 3, 1]
   x=-7:v=7, home idx 6. nums[6]=3 >0 -> flip.   [4, -3, -2, -7, 8, 2, -3, 1]
   x=8: v=8, home idx 7. nums[7]=1 >0 -> flip.   [4, -3, -2, -7, 8, 2, -3, -1]
   x=2: v=2, home idx 1. nums[1]=-3 <0 -> SEEN.  out=[2]
   x=-3:v=3, home idx 2. nums[2]=-2 <0 -> SEEN.  out=[2, 3]
   x=1: v=1, home idx 0. nums[0]=4 >0 -> flip.   (no new duplicate)
```

Reading `abs(x)` matters: the entry you're standing on may itself have been flipped by an
earlier step, but its magnitude still names the value correctly. Each value appears at
most twice, so each home flips at most once and is caught at most once — no value gets
double-reported.

## Complexity

- **Time:** about `n` steps — one pass; each step is a bit of index arithmetic and a sign
  flip.
- **Extra memory:** constant — we mark inside the input. The output list is the required
  answer, not scratch bookkeeping.

## Pitfalls

- **Reading `nums[i]` instead of `abs(nums[i])`.** Once signs start flipping, the raw
  value can be negative and points at the wrong (or an invalid) index.
- **Marking before checking.** Look at the home slot's sign *first*; if you flip
  unconditionally you lose the "already visited" signal.
- **Assuming you may not touch the array.** #442 permits in-place mutation. If a caller
  forbids it (as #287 does), this trick is off the table.
- **Values outside `1..n`.** This problem guarantees `1..n`; the sign trick relies on it,
  so don't reuse it where the range isn't bounded.

## Transfer

The pattern — *values `1..n` index into the array, and the sign encodes a per-value mark*
— is the workhorse of this chapter. Its mirror image finds what's missing instead of
what's doubled:
[Find All Numbers Disappeared / 448](../0448-find-all-numbers-disappeared-in-an-array/).
Close relatives: [First Missing Positive / 41](../0041-first-missing-positive/),
[Find the Duplicate Number / 287](../0287-find-the-duplicate-number/) (which bans mutation
and forces a different tool).
