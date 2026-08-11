# 307. Range Sum Query - Mutable

**Pattern:** Fenwick tree (Binary Indexed Tree) / segment tree — partial sums
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/range-sum-query-mutable/

## The problem in plain words

You get an array and then a long stream of two kinds of requests, mixed together:
"change the value at position `i`" and "what's the sum of everything from `l` to
`r`?". You must answer both quickly, over and over, while the array keeps changing
underneath you. No request is known in advance, so you can't precompute one answer
and stop.

## Why this matters

The real subject here is a **running aggregate over data that mutates**. Not "sum
this array once" — anyone can do that in a loop — but "keep a sum queryable while
edits keep arriving." The moment updates and range queries interleave, the two
naive tools fight each other: a raw array makes edits free but sums slow; a prefix
table makes sums free but edits slow. You need one structure good at *both*.

That tension is everywhere real. A leaderboard or analytics dashboard shows
"points scored in rows 10–50" while individual scores tick up live. A spreadsheet
recomputes `SUM(B2:B900)` after you edit one cell, without re-adding 898 numbers.
Time-series and monitoring systems roll up "requests in this window" as new events
stream in. Database engines keep aggregate indexes fresh under writes. All of these
are update-then-range-query on a changing sequence.

What the Fenwick tree buys is a **latency budget that holds as the array grows**:
both operations become `O(log n)` instead of one of them being `O(n)`. At a
million elements that's ~20 steps versus a million — the difference between a
dashboard that stays live and one that stalls every time someone edits a cell.

## Start from the obvious

Two honest first tries, each optimal for *one* operation:

```
# Raw array
update(i, v):      nums[i] = v            # O(1)
sumRange(l, r):    return sum(nums[l:r+1]) # O(n)  <- slow

# Prefix sums: prefix[k] = nums[0]+...+nums[k-1]
sumRange(l, r):    return prefix[r+1] - prefix[l]   # O(1)
update(i, v):      # every prefix from i+1 on is now wrong -> rebuild  O(n)
```

Each is great until you mix in the *other* operation. With both happening
frequently, whichever one is `O(n)` dominates and the whole thing crawls.

## Find the waste

The prefix array is *too coarse*: one edit invalidates a huge suffix because each
prefix bundles a sum "from the very start." The raw array is *too fine*: a range
sum has to touch every element because nothing is precomputed.

The waste in both is the same missing idea: **precompute sums of the right-sized
chunks so that no single edit spoils too many of them, and no single query has to
visit too many of them.** If a chunk covers a power-of-two-sized block, then any
index sits inside only `log n` chunks, and any prefix is the sum of only `log n`
chunks. Editing one element touches `log n` chunks; reading a prefix reads `log n`
chunks. Balance achieved.

## The insight

A **Fenwick tree** is exactly that set of chunks, packed cleverly using binary. Use
1-indexing. Node `i` stores the sum of the block of `i & (-i)` elements ending at
`i` — where `i & (-i)` is i's lowest set bit. So node `0110` (6) covers 2 elements,
node `1000` (8) covers 8, node `0101` (5) covers 1. The bits of an index are
literally the sizes of the disjoint blocks that tile the prefix up to it.

```
prefix sum up to i:   s = 0; while i>0: s += tree[i]; i -= i & -i
point update at i:     while i<=n: tree[i] += delta; i += i & -i
```

Reading walks *down* by clearing the lowest bit each step (jump to the previous
block). Updating walks *up* by adding the lowest bit (jump to the next block that
also contains `i`). Both loops run once per bit — `O(log n)`. A range sum is
`prefix(r) - prefix(l-1)`. Because the tree stores sums, an update applies the
*difference* `val - old`, not the new value.

A **segment tree** reaches the same `O(log n)` differently: a binary tree of range
sums, update fixes a leaf and walks to the root, a query stitches together whole
subtrees that fall inside `[l, r]`. It costs ~2× memory and more code but generalizes
to any associative operation (min, max, gcd), where subtraction-based Fenwick can't.
Both are in the solution file.

## Complexity

- **Time:** `update` and `sumRange` are each `O(log n)` — every loop advances by at
  least one binary digit of the index, and there are `⌊log₂ n⌋ + 1` digits. Building
  the Fenwick tree by `n` point-updates is `O(n log n)` (an `O(n)` build exists but
  the simple version is plenty fast).
- **Space:** `O(n)` — one array of size `n+1` (Fenwick) or `2n` (segment tree).

## Pitfalls

- **Off-by-one from 1-indexing.** The Fenwick array must be 1-based; the `i & -i`
  trick fails at index 0 (it loops forever adding 0). Convert once at the boundary.
- **Storing values instead of deltas.** `update` must add `val - nums[i]` and then
  save the new value, or repeated updates to the same cell corrupt the sums.
- **`sumRange(0, r)`.** `prefix(l-1)` with `l == 0` would read index `-1`; special-case
  it (or make prefix handle an empty range cleanly).
- **Forgetting the tree is not the array.** `tree[i]` is a block sum, not `nums[i]`.
  Keep a separate copy of current values if you need them for deltas.

## Transfer

The reusable idea is **maintain an aggregate over a mutable sequence in
sub-linear time by precomputing power-of-two-sized partial sums**. Once you can do
prefix sums under updates, you can do range sums, and (with a second BIT) range
*updates* too. Siblings: [Count of Smaller Numbers After Self /
315](../0315-count-of-smaller-numbers-after-self/) uses a BIT over value-ranks as a
"how many seen so far are less than x" counter; range-min/range-max problems use the
segment-tree variant; 2D versions extend the same bit trick to a grid.
