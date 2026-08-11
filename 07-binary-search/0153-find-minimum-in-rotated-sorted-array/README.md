# 153. Find Minimum in Rotated Sorted Array

**Pattern:** Binary search on a rotated (piecewise-sorted) array
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/

## The problem in plain words

Start with a sorted array of distinct numbers, like `[1, 2, 3, 4, 5]`. "Rotate"
it some number of times — chop a chunk off the front and paste it on the back —
giving something like `[3, 4, 5, 1, 2]`. You're handed the rotated version and
asked for the smallest element. The catch: you must do it in `O(log n)`, so
scanning everything is off the table.

## Why this matters

The real task here isn't "find the smallest number" — it's **find the one discontinuity** in data that is otherwise monotonic. That's the fundamental operation: locate the single point where a smooth, increasing sequence breaks, using only `O(log n)` probes instead of reading everything.

That pattern shows up wherever a sorted or monotonic sequence has exactly one turning point. Circular/ring buffers wrap at an unknown offset, and finding the oldest entry is finding this cliff. Time-series with a counter reset or a rollover (sequence numbers, timestamps that wrap) have one break you must find to reorder the data. Consistent-hashing rings and rotated index structures need the wrap-around point located to resolve a lookup. It's also the shape behind "binary search on the answer": a monotone yes/no function has one boundary, and you hunt it the same way.

What you're solving for is time — turning an `O(n)` scan into `O(log n)` — which matters most when this runs inside a tight loop or under a strict latency budget, where reading every element repeatedly would dominate the cost.

## Start from the obvious

The smallest element is just... the minimum.

```
return min(nums)
```

Correct, but `O(n)` — it reads all `n` elements. The problem specifically asks
for `O(log n)`, which is a strong hint: there's hidden structure to exploit. The
`min` scan ignores it completely.

## Find the waste

A rotated sorted array isn't random — it's two sorted runs glued together. There
is exactly **one** spot where the order breaks: a bigger number sits right before
a smaller one. In `[4, 5, 6, 7, 0, 1, 2]` that break is `7 -> 0`, and the number
right after the break, `0`, is the minimum. So the real task isn't "find the
smallest number" — it's "**find the one cliff**", and a cliff is exactly the kind
of thing binary search can hunt by halving.

## The insight

Compare the middle element to the **rightmost** element of the current window:

- If `nums[mid] > nums[hi]`, the window is *not* sorted from `mid` to `hi` — the
  cliff lies somewhere to the right of `mid`. The minimum is over there, so set
  `lo = mid + 1` (mid itself can't be the min, since something smaller follows).
- Otherwise `nums[mid] <= nums[hi]`, so `[mid, hi]` *is* properly sorted. The
  minimum is at `mid` or to its left. Set `hi = mid` — and crucially **keep
  `mid`**, because `mid` might itself be the smallest element.

```
lo, hi = 0, len(nums) - 1
while lo < hi:
    mid = lo + (hi - lo) // 2
    if nums[mid] > nums[hi]: lo = mid + 1   # min is to the right
    else:                    hi = mid       # min is mid or left; don't drop mid
return nums[lo]
```

Why compare to `hi` and not `lo`? Comparing to `lo` is ambiguous — in a
not-rotated array `nums[mid] > nums[lo]` is normal and tells you nothing about
where the cliff is. The right edge gives a clean two-way split every time. When
the loop ends, `lo == hi` points at the one surviving element: the minimum.

## Complexity

- **Time:** `O(log n)` — each step halves the window, same as plain binary search.
- **Space:** `O(1)` — two indices, nothing grows with input size.

## Pitfalls

- **`hi = mid`, not `hi = mid - 1`.** In the sorted-right case, `mid` is a live
  candidate for the minimum, so you can't throw it away. This is why the loop uses
  `while lo < hi` (converge to one element) rather than `lo <= hi` — with
  `hi = mid` and `lo <= hi`, the window can stop shrinking and loop forever.
- **Comparing to the wrong edge.** Comparing `nums[mid]` to `nums[lo]` instead of
  `nums[hi]` breaks on the already-sorted case. Anchor on `hi`.
- **Not-rotated input.** `[11, 13, 15, 17]` is handled naturally: `nums[mid]` is
  always `<= nums[hi]`, so `hi` keeps walking left until `lo == hi == 0`.
- This version assumes **distinct** values. With duplicates (LeetCode 154),
  `nums[mid] == nums[hi]` is ambiguous and you fall back to `hi -= 1`, losing the
  `O(log n)` guarantee in the worst case.

## Transfer

The move — *use one comparison to decide which piecewise-sorted half holds the
break point* — is the foundation of
[Search in Rotated Sorted Array / 33](../0033-search-in-rotated-sorted-array/),
which first locates structure like this and then searches within it. It builds
directly on plain [Binary Search / 704](../0704-binary-search/). Whenever an array
is "sorted except for one rotation," think: which half is clean, and which half
hides the seam?
