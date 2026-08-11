# 33. Search in Rotated Sorted Array

**Pattern:** Binary search over a rotated (piecewise-sorted) array
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/search-in-rotated-sorted-array/

## The problem in plain words

Take a sorted array of distinct numbers and rotate it at some unknown point:
`[0, 1, 2, 4, 5, 6, 7]` becomes something like `[4, 5, 6, 7, 0, 1, 2]`. Given a
target, return the index where it sits, or `-1` if it's not there. It must run in
`O(log n)`, so scanning is not allowed.

## Start from the obvious

Look at every element until you find the target.

```
for i, x in enumerate(nums):
    if x == target: return i
return -1
```

Correct, but `O(n)`. The array *looks* scrambled, so a scan feels unavoidable —
yet it isn't scrambled at all. It's two sorted runs stuck together, and that's
enough structure for binary search if we're careful.

## Find the waste

Plain binary search needs the whole array sorted so that "target vs middle" tells
you which side to keep. Here the array isn't fully sorted, so that single
comparison is ambiguous. The linear scan gives up on binary search entirely — but
we only need one extra observation to rescue it.

## The insight

Pick the middle and split into a left part `[lo, mid]` and a right part
`[mid, hi]`. The rotation seam (the one spot where order breaks) can live in only
**one** of those parts — so the **other part is fully sorted**. And a sorted part
is something we *can* reason about: we know its exact min and max, so we can tell
in one comparison whether the target lies inside it.

So each step:

1. If `nums[mid] == target`, done.
2. Figure out which half is the clean, sorted one (compare its endpoints).
3. Ask: does the target fall within that sorted half's known range?
   - **Yes** -> search that half.
   - **No** -> the target, if it exists, must be in the other half -> search there.

```
lo, hi = 0, len(nums) - 1
while lo <= hi:
    mid = lo + (hi - lo) // 2
    if nums[mid] == target: return mid
    if nums[lo] <= nums[mid]:                 # left half is sorted
        if nums[lo] <= target < nums[mid]: hi = mid - 1
        else:                              lo = mid + 1
    else:                                     # right half is sorted
        if nums[mid] < target <= nums[hi]: lo = mid + 1
        else:                              hi = mid - 1
return -1
```

Every iteration still throws away half the array, so we keep `O(log n)`.

## Complexity

- **Time:** `O(log n)` — one binary-search pass; each step halves the window.
- **Space:** `O(1)` — just index variables.

## Pitfalls

- **Deciding which half is sorted.** Use `nums[lo] <= nums[mid]` (with `<=`, not
  `<`) so tiny windows where `lo == mid` are treated as a sorted left half. Get
  this boundary wrong and you take the wrong branch near the edges.
- **Inclusive vs exclusive range checks.** Left-sorted uses
  `nums[lo] <= target < nums[mid]`; right-sorted uses
  `nums[mid] < target <= nums[hi]`. `mid` is already handled by the equality check
  at the top, so it's excluded on the open side of each range — mixing these up
  sends the search into the wrong half.
- **Two-pass temptation.** You *can* first find the pivot (like
  [153](../0153-find-minimum-in-rotated-sorted-array/)) and then binary-search a
  half. That works and is easier to reason about, but this single pass does it in
  one sweep — just keep the case analysis disciplined.
- Assumes **distinct** values; duplicates (LeetCode 81) can make
  `nums[lo] == nums[mid]` ambiguous and degrade the worst case.

## Transfer

This is [153](../0153-find-minimum-in-rotated-sorted-array/)'s "which half holds
the seam?" idea pushed one step further, built on plain
[Binary Search / 704](../0704-binary-search/). The reusable move: **when an array
is sorted-except-for-one-break, split so one side is guaranteed clean, and use
that clean side to decide where to go.** The same "one half is always well-behaved"
trick shows up across rotated-array and mountain-array searches.
