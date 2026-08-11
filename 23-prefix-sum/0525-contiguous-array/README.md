# 525. Contiguous Array

**Pattern:** Prefix sum + hash map (relabel to a running balance)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/contiguous-array/

## The problem in plain words

You have an array of just `0`s and `1`s. Find the longest contiguous stretch that
holds the *same number* of `0`s and `1`s, and return its length.

```diagram
   index:  0  1  2  3  4  5  6  7
   nums: [ 0  0  1  0  0  0  1  1 ]
             [ ==== equal 0s and 1s ==== ]
             indices 2..7: three 0s, three 1s  ->  length 6
```

## Why this matters

The lesson is a relabeling trick that turns a *counting* condition into a *sum*
condition, so prefix sums apply. Replace every `0` with `−1`. Now "equal zeros and
ones" is exactly "this stretch sums to `0`", and a stretch sums to zero precisely
when its two ends have the *same* running total. Finding the longest such stretch
becomes: for each running-total value, how early did we first see it?

This "turn a balance into a sum, then compare running totals" move is everywhere
you track two competing quantities over time. Finding the longest span where wins
equal losses, credits equal debits, or bytes-in equal bytes-out is this problem.
Log analysis for the longest window where opens balance closes, or up-votes balance
down-votes, is the same relabel. More broadly it is the template for "longest
subarray with property P" whenever P is really a statement about equal running
totals.

What the good solution buys is a single pass at about `n` steps instead of the
`n²` of re-checking every subarray — the practical difference on a long log or
stream.

## Start from the obvious

Check every subarray; count its zeros and ones.

```diagram
   best = 0
   for start in 0..n-1:
       balance = 0
       for end in start..n-1:
           balance += (nums[end] == 1) ? +1 : -1
           if balance == 0:
               best = max(best, end - start + 1)
```

About `n²`, correct, the right first thought. The `balance` variable is already
the clue.

## Find the waste

Every `start` recomputes the running balance from scratch, even though most of that
work overlaps the previous start. Define one global running balance where `1` adds
`+1` and `0` adds `−1`. A subarray is balanced when the running total is the *same*
at both ends — everything in between summed to zero.

```diagram
   nums:      0   1   0   1
   relabel:  -1  +1  -1  +1
   balance: 0  -1   0  -1   0
           ^                 ^
        before idx0       after idx3
        both are 0  ->  the whole stretch 0..3 sums to 0  ->  balanced, length 4
```

So instead of re-summing, watch for a balance value you have seen before.

## The insight

Sweep once, keeping the running balance. The moment the current balance equals a
value seen at some earlier index, the stretch in between is balanced — and to make
it *longest*, we want the *earliest* time we saw that value. So store each balance's
**first** index only.

```diagram
   nums:      0    0    1    0    0    0    1    1
   relabel:  -1   -1   +1   -1   -1   -1   +1   +1

   i:  balance   first_seen (balance -> earliest index)   length if repeat
   -   0         {0: -1}                                    (seed)
   0   -1        new -> {0:-1, -1:0}
   1   -2        new -> add -2:1
   2   -1        SEEN at 0  ->  i - 0 = 2 - 0 = 2
   3   -2        SEEN at 1  ->  3 - 1 = 2
   4   -3        new -> add -3:4
   5   -4        new -> add -4:5
   6   -3        SEEN at 4  ->  6 - 4 = 2
   7   -2        SEEN at 1  ->  7 - 1 = 6   <- longest

   answer = 6
```

The seed `{0: -1}` is what lets a balanced run that starts at index `0` be measured:
its balance returns to `0`, which we treat as first seen "before the array" at index
`−1`, giving length `i - (-1) = i + 1`.

## Complexity

- **Time: about n** — one pass, constant-time map operations.
- **Extra memory: about n** — the map holds each distinct balance once; balances
  range over `[-n, n]`.

## Pitfalls

- **Store the earliest index, not the latest.** If a balance repeats, do *not*
  overwrite — the first occurrence gives the longest span.
- Forgetting the `{0: -1}` seed — runs starting at index 0 come out one short (or
  are missed entirely).
- Trying a sliding window: because entries are `+1`/`−1`, the balance goes up and
  down, so a window won't work — you genuinely need the running-total map.
- Returning the balance or a count instead of the **length**.

## Transfer

Same engine as [Subarray Sum Equals K / 560](../0560-subarray-sum-equals-k/) —
prefix sum plus a hash map — but the key here is "have I seen this exact running
total before?" (earliest index) rather than "have I seen `current − k`?". The
relabel-to-`±1` idea generalizes: any "equal counts of A and B" question becomes a
running-total-equals-zero question, and problems asking for the longest balanced
window reuse this pattern directly.
