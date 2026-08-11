# 215. Kth Largest Element in an Array

**Pattern:** Fixed-size min-heap / Quickselect (find one rank, don't sort all)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/kth-largest-element-in-an-array/

## The problem in plain words

Given a list of numbers and a number `k`, return the kth largest value once the
list is in order. It's the kth largest by *position*, counting duplicates — not
the kth distinct number. So in `[2, 2, 2, 2]` the 3rd largest is `2`.

```diagram
   nums = [3, 2, 1, 5, 6, 4],  k = 2

   sorted descending:  6  5  4  3  2  1
                          ^
                       rank 2 -> answer 5
```

## Why this matters

The real operation is *selection*: find the value that would sit at one specific
rank if the data were sorted, without paying to sort everything. A full sort
answers "what is the exact order of all n?" when the question is only "what single
value lands at position k?"

This shows up wherever you need a percentile, a threshold, or a top-k cutoff.
Computing a p95 latency is "find the value at rank 0.95·n." A query like "show the
top 100 results" needs the 100th-best score to know where to cut. Quickselect
underpins fast statistics on large arrays; database engines pick selection over
sorting for `LIMIT` and percentile queries.

What the good solutions buy is time and, for the heap, bounded memory. Sorting is
about `n log n`; a size-k heap is about `n log k` and holds only `k` items — ideal
when `k` is small or numbers stream in. Quickselect goes further, finding the
answer in about `n` steps on average by never ordering the parts the answer
doesn't lie in.

## Start from the obvious

"kth largest in sorted order" is a definition you can run directly:

```
sort the numbers descending
return the element at index k-1
```

Correct, one line, about `n log n`. It's the right first thing to write — and
looking at *what it computes but never uses* points at both faster paths.

## Find the waste

Sorting arranges all `n` numbers relative to each other. But the answer is a
single value at one rank. Every comparison spent ordering the other `n-1` numbers
*among themselves* is invisible to the result.

```diagram
   sorted descending, k = 2:

   6  5  4  3  2  1
      ^  the only cell we read
   [  ]  [ 4 3 2 1 ]   <- ordered relative to each other for nothing
```

Two different ways to stop doing that work:

### Path A — keep only the top k (heap)

The kth largest is the **smallest of the top k** numbers. So you never need more
than k numbers in hand, and specifically their minimum.

### Path B — never order what the answer isn't in (Quickselect)

If you cheaply split the array around a pivot into "smaller" and "larger" groups,
you learn which group the target rank falls in — and can throw the other group
away *unsorted*.

## The insight

**Heap (Path A).** Hold the k largest in a **min-heap** (a tree with the smallest
value on top). Push each number; whenever the heap exceeds k, pop its minimum —
that number just fell out of the top k. After one pass, the top is the smallest of
the k largest, i.e. the kth largest.

```diagram
   k = 2, nums = [3, 2, 1, 5, 6, 4], min-heap holds top 2:

   push 3  -> {3}
   push 2  -> {2,3}
   push 1  -> {1,2,3} size 3>2 -> pop 1 -> {2,3}
   push 5  -> {2,3,5} pop 2 -> {3,5}
   push 6  -> {3,5,6} pop 3 -> {5,6}
   push 4  -> {4,5,6} pop 4 -> {5,6}
   top = 5  -> the 2nd largest
```

About `n log k` time, `k` space. Reach for this when `k` is small or the numbers
arrive as a stream you can't fully store.

**Quickselect (Path B).** The kth largest sits at index `n-k` in ascending order.
Pick a random pivot, split into `< pivot`, `== pivot`, `> pivot`, and see which
bucket the target index lands in. Recurse into just that bucket.

```diagram
   nums = [3, 2, 1, 5, 6, 4], k = 2 -> target index n-k = 4 (ascending)

   pivot = 3:  less=[2,1]  equal=[3]  greater=[5,6,4]
               sizes:  2      1          3
   index 4 falls past less(2)+equal(1)=3 -> it's in greater
   recurse into greater with index 4-3 = 1

   greater=[5,6,4], pivot=5: less=[4] equal=[5] greater=[6]
                index 1 = past less(1) -> equals pivot -> answer 5
```

Each step drops one side, so the expected work is `n + n/2 + n/4 + ... = about n`.
A random pivot makes the `n·n` worst case (always splitting off one element)
extremely unlikely.

## Complexity

- **Sort:** about `n log n` time.
- **Heap:** about `n log k` time, `k` space. Best when `k` is much smaller than
  `n`, or streaming.
- **Quickselect:** about `n` average, `n·n` worst, constant extra space if
  partitioned in place. Best when you need the answer once and can mutate the
  array.

## Pitfalls

- **Kth largest, not kth distinct.** Don't dedupe; duplicates each hold a rank.
- **Wrong heap direction.** For the k *largest* you want a **min**-heap of size k
  (evict the smallest). A max-heap of size k would keep the smallest numbers.
- **Index conversion for Quickselect.** kth largest = index `n-k` ascending (or
  `k-1` descending). Mixing the two conventions is the classic bug.
- **Quickselect's worst case.** A fixed pivot (e.g. always the first element) is
  `n·n` on sorted or adversarial input; **randomize the pivot** to keep it linear
  in practice.
- **Recursion bookkeeping.** When recursing into `greater`, subtract
  `len(less) + len(equal)` from the target index, or you'll select the wrong slot.

## Transfer

The move is: **to find one value at a known rank, don't sort — either keep a
size-k heap of the contenders, or partition toward the rank and discard the rest
unsorted.** The heap side is the same structure as
[Kth Largest Element in a Stream / 703](../0703-kth-largest-element-in-a-stream/)
and [K Closest Points to Origin / 973](../0973-k-closest-points-to-origin/); the
partition side is Quickselect, cousin to Quicksort. Whenever a brute force sorts
everything to read one rank or a small slice, reach for a heap or Quickselect.
