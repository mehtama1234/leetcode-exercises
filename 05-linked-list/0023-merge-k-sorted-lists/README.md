# 23. Merge k Sorted Lists

**Pattern:** Merge in balanced pairs (divide and conquer) / min-heap
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/merge-k-sorted-lists/

## The problem in plain words

You're given `k` linked lists, each already sorted. Merge all of them into one
sorted list and return its head. It's
[problem 21](../0021-merge-two-sorted-lists/) scaled from two lists to many.

```diagram
   list 0:  1 -> 4 -> 5
   list 1:  1 -> 3 -> 4
   list 2:  2 -> 6

   merged:  1 -> 1 -> 2 -> 3 -> 4 -> 4 -> 5 -> 6
```

## Why this matters

The core question is: across many sorted streams, keep emitting the smallest front
element. The operation that makes this fast is "find the minimum among the k current
heads" without scanning all k every time.

This k-way merge sits at the heart of real systems. LSM-tree storage engines —
RocksDB, Cassandra, LevelDB — merge dozens of sorted on-disk files this way during
compaction. Log aggregators fold many per-server logs into one time-ordered stream;
MapReduce-style shuffle-and-merge and streaming joins over several ordered inputs do
the same; search engines merge many sorted lists of matching documents. Same shape
everywhere.

What you are solving for is not paying to scan all k heads every step, and not
concatenating everything and re-sorting. Done well, the whole merge stays close to
`N log k` (N total nodes) in one streaming pass, holding only k pointers — the
difference between feasible and not when k and N are large.

## Start from the obvious

You already know how to merge *two* sorted lists. So fold: merge list 0 with list
1, merge that with list 2, and so on.

```diagram
   acc = list0
   acc = merge(acc, list1)     acc now holds 2 lists' nodes
   acc = merge(acc, list2)     acc now holds 3 lists' nodes
   acc = merge(acc, list3)     acc now holds 4 lists' nodes
        ^ each merge re-walks the whole growing accumulator
```

Correct, but watch the accumulator. After folding in `i` lists it holds `i` lists'
worth of nodes, and the next merge walks *all* of them again. With `N` total nodes
the early ones get re-walked on every later merge, so the work piles up to about
`k · N`. The waste is re-scanning the same growing pile over and over.

## Find the waste

The imbalance is the problem: one giant list keeps getting merged against one tiny
list. Fix it by keeping the merges *balanced*. Merge the lists in pairs, so each
round halves how many lists are left.

```diagram
   round 1:  [L0  L1] [L2  L3] [L4  L5] [L6  L7]
                \  /     \  /     \  /     \  /
   round 2:    [ A       B ]     [ C       D ]
                    \    /            \    /
   round 3:        [   E   ]         [   F   ]
                        \                /
   final:              [   merged      ]

   8 lists -> 4 -> 2 -> 1     that's log(k) rounds
```

Each round touches every node once (about `N` work per round), and there are about
`log k` rounds, so the total is about `N log k`.

```diagram
   pairwise loop:
     while more than one list:
       new = []
       for each pair (a, b) in lists:      # b = None if odd one out
         new.append( merge_two(a, b) )
       lists = new
     return lists[0]
```

This is the "combine" phase of merge sort, lifted one level up: instead of merging
sorted halves of an array, you merge sorted lists.

**Alternative — a min-heap (a structure that always hands you the smallest item
fast).** Put the head of every list into the heap keyed by value. Pop the smallest,
append it to the result, then push that node's `next`.

```diagram
   heap holds one head per list (at most k items):

   heap: {1(l0), 1(l1), 2(l2)}   pop 1(l0) -> result: 1     push 4(l0)
   heap: {1(l1), 2(l2), 4(l0)}   pop 1(l1) -> result: 1 1   push 3(l1)
   heap: {2(l2), 3(l1), 4(l0)}   pop 2(l2) -> result: 1 1 2 push 6(l2)
   ... continue until the heap empties
```

The heap holds at most `k` nodes, so each of the `N` pops and pushes costs about
`log k` — same `N log k` total. (Python's `heapq` needs a tiebreaker like a counter,
since raw `ListNode`s can't be compared when values tie.)

## Complexity

- **Time: about N log k.** `log k` merge rounds (or `N` heap operations), each about
  `N` work per round (or `log k` per heap step). Beats the naive `k · N`.
- **Extra memory:** fixed for pairwise merge (nodes are relinked, not copied); about
  `k` for the heap variant, plus `log k` stack frames if written recursively.

## Pitfalls

- Empty inputs: an empty `lists` array, or lists that are individually empty. The
  pairwise loop and the `merge_two` dummy handle both, but test them.
- Odd count: when the number of lists is odd, the last one has no partner. Pair it
  with `None` (merging a list with nothing returns the list unchanged).
- Heap version: don't push raw nodes — Python can't compare them when values tie.
  Push `(node.val, unique_counter, node)`.

## Transfer

The pairwise-merge idea is the top of merge sort — the same tournament shape you use
in Sort List / 148 and any k-way merge (external sorting). Each pair uses
[merge two lists / 21](../0021-merge-two-sorted-lists/) directly. The heap variant
is the general "merge k sorted streams" tool, showing up in Smallest Range Covering
Elements from K Lists / 632 and Kth Smallest Element in a Sorted Matrix / 378.
