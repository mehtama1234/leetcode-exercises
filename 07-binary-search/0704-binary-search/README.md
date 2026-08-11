# 704. Binary Search

**Pattern:** Binary search (halve the search space each step)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/binary-search/

## The problem in plain words

You have a list of numbers that is already sorted in increasing order, with no
duplicates. Given a target, tell me the index where it lives, or `-1` if it isn't
there.

## Start from the obvious

The definition hands you an algorithm: to find something in a list, walk the list
and check each element.

```
for i, x in enumerate(nums):
    if x == target: return i
return -1
```

That's `O(n)`, and it's correct. But notice what it *doesn't* use: the array is
**sorted**, and this scan treats it exactly like a shuffled pile. When your
algorithm ignores a fact you were given, that's usually where the speedup hides.

## Find the waste

Suppose you're looking for `9` in `[-1, 0, 3, 5, 9, 12]` and you peek at the
middle value, `5`. Because the array is sorted, `5 < 9` tells you something huge:
**everything to the left of `5` is also less than `9`**. The entire left half is
disqualified in a single comparison. The linear scan throws that leverage away —
it steps past `-1`, `0`, `3` one at a time to learn what one look at the middle
already told you.

## The insight

Keep a window `[lo, hi]` of the indices that could still contain the target.
Look at the middle:

1. If `nums[mid] == target`, you found it.
2. If `nums[mid] < target`, the target must be to the right — move `lo` to
   `mid + 1` and discard the whole left half (including `mid`).
3. If `nums[mid] > target`, the target must be to the left — move `hi` to
   `mid - 1`.

Every step throws away half of what remains. `n` elements survive at most
`log2(n)` halvings before the window is empty, so the search finishes in about
`log n` comparisons — 20-ish steps for a million elements.

```
lo, hi = 0, len(nums) - 1
while lo <= hi:
    mid = lo + (hi - lo) // 2
    if nums[mid] == target: return mid
    elif nums[mid] < target: lo = mid + 1
    else:                    hi = mid - 1
```

## Complexity

- **Time:** `O(log n)` — each iteration deletes half the remaining range, so the
  number of iterations is the number of times you can halve `n` down to 1.
- **Space:** `O(1)` — just two index variables; nothing grows with `n`.

## Pitfalls

- **The loop condition.** With a *closed* window `[lo, hi]`, use `while lo <= hi`.
  The window `[lo, lo]` (one element) is still a real candidate you must check;
  `lo < hi` would skip it.
- **Moving past mid.** Set `lo = mid + 1` / `hi = mid - 1`, not `lo = mid` /
  `hi = mid`. Since you already compared `mid` and it wasn't the target, leaving
  it in the window can loop forever when `lo`, `hi`, and `mid` collapse together.
- **Overflow.** `mid = lo + (hi - lo) // 2` instead of `(lo + hi) // 2`. Python
  ints never overflow, but this is the safe form the pattern is famous for.
- **Empty array.** `hi = -1` makes `lo <= hi` false immediately, so you correctly
  return `-1` without touching `nums`.

## Transfer

The core move — *one comparison against the middle discards half the space* —
powers every binary-search variant:
[Find Minimum in Rotated Sorted Array / 153](../0153-find-minimum-in-rotated-sorted-array/),
[Search in Rotated Sorted Array / 33](../0033-search-in-rotated-sorted-array/).
More broadly, whenever you can ask a yes/no question whose answer rules out half
the remaining possibilities (searching, or "binary search on the answer" for
optimization problems), reach for this template.
