# 560. Subarray Sum Equals K

**Pattern:** Prefix sum + hash map (count subarrays with a property)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/subarray-sum-equals-k/

## The problem in plain words

Count how many contiguous stretches of the array add up to exactly `k`. The
numbers can be negative and zero, so a stretch can hit `k`, overshoot, then come
back — you have to consider all of them.

## Why this matters

This is the moment prefix sums stop being about *range queries* and become a way
to answer *"how many subarrays have this property?"* in a single pass. The core
realization: a subarray's sum is the difference of two prefix sums, so "does some
subarray ending here sum to `k`?" turns into "have I seen a prefix sum equal to
`current − k` before?" — a hash-map membership question, exactly like Two Sum.

Concretely, this shows up in ledgers and streams. "Find a run of daily
cash-flows that nets to zero" (or to a target) is this problem. Detecting a
window of sensor deltas that sum to a threshold, or spans of a request log whose
signed counts balance out, are the same shape. Because values can be negative,
the greedy sliding window doesn't apply — which is precisely why the prefix-sum
map is the right tool.

What the good solution buys is one pass over data you often can't rewind, at
`O(n)` instead of `O(n²)`. On a large log or an unbounded stream, that's the
difference between keeping up in real time and falling behind.

## Start from the obvious

Try every subarray and add it up.

```
count = 0
for start in range(n):
    running = 0
    for end in range(start, n):
        running += nums[end]
        if running == k:
            count += 1
```

`O(n²)`. Correct, and the right first thought. Now look at what it repeats.

## Find the waste

Every `start` re-walks the tail from scratch, recomputing sums that overlap
heavily with the previous `start`. The sum of `nums[i..j]` is really just
`prefix[j+1] - prefix[i]`, where `prefix[m]` is the sum of the first `m`
elements. So a subarray `(i..j)` sums to `k` exactly when:

```
prefix[j+1] - prefix[i] == k
    <=>   prefix[i] == prefix[j+1] - k
```

We don't need to *search* for the matching start — like Two Sum, the value we
need is fully determined. We only need to know **how many** earlier prefixes had
that value.

## The insight

Sweep once, keeping the running prefix sum. At each position, the number of
subarrays ending here that sum to `k` is the number of times we've already seen
the prefix `running − k`. Keep a dict `prefix_sum -> count`:

```
count, running = 0, 0
seen = {0: 1}                      # empty prefix seen once, before we start
for x in nums:
    running += x
    count += seen.get(running - k, 0)   # each earlier match is one subarray
    seen[running] = seen.get(running, 0) + 1
```

The seed `{0: 1}` is what lets subarrays starting at index 0 be counted: a prefix
of `k` then matches `running − k == 0`, which we've "seen" once (the empty
prefix). We count *before* inserting the current prefix so a subarray can't be
empty.

## Complexity

- **Time:** `O(n)` — one pass; each map lookup/update is `O(1)` average.
- **Space:** `O(n)` — the map may hold up to `n` distinct prefix sums.

## Pitfalls

- **Don't use a sliding window.** Negatives break the monotonic assumption a
  window relies on; you must consider all start points, which the prefix map does
  implicitly.
- Forgetting the `{0: 1}` seed — you'll miss every subarray that starts at index
  0.
- Counting *after* inserting the current prefix, which can let `running - k == running`
  match the just-inserted entry and count an empty subarray.
- We want the **count**, not existence — accumulate `seen[running - k]`, not a
  boolean.

## Transfer

This "prefix sum + hash map to count/find subarrays with a property" template is
the heart of the pattern. Its close siblings:
[Contiguous Array / 525](../0525-contiguous-array/) (map 0→−1 to hit "equal
counts"), subarray-divisible-by-k (bucket prefixes by remainder), and it's
literally Two Sum on prefix sums — same membership check, different key.
