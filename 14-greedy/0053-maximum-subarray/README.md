# 53. Maximum Subarray

**Pattern:** Greedy (Kadane's algorithm — best-ending-here)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/maximum-subarray/

## The problem in plain words

You have a row of numbers, some positive, some negative. Pick a **contiguous**
run of them (you can't skip around) — at least one number — so that the run's sum
is as large as possible. Return that largest sum.

## Start from the obvious

A "contiguous run" is defined by where it starts and where it ends. So just try
all of them:

```
best = nums[0]
for each start i:
    running = 0
    for each end j >= i:
        running += nums[j]
        best = max(best, running)
```

That's `O(n^2)`. It's correct and it's the right first move — but notice what it
keeps doing.

## Find the waste

For start `i` we add up `nums[i..j]`. Then for start `i+1` we add up
`nums[i+1..j]` from scratch — re-touching almost the same elements. We recompute
overlapping sums again and again. The fix is to stop thinking "for each start,
scan forward" and instead sweep left to right **once**, keeping a single fact up
to date.

## The insight

Ask a smaller question at each position: *what is the best subarray that ends
exactly here?* Call it `cur`. Standing on element `x`, a subarray ending at `x`
is either:

- just `x` by itself, or
- `x` tacked onto the best subarray that ended at the **previous** element.

So:

```
cur = max(x, cur + x)
```

Then the answer to the whole problem is just the largest `cur` over all
positions (`best = max(best, cur)`), because the globally best subarray has to end
*somewhere*, and we check every "somewhere".

**Why is the greedy choice safe?** The only decision is: when I reach `x`, do I
extend the previous run or start a new one at `x`? Extend only if the previous
run's sum (`cur`) is positive — because then it *adds* to `x`. If `cur` is
negative, carrying it forward would only shrink every future sum, so dropping it
and restarting at `x` is never worse. That's exactly what `max(x, cur + x)`
encodes: when `cur < 0`, `x` wins; when `cur >= 0`, extending wins. There's no
scenario where hauling a negative prefix along helps, so the greedy discard loses
nothing.

If we *didn't* reset — if we naively kept accumulating — a single bad stretch
early on would poison every later subarray sum, and we'd report a total smaller
than the real best. Resetting at the right moment is the whole trick.

## Complexity

- **Time:** `O(n)` — one pass, constant work per element.
- **Space:** `O(1)` — two running numbers (`cur`, `best`), nothing that grows.

## Pitfalls

- **Initializing `best` to 0.** If every number is negative (e.g. `[-3, -1, -2]`),
  the answer is `-1`, not `0` — you must pick at least one element. Seed both
  `cur` and `best` from `nums[0]`, not from `0`.
- **Confusing `cur` and `best`.** `cur` is "best ending here" and can dip; `best`
  is the high-water mark and never decreases. You need both.
- **Allowing an empty subarray.** The problem requires length `>= 1`. Starting the
  loop at `nums[1:]` with the seed above guarantees at least one element is used.
- **Reaching for divide-and-conquer.** There's a clever `O(n log n)` split
  solution, but Kadane is simpler and strictly faster; don't over-engineer.

## Transfer

The reusable idea is **"best-ending-here": carry one rolling quantity that answers
a per-position subproblem, and discard it the moment it turns into deadweight.**
This is greedy and DP at the same time. Siblings:
[Maximum Product Subarray / 152](https://leetcode.com/problems/maximum-product-subarray/)
(same shape, but track best *and* worst because a negative flips them),
[Best Time to Buy and Sell Stock / 121](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/)
(track the running minimum instead of a running sum),
[Maximum Circular Subarray / 918](https://leetcode.com/problems/maximum-sum-circular-subarray/).
Whenever an answer is "best contiguous window", ask "what's the best one ending
right here?" first.
