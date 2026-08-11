# 23. Merge k Sorted Lists

**Pattern:** Divide and conquer (pairwise merge) / min-heap
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/merge-k-sorted-lists/

## The problem in plain words

You're given `k` linked lists, each already sorted. Merge all of them into one
sorted list and return its head. It's [problem 21](../0021-merge-two-sorted-lists/)
scaled from two lists to many.

## Start from the obvious

You already know how to merge *two* sorted lists. So just fold: merge list 0 with
list 1, merge that result with list 2, and so on.

```
result = None
for lst in lists:
    result = merge_two(result, lst)
return result
```

Correct — but look at what `result` does. After merging in `i` lists, the
accumulator already holds `i` lists' worth of nodes, and the next merge walks
*all* of them again. Let `N` be the total number of nodes across all lists. The
early nodes get re-walked on every subsequent merge, so the total work is about
`N + 2N/k + 3N/k + ... ≈ O(k·N)`. The waste is re-scanning the same growing
accumulator over and over.

## Find the waste / the insight

The imbalance is the problem: one huge list keeps getting merged against one tiny
list. Fix it by keeping the merges *balanced*. Merge the lists in **pairs**, so
each round halves how many lists remain:

```
k lists -> k/2 lists -> k/4 -> ... -> 1
```

Each round touches every node once (that's `O(N)` per round), and there are
`log k` rounds, so the total is `O(N log k)`.

```
while len(lists) > 1:
    merged = []
    for i in range(0, len(lists), 2):
        a = lists[i]
        b = lists[i+1] if i+1 < len(lists) else None
        merged.append(merge_two(a, b))
    lists = merged
return lists[0]
```

This is exactly the "combine" phase of merge sort, lifted one level up: instead
of merging sorted halves of an array, we merge sorted lists.

**Alternative — a min-heap.** Put the head of every list into a min-heap keyed by
value. Pop the smallest, append it to the result, and push that node's `next`.
The heap always holds at most `k` nodes, so each of the `N` pops/pushes costs
`O(log k)` — same `O(N log k)` total, `O(k)` extra space. (Python's `heapq`
needs a tiebreaker like a counter since raw `ListNode`s aren't comparable.)

## Complexity

- **Time:** `O(N log k)` — `log k` merge rounds (or `N` heap operations), each
  `O(N)` / `O(log k)`. Beats the naive `O(k·N)`.
- **Space:** `O(1)` extra for pairwise merge (nodes are re-linked, not copied);
  `O(k)` for the heap variant, plus `O(log k)` recursion if written recursively.

## Pitfalls

- Empty inputs: an empty `lists` array, or lists that are individually empty —
  the pairwise loop and the `merge_two` dummy handle both, but test them.
- Odd count: when `len(lists)` is odd, the last list has no partner. Pair it with
  `None` (merging a list with nothing returns the list unchanged).
- Heap version: don't push raw nodes — Python can't compare them when values tie.
  Push `(node.val, unique_counter, node)`.

## Transfer

The pairwise-merge idea is the top of merge sort — it's the same tournament shape
you use in Sort List / 148 and any k-way merge (external sorting). The heap
variant is the general "merge k sorted streams" tool, e.g. Smallest Range
Covering Elements from K Lists / 632 and Kth Smallest Element in a Sorted Matrix
/ 378.
