# 41. First Missing Positive

**Pattern:** Cyclic sort / index-as-hash (the array is its own hash table)
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/first-missing-positive/

## The problem in plain words

You have an unsorted list of integers — positives, negatives, zeros, duplicates,
anything. Find the smallest positive integer (1, 2, 3, ...) that is *not* in the
list. And do it fast (one pass) with no meaningful extra memory.

## Why this matters

Underneath this puzzle is a sharp idea: when your values are drawn from a known,
bounded range, you don't need a separate hash table to remember which ones you've
seen — the storage you already have *is* the table. An array of length n has n
addressable slots; if the interesting values are 1..n, then value `v` has an
obvious home at index `v-1`, and "is v present?" becomes "is v's home slot filled
correctly?". That reframing is what lets you hit O(1) extra space.

This "use the container's own addresses as the index" move is everywhere real
systems fight for memory. Allocators and free-list managers track which fixed-size
blocks are in use by writing marks into the blocks themselves. A bitmap filesystem
records "is block k allocated?" in bit k — the position carries the meaning.
Finding the lowest free ID (a process slot, a file descriptor, a ticket number) is
literally "first missing positive" over a bounded pool.

What the good solution buys is the tightest resource budget possible: one linear
pass and *zero* auxiliary structures, so it stays flat as the input grows instead
of doubling your footprint with a side set.

## Start from the obvious

Dump everything into a set, then count upward until you find a gap:

```
present = set(nums)
c = 1
while c in present:
    c += 1
return c
```

Correct and easy to trust. But that set is O(n) extra memory — the exact thing
the problem forbids. The interesting question is: can the array we already have do
the set's job?

## Find the waste

The set exists only to answer "have I seen value v?". Notice two facts that make
it redundant:

1. **The answer is boxed in.** With n numbers, the smallest missing positive is at
   most n+1 (if 1..n are all present, the answer is n+1; otherwise it's some value
   ≤ n). So only values in the range 1..n can ever matter — everything else
   (negatives, zeros, anything > n) is noise we can ignore.
2. **Each relevant value has a natural address.** Value `v` in 1..n "belongs" at
   index `v-1`. If we could arrange for each such value to sit in its home slot,
   then a missing value would announce itself as a slot holding the wrong number.

## The insight

**Put every value where it belongs, then scan for the first seat that's wrong.**

Pass 1 — placement by swapping. Walk index by index. While the value at index `i`
is in range 1..n and isn't already sitting in its home, swap it to its home
(`index = value - 1`). Keep swapping until index `i` holds something out of range
or already-correct:

```
while 1 <= nums[i] <= n and nums[nums[i]-1] != nums[i]:
    correct = nums[i] - 1
    nums[i], nums[correct] = nums[correct], nums[i]
```

This looks like a nested loop but is O(n) overall: every swap drops at least one
value into its final seat, and a value never leaves once it's home, so there are
at most n swaps total.

Pass 2 — read off the gap. Scan left to right; the first index `i` where
`nums[i] != i + 1` means `i + 1` never made it home, so `i + 1` is missing. If
every seat checks out, all of 1..n are present and the answer is n+1.

## Complexity

- **Time:** `O(n)` — two passes; the swap loop does at most n placements total
  because each swap finalizes one element's position.
- **Space:** `O(1)` — we rearrange the input in place and keep no side structure.

## Pitfalls

- **Infinite swap loop on duplicates.** The guard `nums[nums[i]-1] != nums[i]` is
  essential: if the home slot already holds the same value (a duplicate), swapping
  would spin forever. Stop when the target seat is already satisfied.
- **Forgetting the empty array.** Length 0 must return 1.
- **Swapping to `i` vs to `value-1`.** The destination is the value's home
  (`nums[i]-1`), not the running index. Getting this backwards silently corrupts
  the placement.
- **Off-by-one in the read pass.** Index `i` should hold `i+1`, not `i`.

## Transfer

The reusable move is *values 1..n ↔ indices 0..n-1, so the array is the hash
table*. Once each value is home (or you mark homes by sign), gaps and duplicates
fall out of a single scan. Siblings:
[Find All Numbers Disappeared / 448](../0448-find-all-numbers-disappeared-in-an-array/),
[Find All Duplicates / 442](../0442-find-all-duplicates-in-an-array/),
[Find the Duplicate Number / 287](../0287-find-the-duplicate-number/).
