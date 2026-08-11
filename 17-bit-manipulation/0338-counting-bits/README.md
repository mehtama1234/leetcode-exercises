# 338. Counting Bits

**Pattern:** Bit manipulation + dynamic programming (reuse a smaller answer)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/counting-bits/

## The problem in plain words

For every number from `0` up to `n`, count how many `1`s it has when written in
binary, and return all those counts in one array. So for `n = 5` you want the
counts for `0, 1, 2, 3, 4, 5`:

```
0 = 000 -> 0 ones
1 = 001 -> 1 one
2 = 010 -> 1 one
3 = 011 -> 2 ones
4 = 100 -> 1 one
5 = 101 -> 2 ones
```

Answer: `[0, 1, 1, 2, 1, 2]`.

## Start from the obvious

Count each number on its own. To count the 1-bits of a single number, keep
clearing its lowest set bit until nothing is left:

```
count = 0
while x:
    x &= x - 1   # this clears the lowest 1-bit
    count += 1
```

Why does `x & (x - 1)` clear the lowest set bit? Subtracting 1 flips the lowest
`1` to `0` and turns every `0` below it into `1`. AND-ing with the original
keeps everything above untouched and wipes out that bottom run:

```
x     = 10110   (22)
x - 1 = 10101
x&x-1 = 10100   (lowest set bit gone)
```

Each number has at most `log2(i)` set bits, so this is `O(n log n)`. Correct,
and the right first thing to write.

## Find the waste

We count every number from scratch, as if we'd never seen a similar number
before. But binary numbers are built out of each other. Take `6 = 110`. If you
erase its lowest `1`, you get `100 = 4` — a number we already counted earlier in
the loop. The only difference between `6` and `4` is that one extra `1` we
erased.

## The insight

Clearing the lowest set bit with `i & (i - 1)` always lands on a *smaller*
number whose count we already know. That step removed exactly one `1`, so:

```
ans[i] = ans[i & (i - 1)] + 1
```

Worked through:

```
i = 6 = 110  -> i & (i-1) = 100 = 4,  ans[6] = ans[4] + 1 = 1 + 1 = 2
i = 7 = 111  -> i & (i-1) = 110 = 6,  ans[7] = ans[6] + 1 = 2 + 1 = 3
```

Because `i & (i - 1) < i`, its answer is already filled in by the time we reach
`i`. Every entry is now one lookup plus one add.

## Complexity

- **Time:** `O(n)` — one pass, each entry is `O(1)` (drop the brute's `log n`
  per-number factor).
- **Space:** `O(1)` beyond the output array we must return.

## Pitfalls

- The array has length `n + 1`, not `n` — index `0` through `n` inclusive.
- Off-by-one on `i & (i - 1)` when `i = 0`; start the DP loop at `i = 1` and
  leave `ans[0] = 0`.
- Reaching for Python's `bin(i).count("1")` works but hides the point; the DP
  relation is what the problem is teaching.

## Transfer

The trick `x & (x - 1)` (clear the lowest set bit) shows up in
[Number of 1 Bits / 191](../0191-number-of-1-bits/) and in any "is this a power
of two?" check (`x & (x - 1) == 0`). The broader move — "a bigger case is a
smaller solved case plus one cheap step" — is the heart of DP, same shape as
[Climbing Stairs](../../13-dynamic-programming/) style recurrences.
