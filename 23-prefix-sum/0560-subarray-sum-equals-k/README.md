# 560. Subarray Sum Equals K

**Pattern:** Prefix sum + hash map (count subarrays with a property)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/subarray-sum-equals-k/

## The problem in plain words

Count how many contiguous stretches of the array add up to exactly `k`. The numbers
can be negative and zero, so a stretch can hit `k`, overshoot, then come back — you
have to consider all of them.

```diagram
   nums = [ 1, 1, 1 ]   k = 2

   stretches that sum to 2:
       [1,1] at indices 0..1
       [1,1] at indices 1..2
   answer = 2
```

## Why this matters

This is the moment prefix sums stop being about *range queries* and become a way to
answer *"how many subarrays have this property?"* in a single pass. The core
realization: a subarray's sum is the difference of two running totals, so "does some
subarray ending here sum to `k`?" turns into "have I seen a running total equal to
`current − k` before?" — a hash-map lookup, exactly like Two Sum.

Concretely, this shows up in ledgers and streams. "Find a run of daily cash-flows
that nets to a target" is this problem. Detecting a window of sensor deltas that sum
to a threshold, or spans of a request log whose signed counts balance out, are the
same shape. Because values can be negative, the greedy sliding window doesn't
apply — which is exactly why the running-total map is the right tool.

What the good solution buys is one pass over data you often can't rewind, at about
`n` steps instead of `n²`. On a large log or an unbounded stream, that is the
difference between keeping up in real time and falling behind.

## Start from the obvious

Try every subarray and add it up.

```diagram
   count = 0
   for start in 0..n-1:
       running = 0
       for end in start..n-1:
           running += nums[end]
           if running == k:
               count += 1
```

About `n²`. Correct, and the right first thought. Now look at what it repeats.

## Find the waste

Every `start` re-walks the tail from scratch, recomputing sums that overlap heavily
with the previous `start`. The sum of `nums[i..j]` is really just
`prefix[j+1] - prefix[i]`, where `prefix[m]` is the sum of the first `m` elements.
So a subarray `(i..j)` sums to `k` exactly when their two running totals differ by
`k`.

```diagram
   prefix[j+1] - prefix[i] == k
       <=>   prefix[i] == prefix[j+1] - k

   like Two Sum: the running total we need is FIXED, not searched.
   we only need to know HOW MANY earlier running totals had that value.
```

## The insight

Sweep once, keeping the running total. At each position, the number of subarrays
ending here that sum to `k` is the number of times we have already seen the running
total `running − k`. Keep a dict `running total -> how many times seen`.

```diagram
   nums = [ 1, -1, 0 ]   k = 0     seen = {0: 1}   (empty prefix, before we start)

   x    running   need running-k = running-0   seen.get -> add   update seen
   1    1         need 1   seen has 1? no  -> +0    seen={0:1, 1:1}
  -1    0         need 0   seen has 0? YES x1 -> +1  seen={0:2, 1:1}
   0    0         need 0   seen has 0? YES x2 -> +2  seen={0:3, 1:1}

   count = 0 + 1 + 2 = 3
   the three runs: [1,-1]  [0]  [1,-1,0]
```

The seed `{0: 1}` is what lets subarrays starting at index 0 be counted: a prefix of
`k` then matches `running − k == 0`, which we have "seen" once (the empty prefix). We
count *before* inserting the current running total so a subarray can't be empty.

```diagram
   why count-before-insert matters (k=0 case above):

   at x=-1 running becomes 0.  if we inserted seen[0] FIRST (making it 2),
   then looked up need=0, we'd count the just-added entry -> an EMPTY subarray.
   look up first, then insert:  each match is a real, non-empty run.
```

## Complexity

- **Time: about n** — one pass; each map lookup/update is constant on average.
- **Extra memory: about n** — the map may hold up to `n` distinct running totals.

## Pitfalls

- **Don't use a sliding window.** Negatives break the up-only assumption a window
  relies on; you must consider all start points, which the running-total map does
  for you.
- Forgetting the `{0: 1}` seed — you'll miss every subarray that starts at index 0.
- Counting *after* inserting the current running total, which can let
  `running - k == running` match the just-inserted entry and count an empty
  subarray.
- We want the **count**, not just existence — add up `seen[running - k]`, not a
  yes/no.

## Transfer

This "prefix sum + hash map to count/find subarrays with a property" template is the
heart of the pattern. Its close siblings:
[Contiguous Array / 525](../0525-contiguous-array/) (map `0` to `−1` to hit "equal
counts"), subarray-sum-divisible-by-k (bucket running totals by remainder), and it
is literally Two Sum on running totals — same lookup, different key.
