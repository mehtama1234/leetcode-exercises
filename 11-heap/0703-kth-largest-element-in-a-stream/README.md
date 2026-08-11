# 703. Kth Largest Element in a Stream

**Pattern:** Fixed-size min-heap (keep only the k biggest, forget the rest)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/kth-largest-element-in-a-stream/

## The problem in plain words

You're told a number `k` up front and given a starting list of numbers. Then
numbers keep arriving one at a time. Each time one arrives, answer: "among
*everything* seen so far, what is the kth largest value?"

It's the kth *largest*, not the kth *distinct* — duplicates each take a spot. So
with `k = 2` and numbers `5, 5`, the 2nd largest is `5`.

## Why this matters

The real job is keeping a *top-k* set current over a stream you can't rewind. You
don't care about the full ranking, only about the value at one fixed spot near
the top. The move that makes it work: remember exactly the k items that could
still matter, and forget every other number the instant it can't.

This is how leaderboards and threshold alarms work. A monitor that alerts on your
kth-worst latency, a game keeping the top-k high scores as matches finish, a
search pipeline holding the k best candidates while scoring a stream of documents
— all keep a small bounded structure instead of re-ranking the full history.

What you buy is bounded memory and a fixed per-update cost. You store `k` items,
not `n`, and each new number costs about `log k` steps no matter how long the
stream runs — the difference between a service that stays flat under load and one
whose per-event work grows with everything it has ever seen.

## Start from the obvious

"kth largest" is defined by sorted order, so the honest first move is to keep
every number and sort when asked:

```
add(x):
    history.append(x)
    return sorted(history, descending)[k - 1]
```

Correct. But `add` re-sorts the entire history every single call — about
`n log n` work — even though the answer only ever depends on the few biggest
numbers.

## Find the waste

To name the kth largest you need the top k numbers, and specifically the
*smallest* of those k — everything above it is larger, so it sits at rank k.
Numbers ranked below the top k can never be the answer, and they can never climb
back in either: new arrivals only push the boundary *up*. So keeping them, and
re-sorting them, is pure waste.

```diagram
   k = 3, seen so far: 8 5 4 2 1        (sorted view)

   [ 8  5  4 ] 2  1
     top 3      |__ can never be the 3rd largest again
     ^^^^^^^^
     answer is the SMALLEST of these = 4
```

That narrows the requirement:

> Keep only the k largest numbers, and keep their smallest instantly reachable.

## The insight

Hold the k largest values in a **min-heap** (a tree where every parent is smaller
than its children, so the smallest sits on top) of fixed size `k`. The smallest
of the top k is precisely the kth largest overall, so the answer is always the
heap's top, read in one step.

On each add: push the new number; if the heap now holds more than k, pop its
smallest — that one just fell out of the top k.

```diagram
   k = 3, start [4,5,8,2] -> keep top 3 -> heap holds {4,5,8}, top = 4

   min-heap (smallest on top):
            4
           / \
          5   8

   add(3): push 3 -> {3,4,5,8}, size 4 > 3 -> pop smallest (3)
           back to {4,5,8}, top = 4        -> answer 4

   add(10): push 10 -> {4,5,8,10}, pop smallest (4)
            {5,8,10}, top = 5              -> answer 5

   add(9): push 9 -> {5,8,9,10}, pop smallest (5)
           {8,9,10}, top = 8              -> answer 8
```

The heap never grows past `k`. If a new number is big, it stays and bumps out the
old minimum; if it's small, it becomes the new minimum and is popped right back.
Either way the heap holds exactly the current top k afterward.

## Complexity

- **`add`:** about `log k` — one push and at most one pop on a heap of size at
  most k.
- **Constructor:** about `n` to build the heap from the initial list, then
  trimming the excess with pops.
- **Space:** `k` — the heap never holds more than k numbers.

Against the sorted-list version's `n log n` per add and `n` memory, we traded
"keep all of it ordered" for "keep only the k that matter".

## Pitfalls

- **Wrong heap direction.** You want a **min**-heap (smallest of the top k on
  top), not a max-heap. A max-heap surfaces the *largest* number, which is the
  1st largest, not the kth.
- **Forgetting to cap the size.** If you never pop, the heap becomes the whole
  stream and its top is the global minimum, not the kth largest.
- **The initial list can be shorter than k.** The heap simply holds fewer than k
  items until enough numbers arrive; the top still works, and the problem
  guarantees a valid kth largest exists whenever `add` is called.
- **Kth largest is not kth distinct.** Don't dedupe; duplicates each occupy a
  slot.

## Transfer

The move is: **when you only need a fixed number of the biggest (or smallest)
items from a stream, keep a bounded heap of exactly that many and pop the loser on
each insert.** The same size-k heap solves
[K Closest Points to Origin / 973](../0973-k-closest-points-to-origin/) and
[Kth Largest Element in an Array / 215](../0215-kth-largest-element-in-an-array/),
and the balanced two-heap cousin powers
[Find Median from Data Stream / 295](../0295-find-median-from-data-stream/).
Whenever a brute force keeps re-sorting to read "the top k", reach for a capped
heap first.
