# 525. Contiguous Array

**Pattern:** Prefix sum + hash map (relabel to a running balance)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/contiguous-array/

## The problem in plain words

You have an array of just `0`s and `1`s. Find the longest contiguous stretch that
contains the *same number* of `0`s and `1`s, and return its length.

## Why this matters

The lesson here is a relabeling trick that converts a *counting* condition into a
*sum* condition, so prefix sums apply. Replace every `0` with `−1`. Now "equal
zeros and ones" is exactly "this stretch sums to `0`", and a stretch sums to zero
precisely when its two endpoints have the *same* running total. Finding the
longest such stretch becomes: for each prefix value, how early did we first see
it?

This "turn a balance into a sum, then compare prefixes" move is everywhere you
track two competing quantities over time. Finding the longest span where wins
equal losses, credits equal debits, or bytes-in equal bytes-out is this problem.
Log analysis for the longest window where opens balance closes, or up-votes
balance down-votes, is the same relabel. More generally it's the template for
"longest subarray with property P" whenever P is really a statement about equal
prefix sums.

What the good solution buys is a single pass at `O(n)` instead of the `O(n²)` of
re-checking every subarray — the practical difference on a long log or stream.

## Start from the obvious

Check every subarray; count its zeros and ones.

```
best = 0
for start in range(n):
    balance = 0
    for end in range(start, n):
        balance += 1 if nums[end] == 1 else -1
        if balance == 0:
            best = max(best, end - start + 1)
```

`O(n²)`, correct, right first thought. The `balance` variable is already the clue.

## Find the waste

Every `start` recomputes the running balance from scratch, even though most of
that work overlaps the previous start. Define a global running balance where `1`
adds `+1` and `0` adds `−1`. A subarray `(i..j)` is balanced when:

```
balance_after(j) == balance_before(i)
```

i.e. the running total is the *same* at both ends — everything in between summed
to zero. So instead of re-summing, we just watch for a balance value we've seen
before.

## The insight

Sweep once, maintaining the running balance. The moment the current balance
equals a value seen at some earlier index, the stretch in between is balanced —
and to make it *longest*, we want the *earliest* time we saw that value. So store
each balance's **first** index only:

```
best, balance = 0, 0
first_seen = {0: -1}          # balance 0 exists "before index 0"
for i, x in enumerate(nums):
    balance += 1 if x == 1 else -1
    if balance in first_seen:
        best = max(best, i - first_seen[balance])
    else:
        first_seen[balance] = i     # keep only the earliest occurrence
```

The seed `{0: -1}` is what lets a balanced run that starts at index `0` be
measured: its balance returns to `0`, which we treat as first seen "before the
array" at index `−1`, giving length `i - (-1) = i + 1`.

## Complexity

- **Time:** `O(n)` — one pass, `O(1)` map operations.
- **Space:** `O(n)` — the map holds each distinct balance once; balances range
  over `[-n, n]`.

## Pitfalls

- **Store the earliest index, not the latest.** If a balance repeats, do *not*
  overwrite — the first occurrence gives the longest span.
- Forgetting the `{0: -1}` seed — runs starting at index 0 come out one short (or
  missed entirely).
- Trying a sliding window: because entries are `±1`, the balance is non-monotonic,
  so a window won't work — you genuinely need the prefix map.
- Returning the balance or a count instead of the **length**.

## Transfer

Same engine as [Subarray Sum Equals K / 560](../0560-subarray-sum-equals-k/) —
prefix sum plus a hash map — but the key is "have I seen this exact prefix
before?" (with earliest index) rather than "have I seen `current − k`?". The
relabel-to-`±1` idea generalizes: any "equal counts of A and B" question becomes a
prefix-sum-equals-zero question, and problems asking for the longest balanced
window reuse this pattern directly.
