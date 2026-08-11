# 704. Binary Search

**Pattern:** Binary search (one look at the middle throws away half)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/binary-search/

## The problem in plain words

You have a list of numbers already sorted in increasing order, with no duplicates.
Given a target, tell me the index where it lives, or `-1` if it isn't there.

```diagram
   index:   0    1    2    3    4    5
   nums:  [-1 ,  0 ,  3 ,  5 ,  9 , 12 ]     target = 9

   answer: index 4
```

## Why this matters

This is the purest form of a question that shows up everywhere: **given an ordered
collection, can I locate something — or rule out half of everything — with one
comparison?** The reusable move is halving the search space by asking a single
yes/no question whose answer eliminates half the candidates.

It's the backbone of real systems. Database indexes (B-trees) are binary search
generalized to disk, so a lookup touches a handful of pages instead of a whole
table. `git bisect` finds the commit that introduced a bug in about `log n` steps
instead of checking every commit. Autocomplete and dictionaries binary-search
sorted term lists. And "binary search on the answer" solves optimization problems —
the smallest capacity, speed, or threshold that satisfies a monotone condition —
across scheduling and capacity planning.

What you're buying is time: about `log n` steps instead of `n`. Twenty comparisons
find a target in a million sorted elements. When lookups happen millions of times a
second, or the data sits on slow disk where each read is expensive, that gap decides
whether the system keeps up.

## Start from the obvious

The definition hands you an algorithm: to find something in a list, walk the list
and check each element.

```
for i, x in enumerate(nums):
    if x == target: return i
return -1
```

That's about `n` steps, and it's correct. But notice what it *doesn't* use: the
array is **sorted**, and this scan treats it exactly like a shuffled pile. When your
algorithm ignores a fact you were given, that's usually where the speedup hides.

## Find the waste

Look for `9` in `[-1, 0, 3, 5, 9, 12]` and peek at the middle value, `5`. Because
the array is sorted, `5 < 9` tells you something big: **everything to the left of
`5` is also less than `9`.** The whole left half is disqualified in one comparison.
The linear scan throws that advantage away — it steps past `-1`, `0`, `3` one at a
time to learn what one look at the middle already told you.

```diagram
   nums:  [-1 ,  0 ,  3 ,  5 ,  9 , 12 ]     target = 9
                         ^mid
   5 < 9  ->  everything at or left of mid is too small, DROP it:

           [-1   0   3   5]  9  12
            \_____ gone _____/
```

## The insight

Keep a window `[lo, hi]` of the indices that could still hold the target. Look at
the middle. If it's the target, done. If the middle is too small, the target must
be to the right, so move `lo` past `mid`. If the middle is too big, move `hi` to
just below `mid`.

```diagram
   nums:  [-1 ,  0 ,  3 ,  5 ,  9 , 12 ]     target = 9

   step 1   lo=0 ............... hi=5   mid=2 -> nums[2]=3 < 9
            [-1   0   3   5   9  12]           go right, lo = 3
                     ^mid

   step 2               lo=3 ... hi=5   mid=4 -> nums[4]=9 == 9
                        [ 5   9  12]           FOUND at index 4
                             ^mid
```

Every step throws away half of what remains. `n` elements survive at most about
`log2(n)` halvings before the window is empty, so the search finishes in roughly
`log n` comparisons — around 20 steps for a million elements.

```
lo, hi = 0, len(nums) - 1
while lo <= hi:
    mid = lo + (hi - lo) // 2
    if nums[mid] == target: return mid
    elif nums[mid] < target: lo = mid + 1
    else:                    hi = mid - 1
```

## Complexity

- **Time: about log n steps.** Each iteration deletes half the range, so the number
  of steps is how many times you can halve `n` down to 1.
- **Extra memory: constant.** Just two index variables; nothing grows with `n`.

## Pitfalls

- **The loop condition.** With a *closed* window `[lo, hi]` (both ends included),
  use `while lo <= hi`. The window `[lo, lo]` (one element) is still a real
  candidate you must check; `lo < hi` would skip it.
- **Moving past mid.** Set `lo = mid + 1` / `hi = mid - 1`, not `lo = mid` /
  `hi = mid`. You already compared `mid` and it wasn't the target, so leaving it in
  the window can loop forever when `lo`, `hi`, and `mid` collapse together.
- **Overflow.** Use `mid = lo + (hi - lo) // 2` instead of `(lo + hi) // 2`. Python
  ints never overflow, but this is the safe form the pattern is known for.
- **Empty array.** `hi = -1` makes `lo <= hi` false immediately, so you correctly
  return `-1` without touching `nums`.

## Transfer

The core move — *one comparison against the middle discards half the space* — powers
every binary-search variant:
[Find Minimum in Rotated Sorted Array / 153](../0153-find-minimum-in-rotated-sorted-array/),
[Search in Rotated Sorted Array / 33](../0033-search-in-rotated-sorted-array/).
More broadly, whenever you can ask a yes/no question whose answer rules out half the
remaining possibilities — plain searching, or "binary search on the answer" for
optimization — reach for this template.
