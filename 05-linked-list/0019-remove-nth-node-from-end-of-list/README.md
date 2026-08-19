# 19. Remove Nth Node From End of List

**Pattern:** Two pointers held a fixed gap apart, plus a dummy head
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/remove-nth-node-from-end-of-list/

## The problem in plain words

Delete the node that is `n`th from the *end* of the list (n=1 is the last node) and
return the head. A singly linked list only walks forward, so "from the end" is the
awkward part.

```diagram
   1 -> 2 -> 3 -> 4 -> 5      n = 2  (2nd from the end)
                  ^ remove this
   result:  1 -> 2 -> 3 -> 5
```

## Why this matters

You're asked about a spot measured from the end of a forward-only chain — an end
you haven't reached yet. The move that fixes this is to hold a second pointer a
fixed number of steps *behind* a lead pointer. When the lead reaches the end, the
trailing one is automatically `n` from the end. One pass, no measuring the length
and walking back.

That "trailing window" shows up wherever you process a sequence you can't cheaply
rewind: keeping the last N lines of a log (`tail`), sliding a window over a network
or sensor stream, dropping the oldest entry from a bounded buffer, or streaming a
large file where seeking backward is expensive. Databases and log processors lean
on this so they never buffer the whole input.

What you are buying is a single pass and fixed extra memory. Instead of two walks
(measure, then delete) or storing every node to index from the back, one walk with
a fixed-gap pair does it — the difference that matters when the stream is huge or
arrives live.

## Start from the obvious

"nth from the end" is the same as "(length − n)th from the front." So count first,
then walk.

```diagram
   pass 1 (count):  1 -> 2 -> 3 -> 4 -> 5   ->  length = 5, n = 2
   pass 2 (walk):   stop (5 - 2) = 3 steps in, at node 3 (just before target)
                    1 -> 2 -> 3 -> 4 -> 5
                              ^ node before target
   unlink:          3.next = 3.next.next  ->  3 -> 5
```

Correct, but it walks the list roughly twice, and deleting the *first* node would
be a special case unless you put a dummy node in front.

## Find the waste

The whole first pass exists only to learn the length. You don't need the number —
you need a pointer positioned relative to the end. Park one pointer `n` nodes ahead
of another and slide them together: when the leader falls off the end, the trailing
one lands `n` from the end, no counting.

## The insight

Use a dummy head, then open a gap of exactly `n + 1` between two pointers, and
slide them together until the lead runs off the end.

```diagram
   dummy -> 1 -> 2 -> 3 -> 4 -> 5      n = 2

   open a gap of n+1 = 3 (push lead 3 ahead of trail):
     trail=dummy                 lead=3

   slide both until lead is None:
     trail=1    lead=4
     trail=2    lead=5
     trail=3    lead=None   <- lead fell off
                ^ trail sits just BEFORE the target (node 4)

   unlink:  trail.next = trail.next.next
     dummy -> 1 -> 2 -> 3 -> 5      return dummy.next
```

Why `n + 1` and not `n`? Because you want `trail` to stop on the node *before* the
one you delete, so you can splice around it. The dummy guarantees such a "before"
node always exists — even when the target is the real head.

```diagram
   deleting the real head (n = length):

   dummy -> 1 -> 2 -> 3      n = 3
   trail=dummy      lead=None after the slide
   trail.next = trail.next.next
   dummy -> 2 -> 3      return dummy.next  (new head is 2)
```

## Complexity

- **Time: about `length` steps.** A single pass; the lead pointer crosses the list once.
- **Extra memory: fixed.** Two pointers plus the dummy.

## Pitfalls

- Off-by-one on the gap: `n` steps leaves `trail` *on* the target (can't unlink
  it); `n + 1` leaves it just before. Get this wrong and you delete the wrong node
  or crash.
- Deleting the head: without the dummy you'd need a separate branch. The dummy makes
  `dummy.next = dummy.next.next` handle it, and you return `dummy.next`, not the
  original `head`.
- The problem guarantees `1 <= n <= length`, so you don't defend against `n` too
  large — but the `assert` in the code documents that assumption.

## Transfer

"Two pointers a fixed distance apart" is the reusable move for anything phrased
relative to the end of a forward-only structure — the kth-from-last node, for
instance. It pairs with the dummy-head trick used across list-editing problems like
[merge two lists / 21](../0021-merge-two-sorted-lists/) and Remove Linked List
Elements / 203. The fixed-gap slide is a cousin of the fast/slow walk in
[middle of the list / 876](../0876-middle-of-the-linked-list/).
