# 215. Kth Largest Element in an Array

**Pattern:** Fixed-size min-heap / Quickselect (partial selection)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/kth-largest-element-in-an-array/

## The problem in plain words

Given a list of numbers and a number `k`, return the kth largest value once the
list is put in order. It's the kth largest by *position*, counting duplicates —
not the kth distinct number. So in `[2, 2, 2, 2]` the 3rd largest is `2`.

## Why this matters

The deeper operation is *selection*: find the value that would sit at one specific
rank if the data were sorted, without paying to sort everything. A full sort
answers "what is the exact order of all n?" when the question is only "what single
value lands at position k?"

This shows up wherever you need a percentile, a threshold, or a top-k cutoff.
Computing a p95 latency is "find the value at rank 0.95·n." A query like "show the
top 100 results" needs the 100th-best score to know where to cut. Median-of-medians
and Quickselect underpin fast statistics on large arrays; database engines pick
selection over sorting for `LIMIT`/percentile queries. Streaming leaderboards keep
the kth-best score as new entries arrive.

What the good solution buys is time and, for the heap, bounded memory. Sorting is
`O(n log n)`; a size-k heap is `O(n log k)` and holds only `k` items — ideal when
`k` is small or numbers stream in. Quickselect goes further, finding the answer in
`O(n)` on average by never ordering the parts of the array the answer doesn't lie
in.

## Start from the obvious

"kth largest in sorted order" is a definition you can run directly:

```
sort the numbers descending
return the element at index k-1
```

Correct, one line, `O(n log n)`. It's the right first thing to write — and looking
at *what it computes but never uses* points at both faster paths.

## Find the waste

Sorting arranges all `n` numbers relative to each other. But the answer is a single
value at one rank. Every comparison spent ordering the other `n-1` numbers *among
themselves* is invisible to the result. Two different ways to stop doing that work:

### Path A — keep only the top k (heap)

The kth largest is the **smallest of the top k** numbers. So you never need more
than k numbers in hand, and specifically their minimum.

> Keep the k largest numbers; the answer is the smallest of them.

### Path B — never order what the answer isn't in (Quickselect)

If you can cheaply split the array around a pivot into "smaller" and "larger"
groups, you learn which group the target rank falls in — and can throw the other
group away *unsorted*.

> Partition toward the target rank; recurse into one side only.

## The insight

**Heap (Path A).** Hold the k largest in a **min-heap** (smallest on top). Push
each number; whenever the heap exceeds k, pop its minimum — that number just fell
out of the top k. After one pass, `heap[0]` is the smallest of the k largest, i.e.
the kth largest.

```
for x in nums:
    push x
    if size > k: pop the smallest
return heap[0]
```

`O(n log k)` time, `O(k)` space. Reach for this when `k` is small or the numbers
arrive as a stream you can't fully store.

**Quickselect (Path B).** The kth largest sits at index `n-k` in ascending order.
Pick a random pivot, partition into `< pivot`, `== pivot`, `> pivot`, and see which
bucket the target index lands in. Recurse into just that bucket:

```
select(arr, idx):
    pivot = random element
    split into less / equal / greater
    if idx < len(less):            recurse into less
    elif idx < len(less)+len(equal): return pivot
    else:                         recurse into greater (shift idx)
```

Each step drops one side, so the expected work is `n + n/2 + n/4 + … = O(n)`. A
random pivot makes the `O(n^2)` worst case (always splitting off one element)
astronomically unlikely.

## Complexity

- **Sort:** `O(n log n)` time, `O(1)`–`O(n)` space depending on the sort.
- **Heap:** `O(n log k)` time, `O(k)` space. Best when `k ≪ n` or streaming.
- **Quickselect:** `O(n)` average, `O(n^2)` worst, `O(1)` extra space if
  partitioned in place. Best when you need the answer once and can mutate the
  array.

## Pitfalls

- **Kth largest, not kth distinct.** Don't dedupe; duplicates each hold a rank.
- **Wrong heap direction.** For the k *largest* you want a **min**-heap of size k
  (evict the smallest). A max-heap of size k would keep the smallest numbers.
- **Index conversion for Quickselect.** kth largest = index `n-k` ascending (or
  `k-1` descending). Mixing the two off-by-one conventions is the classic bug.
- **Quickselect's worst case.** A fixed pivot (e.g. always the first element) is
  `O(n^2)` on sorted or adversarial input; **randomize the pivot** (or use
  median-of-medians) to keep it linear in practice.
- **Recursion vs. index bookkeeping.** When recursing into `greater`, subtract
  `len(less) + len(equal)` from the target index, or you'll select the wrong slot.

## Transfer

The move is: **to find one value at a known rank, don't sort — either keep a size-k
heap of the contenders, or partition toward the rank and discard the rest
unsorted.** The heap side is the same structure as
[Kth Largest Element in a Stream / 703](../0703-kth-largest-element-in-a-stream/)
and [K Closest Points to Origin / 973](../0973-k-closest-points-to-origin/); the
partition side is Quickselect, cousin to Quicksort and to
[Top K Frequent Elements / 347](https://leetcode.com/problems/top-k-frequent-elements/).
Whenever a brute force sorts everything to read one rank or a small slice, reach
for a heap or Quickselect.
