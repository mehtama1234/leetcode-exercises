# 41. First Missing Positive

**Pattern:** Cyclic sort / index-as-hash (the array is its own lookup table)
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/first-missing-positive/

## The problem in plain words

You have an unsorted list of integers — positives, negatives, zeros, duplicates,
anything. Find the smallest positive integer (1, 2, 3, ...) that is *not* in the list.
Do it in one pass with no meaningful extra memory.

```diagram
   nums = [3, 4, -1, 1]

   present positives: 1, 3, 4        (ignore -1)
   count up:  1? yes | 2? NO
   answer = 2
```

## Why this matters

Underneath this puzzle is a sharp idea: when your values come from a known, bounded
range, you don't need a separate lookup table to remember which ones you've seen — the
storage you already have *is* the table. An array of length `n` has `n` addressable
slots; if the interesting values are `1..n`, then value `v` has an obvious home at index
`v-1`, and "is `v` present?" becomes "is `v`'s home slot filled with `v`?". That
reframing is what lets you use no extra memory.

This "use the container's own addresses as the index" move shows up wherever real
systems fight for memory. Allocators track which fixed-size blocks are in use by writing
marks into the blocks themselves. A bitmap filesystem records "is block `k` allocated?"
in bit `k` — the position carries the meaning. Finding the lowest free ID (a process
slot, a file descriptor, a ticket number) is literally "first missing positive" over a
bounded pool.

What the good solution buys: the tightest possible memory budget — one linear pass and
*no* side structure, so the footprint stays flat as the input grows.

## Start from the obvious

Dump everything into a set, then count upward until you find a gap.

```diagram
   present = {3, 4, -1, 1}
   c = 1: in set? yes -> c = 2
   c = 2: in set? no  -> return 2
```

Correct and easy to trust. But that set is extra memory that grows with the input — the
exact thing the problem forbids. The interesting question: can the array we already have
do the set's job?

## Find the waste

The set exists only to answer "have I seen value `v`?". Two facts make it redundant:

1. **The answer is boxed in.** With `n` numbers, the smallest missing positive is at
   most `n+1` (if `1..n` are all present the answer is `n+1`; otherwise it's some value
   at most `n`). So only values in `1..n` can ever matter — negatives, zeros, and
   anything above `n` are noise.
2. **Each relevant value has a natural address.** Value `v` in `1..n` belongs at index
   `v-1`. If we get each such value into its home slot, then a *missing* value announces
   itself: its home holds the wrong number.

## The insight

**Put every value where it belongs, then scan for the first seat that's wrong.**

Pass 1 — placement by swapping. Walk index by index. While the value at index `i` is in
`1..n` and isn't already home, swap it to its home (`index = value - 1`). Keep swapping
at `i` until it holds something out of range or already correct.

```diagram
   nums = [3, 4, -1, 1]      home of value v is index v-1

   i=0: nums[0]=3 -> home index 2. swap nums[0] <-> nums[2]
        [3, 4, -1, 1]
         ^--------^  (3 goes to index 2, -1 comes back)
        [-1, 4, 3, 1]
        nums[0]=-1 out of range -> stop, move on

   i=1: nums[1]=4 -> home index 3. swap nums[1] <-> nums[3]
        [-1, 4, 3, 1]
             ^-----^
        [-1, 1, 3, 4]
        nums[1]=1 -> home index 0. swap nums[1] <-> nums[0]
        [-1, 1, 3, 4]
         ^---^
        [1, -1, 3, 4]
        nums[1]=-1 out of range -> stop

   i=2: nums[2]=3 already home (index 2). skip
   i=3: nums[3]=4 already home (index 3). skip

   final: [1, -1, 3, 4]
```

This looks like a nested loop but is one linear pass overall: every swap drops at least
one value into its final seat, and a value never leaves once it's home, so there are at
most `n` swaps total.

Pass 2 — read off the gap. Scan left to right; the first index `i` where
`nums[i] != i + 1` means `i + 1` never made it home, so `i + 1` is missing. If every seat
checks out, all of `1..n` are present and the answer is `n+1`.

```diagram
   final: [ 1, -1,  3,  4 ]     want index i to hold i+1
   index:   0   1   2   3
   want:    1   2   3   4
                ^ index 1 holds -1, not 2  ->  2 is missing
```

## Complexity

- **Time:** about `n` steps — two passes; the swap loop does at most `n` placements
  because each swap finalizes one element's spot.
- **Extra memory:** constant — we rearrange the input in place and keep no side
  structure.

## Pitfalls

- **Infinite swap loop on duplicates.** The guard `nums[nums[i]-1] != nums[i]` is
  essential: if the home slot already holds the same value (a duplicate), swapping would
  spin forever. Stop when the target seat is already satisfied.
- **Forgetting the empty array.** Length 0 must return 1.
- **Swapping to `i` vs to `value-1`.** The destination is the value's home
  (`nums[i]-1`), not the running index. Reversing this silently corrupts the placement.
- **Off-by-one in the read pass.** Index `i` should hold `i+1`, not `i`.

## Transfer

The reusable move: *values `1..n` line up with indices `0..n-1`, so the array is its own
lookup table*. Once each value is home (or you mark homes by sign), gaps and duplicates
fall out of a single scan. Siblings:
[Find All Numbers Disappeared / 448](../0448-find-all-numbers-disappeared-in-an-array/),
[Find All Duplicates / 442](../0442-find-all-duplicates-in-an-array/),
[Find the Duplicate Number / 287](../0287-find-the-duplicate-number/).
