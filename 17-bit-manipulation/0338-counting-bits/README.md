# 338. Counting Bits

**Pattern:** Bit manipulation plus dynamic programming (reuse a smaller answer)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/counting-bits/

## The problem in plain words

For every number from `0` up to `n`, count how many `1`s it has in binary, and
return all those counts in one array. So for `n = 5` you want the counts for
`0, 1, 2, 3, 4, 5`:

```diagram
   i | binary | ones
   --+--------+-----
   0 |  000   |  0
   1 |  001   |  1
   2 |  010   |  1
   3 |  011   |  2
   4 |  100   |  1
   5 |  101   |  2

   answer: [0, 1, 1, 2, 1, 2]
```

## Why this matters

The core move is **reusing an answer you already computed for a smaller number** —
dynamic programming (building a big answer out of smaller solved ones) over bits.
Every number's popcount is one more than the popcount of a strictly smaller
number (drop its lowest set bit), so filling a whole table costs a constant amount
per entry instead of recounting each number from scratch.

Two things generalize here. First, *precomputing a lookup table* of popcounts: a
common real trick is to compute counts for all 8-bit or 16-bit values once, then
popcount any word with a couple of table lookups — used in database bitmap
engines, in compression, and on older processors with no `POPCNT` instruction.
Second, the DP habit of *building big answers from overlapping small ones* is
behind everything from parsing to spell-check edit distance to routing tables;
this is a clean, minimal example of it.

What you get is time: linear to fill the whole array instead of `n log n`, by
never redoing work the loop already did. When you need popcounts for a dense range
of values (histograms, bitmap stats), precomputing them this way turns a per-item
cost into a single cheap table read.

## Start from the obvious

Count each number on its own. To count the `1`-bits of a single number, keep
clearing its lowest set bit until nothing is left:

```diagram
   count the ones in x = 10110 (22) by clearing the lowest 1 each step

     10110  --(& x-1)-->  10100   count 1
     10100  --(& x-1)-->  10000   count 2
     10000  --(& x-1)-->  00000   count 3   done
```

Why does `x & (x - 1)` clear the lowest set bit? Subtracting 1 flips the lowest
`1` to `0` and turns every `0` below it into `1`. AND-ing with the original keeps
everything above untouched and wipes out that bottom run:

```diagram
     x      = 1 0 1 1 0
     x - 1  = 1 0 1 0 1
     -----------------
     x & .. = 1 0 1 0 0     the lowest set bit is gone
```

Each number has at most about `log2(i)` set bits, so counting them all this way is
`n log n`. Correct, and the right first thing to write.

## Find the waste

You count every number from scratch, as if you'd never seen a similar one. But
binary numbers are built out of each other. Take `6 = 110`. Erase its lowest `1`
and you get `100 = 4` — a number you already counted earlier in the loop. The only
difference between `6` and `4` is that one extra `1` you erased.

## The insight

Clearing the lowest set bit with `i & (i - 1)` always lands on a *smaller* number
whose count you already know. That step removed exactly one `1`, so:

```
ans[i] = ans[i & (i - 1)] + 1
```

```diagram
   fill the table left to right; each cell points back to a smaller solved one

   i=6 = 110   i&(i-1)=100=4    ans[6] = ans[4] + 1 = 1 + 1 = 2
                        ^--------------------+
   i=7 = 111   i&(i-1)=110=6    ans[7] = ans[6] + 1 = 2 + 1 = 3
                        ^--------------------+

   index:  0  1  1  2  1  2  [2] [3]
                             ^6  ^7   filled from earlier cells
```

Because `i & (i - 1)` is always smaller than `i`, its answer is already filled in
by the time you reach `i`. Every entry becomes one lookup plus one add.

## Complexity

- **Time: about n steps.** One pass, each entry is constant work — the brute
  version's `log n` per-number factor is gone.
- **Extra memory: constant** beyond the output array you must return.

## Pitfalls

- The array has length `n + 1`, not `n` — index `0` through `n` inclusive.
- Off-by-one on `i & (i - 1)` when `i = 0`; start the loop at `i = 1` and leave
  `ans[0] = 0`.
- Reaching for Python's `bin(i).count("1")` works but hides the point; the DP
  relation is what this problem is teaching.

## Transfer

The trick `x & (x - 1)` (clear the lowest set bit) shows up in
[Number of 1 Bits / 191](../0191-number-of-1-bits/) and in any "is this a power of
two?" check (`x & (x - 1) == 0`). The broader move — "a bigger case is a smaller
solved case plus one cheap step" — is the heart of DP, the same shape as
[Climbing Stairs](../../13-dynamic-programming/) style problems.
