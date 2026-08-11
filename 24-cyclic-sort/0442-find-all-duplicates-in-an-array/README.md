# 442. Find All Duplicates in an Array

**Pattern:** Index-as-hash / sign marking (the array is its own hash table)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/find-all-duplicates-in-an-array/

## The problem in plain words

You have a list of length n where every value is between 1 and n. Some values show
up once, some show up exactly twice. Return the list of values that appear twice —
in linear time and without spending extra memory.

## Why this matters

The heart of this problem is the same one behind counting sort and bitmap-style
bookkeeping: when values are known to live in a tight range 1..n, you don't need a
separate counter table — the array's own slots can carry the "have I seen this?"
bit. Value `v` maps to home index `v-1`, and you record a visit by *flipping the
sign* of the number parked there. The data and its own metadata share one array.

That "encode a flag into a value you already store" trick is a real memory-saving
tool. Mark-and-sweep garbage collectors flip a bit inside each object header to
record "reachable" during a traversal — no side table. Union-find and in-place
graph algorithms stash visited/parent info directly in the node array. Databases
and columnar engines lean on the same bounded-domain insight for bitmap indexes
and dictionary encoding.

What the good solution buys is O(1) auxiliary space and a single pass: you find
every repeat without allocating a hash map the size of the input, which is the
difference between a routine that scales and one whose memory doubles the data.

## Start from the obvious

Keep a set of what you've seen; when a value reappears, it's a duplicate:

```
seen = set()
out = []
for x in nums:
    if x in seen: out.append(x)
    seen.add(x)
return out
```

Correct and readable. But the set is O(n) extra memory — the very thing we're
asked to avoid. Can the input array itself remember what we've seen?

## Find the waste

The set only ever answers one yes/no question: "have I already visited value v?".
We're paying for a whole hash table to store a single bit per value. But we're
handed a powerful constraint: **every value is in 1..n**, so every value has a
private home index `v-1` in the array we already own. If we can stash the
visited-bit *at that home slot*, the set becomes pointless.

Where do we hide a bit inside an integer we still need to read later? The **sign**.
The magnitudes stay intact (so we can always recover which value a slot represents
with `abs`), while a negative sign quietly means "this home has been visited."

## The insight

**Use the sign at index `v-1` as the visited-flag for value `v`.**

Walk the array. For each entry, recover the real value `v = abs(x)` and look at its
home slot `nums[v-1]`:

- If that slot is still **positive**, this is the first sighting of `v` — flip it
  negative to record the visit.
- If it's already **negative**, we've been to `v`'s home before, so `v` is a
  duplicate. Emit it.

```
for x in nums:
    v = abs(x)
    if nums[v-1] < 0: out.append(v)
    else: nums[v-1] = -nums[v-1]
```

Reading `abs(x)` matters: the entry you're standing on may itself have been flipped
by an earlier step, but its magnitude still names the value correctly. Each value
appears at most twice, so each home flips at most once and is caught at most once —
no value is double-reported.

## Complexity

- **Time:** `O(n)` — one pass; each step is O(1) index arithmetic and a sign flip.
- **Space:** `O(1)` extra — we mutate the input in place. The output list is the
  required answer, not auxiliary bookkeeping.

## Pitfalls

- **Reading `nums[i]` instead of `abs(nums[i])`.** Once signs start flipping, the
  raw value can be negative and points at the wrong (or an invalid) index.
- **Marking before checking.** Look at the home slot's sign *first*; if you flip
  unconditionally you lose the "already visited" signal.
- **Assuming you may not touch the array.** #442 permits in-place mutation. If a
  caller forbids it (as #287 does), this trick is off the table.
- **Values outside 1..n.** This problem guarantees 1..n; the sign trick relies on
  it, so don't reuse it blindly where the range isn't bounded.

## Transfer

The pattern — *values 1..n index into the array, and sign encodes a per-value
bit* — is the workhorse of this chapter. Its mirror image finds what's missing
instead of what's doubled:
[Find All Numbers Disappeared / 448](../0448-find-all-numbers-disappeared-in-an-array/).
Close relatives:
[First Missing Positive / 41](../0041-first-missing-positive/),
[Find the Duplicate Number / 287](../0287-find-the-duplicate-number/) (which bans
mutation and forces a different tool).
