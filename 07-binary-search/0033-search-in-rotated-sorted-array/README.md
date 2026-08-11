# 33. Search in Rotated Sorted Array

**Pattern:** Binary search over a rotated array (one half is always clean)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/search-in-rotated-sorted-array/

## The problem in plain words

Take a sorted array of distinct numbers and rotate it at some unknown point:
`[0, 1, 2, 4, 5, 6, 7]` becomes something like `[4, 5, 6, 7, 0, 1, 2]`. Given a
target, return the index where it sits, or `-1` if it's not there. It must run in
about `log n` steps, so scanning is not allowed.

```diagram
   sorted:    [ 0  1  2  4  5  6  7 ]
   rotated:   [ 4  5  6  7 | 0  1  2 ]     target = 0
                          break here
                              ^ answer: index 4
```

## Why this matters

Underneath the rotation, this is a search over data that is *mostly* ordered but
has one seam where the order wraps. The reusable move is deciding, from a single
probe, which side of the seam your answer is on without looking at the rest.

That situation is common. Ring buffers and circular queues store data that wraps at
an arbitrary offset; log files and time-series that roll over at midnight or a
sequence-number reset are sorted-then-wrapped in exactly this way. Systems that
bisect commit histories or index pages may be searching data that was rotated or
partitioned. Anything using a consistent-hashing ring locates a key by searching a
sorted ring of hash values.

What you're buying is time and a latency budget: about `log n` steps instead of `n`.
For a million entries that's roughly 20 comparisons versus a million — the
difference between an instant answer and a stall. The trick is that you don't
un-rotate or re-sort the data first; you use the structure that's already there.

## Start from the obvious

Look at every element until you find the target.

```
for i, x in enumerate(nums):
    if x == target: return i
return -1
```

Correct, but about `n` steps. The array *looks* scrambled, so a scan feels
unavoidable — yet it isn't scrambled at all. It's two sorted runs stuck together,
and that's enough structure for binary search if you're careful.

## Find the waste

Plain binary search needs the whole array sorted so that "target vs middle" tells
you which side to keep. Here the array isn't fully sorted, so that single comparison
is ambiguous. The linear scan gives up on binary search entirely — but you only need
one extra observation to rescue it.

```diagram
   [ 4  5  6  7  0  1  2 ]
              ^mid = 7

   split at mid into  [4 5 6 7]  and  [7 0 1 2]
   the break lives in only ONE of them
   -> the OTHER half is a clean sorted run you can reason about
```

## The insight

Pick the middle and split into a left part `[lo..mid]` and a right part
`[mid..hi]`. The rotation seam can live in only **one** of those parts — so the
**other part is fully sorted**. And a sorted part is something you *can* reason
about: you know its exact smallest and largest, so one comparison tells you whether
the target lies inside it.

So each step: if the middle is the target, done. Otherwise figure out which half is
the clean sorted one (compare its endpoints), then ask whether the target falls
inside that half's known range. If yes, search there; if no, the target must be in
the other half.

```diagram
   nums:  [ 4  5  6  7  0  1  2 ]     target = 0

   step 1  lo=0 ............... hi=6   mid=3 nums[3]=7
           nums[lo]=4 <= nums[mid]=7  -> LEFT half [4..7] is sorted
           is 0 in [4,7)?  no  -> go RIGHT, lo = mid+1 = 4
           [ 4  5  6  7  0  1  2 ]
                    ^mid

   step 2              lo=4 .... hi=6   mid=5 nums[5]=1
           nums[lo]=0 <= nums[mid]=1  -> LEFT half [0..1] is sorted
           is 0 in [0,1)?  yes -> go LEFT, hi = mid-1 = 4
           [ 0  1  2 ]
                ^mid

   step 3              lo=4  hi=4       mid=4 nums[4]=0
           nums[mid]=0 == target  ->  FOUND at index 4
```

Every step still throws away half the array, so you keep about `log n` steps.

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

## Complexity

- **Time: about log n steps.** One binary-search pass; each step halves the window.
- **Extra memory: constant.** Just index variables.

## Pitfalls

- **Deciding which half is sorted.** Use `nums[lo] <= nums[mid]` (with `<=`, not
  `<`) so tiny windows where `lo == mid` count as a sorted left half. Get this
  boundary wrong and you take the wrong branch near the edges.
- **Inclusive vs exclusive range checks.** Left-sorted uses
  `nums[lo] <= target < nums[mid]`; right-sorted uses
  `nums[mid] < target <= nums[hi]`. `mid` is already handled by the equality check
  at the top, so it's excluded on the open side of each range — mixing these up sends
  the search into the wrong half.
- **Two-pass temptation.** You *can* first find the break (like
  [153](../0153-find-minimum-in-rotated-sorted-array/)) and then binary-search one
  half. That works and is easier to reason about, but this single pass does it in one
  sweep — just keep the case analysis disciplined.
- Assumes **distinct** values; duplicates (LeetCode 81) can make
  `nums[lo] == nums[mid]` ambiguous and degrade the worst case.

## Transfer

This is [153](../0153-find-minimum-in-rotated-sorted-array/)'s "which half holds the
seam?" idea pushed one step further, built on plain
[Binary Search / 704](../0704-binary-search/). The reusable move: **when an array is
sorted-except-for-one-break, split so one side is guaranteed clean, and use that
clean side to decide where to go.** The same "one half is always well-behaved" trick
shows up across rotated-array and mountain-array searches.
