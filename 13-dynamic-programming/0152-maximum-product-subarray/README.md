# 152. Maximum Product Subarray

**Pattern:** Dynamic programming (rolling state — track max *and* min)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/maximum-product-subarray/

## The problem in plain words

Among all contiguous subarrays, find the one whose numbers multiply to the largest
value, and return that product. The array may hold negatives and zeros. Example:
`[2, 3, -2, 4]` → `6` (from `[2, 3]`).

## Start from the obvious

Try every subarray and multiply it out, keeping the best:

```
best = nums[0]
for i in range(n):
    prod = 1
    for j in range(i, n):
        prod *= nums[j]
        best = max(best, prod)
```

`O(n^2)`. Correct, and it re-multiplies overlapping prefixes constantly — that's
the waste. We'd like a single pass.

## Find the waste

The single-pass instinct is Kadane's trick: carry "best product ending right
here" and extend it. But products have a trap that sums don't:

> a **negative** number flips sign, so the *smallest* running product can suddenly
> become the *largest* when the next negative arrives.

Consider `[-2, 3, -4]`. If you only tracked the running max, `-2` then `3` gives a
max of `3`, and multiplying by `-4` looks like `-12`. But the true answer is `24`,
from all three: `(-2) * 3 * (-4)`. The `-6` you'd have thrown away as "worst" is
exactly what becomes best after the final negative.

## The insight

Track **two** rolling values at each index: the largest product ending here *and*
the smallest (most negative) product ending here. For each new number `x`, the best
subarray ending at `x` is one of three:

- `x` by itself (start a fresh run — this handles zeros resetting the product),
- `cur_max * x` (extend the best run),
- `cur_min * x` (extend the worst run — which, if `x < 0`, may now be best).

So compute all three candidates, then set `cur_max = max` of them and
`cur_min = min` of them. Keep a global `best`. Because a negative `x` swaps which
of max/min is larger, carrying the min is what makes it correct.

```
best = cur_max = cur_min = nums[0]
for x in nums[1:]:
    candidates = (x, cur_max*x, cur_min*x)
    cur_max, cur_min = max(candidates), min(candidates)
    best = max(best, cur_max)
```

## Complexity

- **Brute force:** `O(n^2)` time, `O(1)` space.
- **Rolling min/max:** `O(n)` time, `O(1)` space — one pass, two carried numbers.

## Pitfalls

- Tracking only the running max and dropping the min — this is *the* mistake here,
  and it fails on any input where two negatives should combine.
- Computing `cur_max` first and then reusing the *updated* `cur_max` when computing
  `cur_min`. Read both from the same candidate triple before assigning either.
- Zeros: including `x` itself as a candidate lets the run restart cleanly after a
  zero (a zero makes all three candidates involve 0, and the next element starts
  fresh via the `x`-alone option).
- Initializing `best` to `0` or `1` — start it at `nums[0]` so all-negative or
  single-element arrays work.

## Transfer

This is [Maximum Subarray / 53](../../02-arrays-hashing/) (Kadane's algorithm) with
a twist: because the combining operation (multiply) can flip sign, you carry both
extremes instead of one. The general lesson — **when your running state can be
"rescued" by a future operation, track the states that could become optimal, not
just the current best** — shows up whenever signs, mins/maxes, or parities interact.
