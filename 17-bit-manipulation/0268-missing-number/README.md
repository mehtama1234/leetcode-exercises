# 268. Missing Number

**Pattern:** XOR cancellation (matching pairs vanish, the lone one survives)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/missing-number/

## The problem in plain words

You have an array of `n` distinct numbers. They're supposed to be the whole range
`0, 1, 2, ..., n` — that's `n + 1` slots — but one number is missing. Find the one
that isn't there.

Example: `[3, 0, 1]`. The full range is `0, 1, 2, 3`. The array has `0, 1, 3`, so
`2` is the missing one.

```diagram
   should be present:  0  1  2  3
   actually present:   0  1  .  3     ( . = the gap )
                              ^
                          missing = 2
```

## Why this matters

The deeper idea is **XOR cancellation**: a value XOR'd with itself becomes `0`, so
things that appear an even number of times all vanish and the one unpaired item
survives — and you find it without ever storing what you've already seen. A close
cousin uses a **known total**: add up what the range *should* sum to, subtract
what's actually there, and the shortfall is the missing value. Both replace a
lookup structure with one accumulating number.

Where this is genuinely used: RAID storage keeps a parity block that is the XOR of
the others, so a lost disk is rebuilt by XOR-ing what remains — literally
"recover the missing element." Checksums fold data together with XOR. Reconciling
"what should be present" against "what is" via a sum or XOR digest is how systems
spot the one dropped record. And "find the single unpaired value" problems all
collapse to the same `x ^ x == 0` fact.

What you get is linear time with constant memory and no overflow risk — one pass,
one number, no hash set — which matters when the dataset is huge or the check runs
on a memory-starved or streaming path.

## Start from the obvious

Put the array in a set and walk `0..n` asking "is this one here?":

```diagram
   seen = { 3, 0, 1 }

   v=0  in seen? yes
   v=1  in seen? yes
   v=2  in seen? NO   -> answer 2
   v=3  in seen? yes
```

That's linear time but it also spends extra memory the size of the whole array on
the set. It works, and it makes the shape clear: you're comparing "the range that
should be there" against "what actually is." The question is whether you can do
that comparison without a whole extra set.

## Find the waste

The set stores every present number just to detect the one absent one. That's a
lot of bookkeeping for a single answer. Two cheaper ways to capture "what's
present versus what should be present":

**Sum.** The numbers `0..n` add up to a fixed total, `n(n+1)/2`. The actual array
falls short of that total by exactly the missing value: `missing = n(n+1)/2 -
sum(nums)`.

**XOR.** Even better, because it never builds large numbers and never overflows.

## The insight

XOR has two properties that make missing-element problems collapse:

- `x ^ x == 0` — any value XOR'd with itself vanishes.
- `x ^ 0 == x` — XOR with zero changes nothing.

XOR also doesn't care about order. So XOR together **all the indices `0..n`** and
**all the values in the array**. Every number that appears in both lists pairs off
and cancels to `0`. The missing number shows up as an index but has no matching
value, so it's the lone survivor.

Work through `nums = [3, 0, 1]` (n = 3, missing 2). Seed the accumulator with `n`,
then fold in each `i` and each `nums[i]`:

```diagram
   acc starts at 3   (seed with n, the top of the value range)

   i | index | value | fold in i^value | acc
   --+-------+-------+-----------------+----
   0 |   0   |   3   |   3 ^ 0 ^ 3     |  0
   1 |   1   |   0   |   0 ^ 1 ^ 0     |  1
   2 |   2   |   1   |   1 ^ 2 ^ 1     |  2   <- survivor = missing number

   every value that appears as both an index and an array entry cancels;
   only 2 (an index with no matching value) is left standing
```

You seed `acc` with `n` because the indices only reach `0..n-1`, but the values
range over `0..n`. Seeding folds that top value `n` in.

## Complexity

- **Time: about n steps.** A single pass, one XOR per element.
- **Extra memory: constant.** Just the running number — no set, no sorted copy.

## Pitfalls

- Forgetting the range is `0..n` (that's n+1 values), not `0..n-1`. That's why you
  must fold in `n` separately — as the seed, or with one extra XOR.
- Using the sum formula in a fixed-width language: `n(n+1)/2` can overflow for
  large `n`. XOR never does — it stays inside the same bit width.
- Assuming the input is sorted. It isn't, and XOR doesn't need it to be.

## Transfer

XOR-cancellation is the go-to when elements pair up and you want the odd one out:
[Single Number / 136](../) (every number appears twice except one — the whole
array XOR'd together leaves it). The general move is "encode presence as XOR and
let duplicates annihilate." The sum-invariant idea also transfers to "find the
duplicate or missing value when one is off."
