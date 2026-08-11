# 268. Missing Number

**Pattern:** Bit manipulation (XOR cancellation) / arithmetic invariant
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/missing-number/

## The problem in plain words

You have an array of `n` distinct numbers, and they're supposed to be the whole
range `0, 1, 2, ..., n` — that's `n + 1` slots — but one number is missing. Find
the one that isn't there.

Example: `[3, 0, 1]`. The full range is `0, 1, 2, 3`. The array has `0, 1, 3`,
so `2` is missing.

## Start from the obvious

Put the array in a set and walk `0..n` asking "is this one here?":

```
seen = set(nums)
for v in range(len(nums) + 1):
    if v not in seen:
        return v
```

That's `O(n)` time but `O(n)` extra space. It works, and it makes the structure
clear: we're comparing "the range that should be there" against "what actually
is there." The question is whether we can do that comparison without a whole
extra set.

## Find the waste

The set stores every present number just to detect the one absent one. That's a
lot of bookkeeping for a single answer. Two cheaper ways to capture "what's
present vs. what should be present":

**Sum.** The numbers `0..n` add up to a fixed total `n(n+1)/2`. The actual array
falls short of that total by exactly the missing value:

```
missing = n(n+1)/2 - sum(nums)
```

**XOR.** Even better, because it never grows large numbers or overflows.

## The insight

XOR has two properties that make missing-element problems collapse:

- `x ^ x == 0` — any value XOR'd with itself vanishes.
- `x ^ 0 == x` — XOR with zero changes nothing.

And XOR doesn't care about order. So XOR together **all the indices `0..n`** and
**all the values in the array**. Every number that shows up in both lists pairs
off and cancels to `0`. The missing number appears as an index but has no
matching value, so it's the lone survivor.

Concretely for `nums = [3, 0, 1]` (n = 3, missing 2). Seed with `n = 3`, then
fold in each `i ^ nums[i]`:

```
acc = 3                          (seed with n, the top of the value range)
i=0: acc ^= 0 ^ 3  ->  3^0^3 = 0
i=1: acc ^= 1 ^ 0  ->  0^1^0 = 1
i=2: acc ^= 2 ^ 1  ->  1^2^1 = 2   <- survivor = missing number
```

We seed `acc` with `n` because the indices only reach `0..n-1`, but the values
range over `0..n`. Seeding folds that top value `n` in.

## Complexity

- **Time:** `O(n)` — a single pass, one XOR per element.
- **Space:** `O(1)` — just the running accumulator; no set, no sorted copy.

## Pitfalls

- Forgetting the range is `0..n` (n+1 values), not `0..n-1`. That's why you must
  fold in `n` separately (as the seed, or with an extra XOR).
- Using the sum formula in a fixed-width language: `n(n+1)/2` can overflow for
  large `n`. XOR never does — it stays within the same bit width.
- Assuming the input is sorted. It isn't, and XOR doesn't need it to be.

## Transfer

XOR-cancellation is the go-to when elements pair up and you want the odd one
out: [Single Number / 136](../) (every number appears twice except one — pure
XOR of the whole array). The general move is "encode presence as XOR and let
duplicates annihilate." The sum-invariant idea also transfers to "find the
duplicate/missing when one value is off."
