# 643. Maximum Average Subarray I

**Pattern:** Sliding window (fixed size)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/maximum-average-subarray-i/

## The problem in plain words

You have a list of numbers and a size `k`. Look at every block of `k`
numbers-in-a-row, and find the one with the biggest average. Return that average.

One thing to notice up front: because every block has the *same* length `k`,
dividing by `k` never changes which block wins. So "biggest average" is exactly
"biggest sum" — we only ever have to compare sums, and divide once at the end.

## Why this matters

This is the **fixed-width sliding aggregate**: compute a summary (here a sum) over every consecutive block of size `k`, without recomputing the whole block each step. The fundamental operation is the *add-one / drop-one* update — as the window slides, one element enters on the right and one leaves on the left, so each step is constant work.

This is exactly how real systems compute windowed statistics over streams:

- **Moving averages** — the canonical smoothing tool for stock prices, sensor readings, and dashboards, computed with a rolling sum rather than re-summing.
- **Rolling metrics and rate limiting** — requests-per-last-`k`-seconds, or a moving sum of errors, maintained incrementally as events tick by.
- **Signal and audio processing** — box filters and running energy over a fixed window applied across a whole sample stream.

What we're solving for is **cutting per-window cost from `O(k)` to `O(1)`**, turning an `O(n·k)` scan into `O(n)` at constant memory. For long streams or large windows that's the difference between a cheap real-time computation and one that can't keep up.

## Start from the obvious

The definition itself hands you an algorithm: for each starting spot, add up the
`k` numbers there, and remember the best sum.

```
best = -infinity
for each start i:
    s = sum(nums[i .. i+k-1])
    best = max(best, s)
return best / k
```

That's `O(n*k)`: there are about `n` windows, and each one costs `k` to add up.
It's correct, and it's the right first thought — staring at *why* it's slow tells
you what to fix.

## Find the waste

Look at two windows that sit next to each other:

```
[1, 12, -5, -6]  50   3      window A
 1  [12, -5, -6, 50]  3      window B
```

They share `12, -5, -6` — that's `k-1` of the `k` elements. The brute force adds
those shared numbers again from scratch every single step. The only *real* change
from A to B is: the `1` on the left leaves, and the `50` on the right joins.

## The insight

Keep a **running sum** of the current window. To slide one step right, don't
re-add anything — just:

1. Add the element entering on the right.
2. Subtract the element leaving on the left.

```
window_sum = sum(first k elements)
best = window_sum
for i from k to n-1:
    window_sum += nums[i] - nums[i-k]   # newcomer in, leaver out
    best = max(best, window_sum)
return best / k
```

Each element is added exactly once and removed exactly once over the whole scan,
so the total work is `O(n)`.

## Complexity

- **Time:** `O(n)` — one pass; each slide is two arithmetic operations.
- **Space:** `O(1)` — we only keep the running sum and the best-so-far.

The brute force is `O(n*k)`; the running sum turns the per-window cost from `k`
down to constant.

## Pitfalls

- Re-summing the whole window each step (the accidental `O(n*k)` trap).
- Returning the **sum** instead of the average — divide by `k` at the end.
- Integer division: divide by `float(k)` (or use `/` in Python 3) or you'll floor
  the answer.
- Comparing averages with `==`: they're floating point, so compare within a tiny
  tolerance in tests.
- Forgetting `best` must start at `-infinity` (or at the first window's sum), not
  `0` — all-negative arrays would break a `0` start.

## Transfer

The move "keep a running total and update it as the window slides" is the whole
fixed-size sliding-window pattern. It reappears whenever you're asked about every
block of a fixed length: maximum sum of `k` consecutive elements, counting
[distinct/vowel windows], or moving averages of a data stream. Whenever a brute
force re-scans overlapping windows, reach for the add-one / drop-one update first.
