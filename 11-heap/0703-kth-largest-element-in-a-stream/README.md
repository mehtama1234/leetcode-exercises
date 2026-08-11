# 703. Kth Largest Element in a Stream

**Pattern:** Fixed-size min-heap (keep only the k biggest)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/kth-largest-element-in-a-stream/

## The problem in plain words

You're told a number `k` up front and given a starting list of numbers. Then
numbers keep arriving one at a time. Every time one arrives, you must answer:
"among *everything* seen so far, what is the kth largest value?"

Note it's the kth *largest*, not the kth *distinct* — duplicates each take a
position. So with `k = 2` and numbers `5, 5`, the 2nd largest is `5`.

## Why this matters

The deeper operation is maintaining a *top-k* set over a stream you can't rewind:
you don't care about the whole ranking, only about a value at one fixed position
near the top, kept current as data flows past. The trick is to remember exactly
the k items that could matter and forget the rest the instant they can't.

This is how real "leaderboard" and threshold systems work. A monitoring service
that alerts on your kth-worst latency, a game keeping the top-k high scores as
matches finish, a search or ads pipeline holding the k best candidates while
scoring a stream of documents, a "top 10 trending" panel updated as events pour
in — all keep a small bounded structure instead of re-ranking the full history.

What the good solution buys is bounded memory and a fixed per-update cost. You
store `k` items, not `n`, and each new number costs `O(log k)` no matter how long
the stream runs — the difference between a service that stays flat under load and
one whose per-event work grows with everything it has ever seen.

## Start from the obvious

The question mentions "kth largest", which is defined by sorted order, so the
honest first move is to keep every number and sort when asked:

```
add(x):
    history.append(x)
    return sorted(history, descending)[k - 1]
```

This is correct. But `add` re-sorts the entire history every single time —
`O(n log n)` per call — even though the answer only ever depends on the few
biggest numbers.

## Find the waste

To name the kth largest, you need the top k numbers, and specifically the
*smallest* of those k (everything above it is larger, so it sits at position k).
Numbers ranked below the top k can never be the answer, and they can never climb
back into the top k either — new arrivals only push the boundary *up*. So keeping
them, and re-sorting them, is pure waste.

That narrows the requirement:

> Keep only the k largest numbers, and keep their smallest instantly reachable.

## The insight

Hold the k largest values in a **min-heap** of fixed size `k`. A min-heap keeps
its *smallest* element on top — and the smallest of the top k is precisely the
kth largest overall. So the answer is always `heap[0]`, read in O(1).

On each add:

```
add(x):
    push x onto the heap
    if heap has more than k items:
        pop the smallest        # it fell out of the top k, discard it
    return heap[0]              # smallest of the top k = kth largest
```

The heap never grows past `k`. Pushing and popping are `O(log k)`, and the
membership rule is automatic: if a new number is big, it stays and bumps out the
old minimum; if it's small, it becomes the new minimum and gets popped right back
out. Either way the heap holds exactly the current top k afterward.

## Complexity

- **`add`:** `O(log k)` — one push and at most one pop on a heap of size ≤ k.
- **Constructor:** `O(n)` to `heapify` the initial list, then trimming excess
  with pops is `O((n − k) log n)` in the worst case.
- **Space:** `O(k)` — the heap never holds more than k numbers.

Against the sorted-list version's `O(n log n)` per add and `O(n)` memory, we
traded "keep all of it ordered" for "keep only the k that matter".

## Pitfalls

- **Wrong heap direction.** You want a **min**-heap (smallest of the top k on
  top), not a max-heap. A max-heap would surface the *largest* number, which is
  the 1st largest, not the kth.
- **Forgetting to cap the size.** If you never pop, the heap becomes the whole
  stream and `heap[0]` is the global minimum, not the kth largest.
- **The initial list can be shorter than k.** The heap simply holds fewer than k
  items until enough numbers arrive; `heap[0]` still works, and LeetCode
  guarantees a valid kth largest exists whenever `add` is called.
- **Kth largest ≠ kth distinct.** Don't dedupe; duplicates each occupy a slot.

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
