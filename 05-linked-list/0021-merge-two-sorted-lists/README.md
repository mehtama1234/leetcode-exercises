# 21. Merge Two Sorted Lists

**Pattern:** Two-pointer merge + dummy head
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/merge-two-sorted-lists/

## The problem in plain words

You have two linked lists that are each already sorted ascending. Interleave them
into one sorted list and return its head. Reuse the existing nodes — don't build
a fresh list from copied values.

## Start from the obvious

The insight is baked into the word "sorted". The smallest unused value across
both lists is always at one of the two current heads — you never have to look
further. So repeatedly pick the smaller head, attach it, and advance that list:

```
while both lists have nodes:
    pick the smaller head, attach it to the result, advance that list
attach whatever list still has nodes
```

There's no faster idea here; the whole difficulty is doing the pointer bookwork
cleanly.

## The insight

Two small tricks turn the bookkeeping from fiddly to trivial:

1. **A dummy head.** Start the result with a throwaway node. Then "attach the
   next node" is always `tail.next = chosen; tail = tail.next` — you never have
   to special-case picking the very first node. Return `dummy.next` at the end.
2. **Splice the leftover in one move.** When one list empties, the other is
   already sorted and already linked, so `tail.next = whichever_remains`
   attaches all of it at once — no per-node loop.

```
dummy = ListNode()
tail = dummy
while l1 and l2:
    if l1.val <= l2.val: tail.next = l1; l1 = l1.next
    else:                tail.next = l2; l2 = l2.next
    tail = tail.next
tail.next = l1 if l1 else l2
return dummy.next
```

## Complexity

- **Time:** `O(n + m)` — each node from both lists is visited once.
- **Space:** `O(1)` — no new nodes; only pointers move. (The dummy is a single
  constant node.)

## Pitfalls

- Use `<=` not `<` when comparing heads. With `<`, equal values still merge
  correctly here, but `<=` keeps the merge **stable** — which matters when this
  is a subroutine inside a sort.
- Forgetting the leftover splice truncates the answer as soon as one list ends.
- Either input can be empty (or both). The dummy + final splice handle those
  with no extra branches.

## Transfer

This merge is the core subroutine of merge sort — it's exactly the "combine"
step in Sort List / 148, and it's what you call repeatedly (or pairwise) to
solve [merge k sorted lists / 23](../0023-merge-k-sorted-lists/). The dummy-head
pattern reappears in nearly every list-building problem, e.g.
[remove nth node / 19](../0019-remove-nth-node-from-end-of-list/) and Add Two
Numbers / 2.
