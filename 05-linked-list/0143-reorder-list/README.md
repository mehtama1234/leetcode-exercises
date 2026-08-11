# 143. Reorder List

**Pattern:** Compose list primitives (find middle + reverse + merge)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/reorder-list/

## The problem in plain words

Given `1 -> 2 -> 3 -> 4 -> 5`, rearrange it to `1 -> 5 -> 2 -> 4 -> 3`: first node,
then last, then second, then second-to-last, zig-zagging from the outside in. Do it
in place — rewire nodes, don't copy values into a new list, and don't return
anything.

```diagram
   from:  1 -> 2 -> 3 -> 4 -> 5
   to:    1 -> 5 -> 2 -> 4 -> 3
          ^front ^back ^front ^back ^middle
```

## Why this matters

This puzzle is really three classic list operations run in sequence, in place: find
the middle, reverse the back half, then weave the two halves together. The skill it
teaches is *restructuring a sequence by relinking pointers* instead of allocating a
copy — splitting, flipping, and zipping without extra storage.

That "transform in place by relinking, not rebuilding" pattern shows up wherever
memory or copying is the constraint. In-place buffer rearrangement drives things
like double-buffering and zero-copy pipelines. Interleaving two halves is the shape
of a perfect shuffle (weaving audio channels, some data-layout tricks). And the
sub-steps — find-middle and reverse — are reusable primitives you'll compose over
and over once you can do each cleanly.

What you are solving for is a non-trivial reshuffle with fixed extra space and a
linear number of pointer moves, instead of dumping everything into an array,
reindexing, and rebuilding. When the structure is large or memory is tight,
composing in-place primitives is what keeps it cheap.

## Start from the obvious

Read the target literally: alternate "next from the front" and "next from the
back." With random access that's easy.

```diagram
   nodes = [1, 2, 3, 4, 5]
   i=0, j=4:  link 1 -> 5 -> 2
   i=1, j=3:  link 2 -> 4 -> 3
   stop when i meets j
   result:  1 -> 5 -> 2 -> 4 -> 3
```

Correct, but it costs a full array's worth of extra memory — and a linked list has
no back-index, so "the node at the end" is exactly what's expensive to reach again
and again.

## Find the waste

The array only exists to give you the list *from both ends at once*. There's a
cheaper way to get that: cut the list in half and **reverse the second half**. Now
the back half is already ordered end-to-front. "Front, back, front, back" becomes
"take one from each half, alternating" — a plain merge, no indexing.

```diagram
   1 -> 2 -> 3 -> 4 -> 5

   find middle (876):        front = 1 -> 2 -> 3
                             back  = 4 -> 5
   reverse back (206):       back  = 5 -> 4
   weave front & back:       1 -> 5 -> 2 -> 4 -> 3
```

## The insight

Three primitives you already know, run in order.

```diagram
   step 1 -- find middle with fast/slow:
     1 -> 2 -> 3 -> 4 -> 5
               ^ slow ends here (middle)

   step 2 -- reverse from the middle onward (three-pointer flip):
     3 -> 4 -> 5   becomes   5 -> 4 -> 3
     front stays:  1 -> 2 -> 3   (3 now also the reversed tail)

   step 3 -- weave, alternating one node from each half:
     take 1(front), then 5(back):   1 -> 5
     take 2(front), then 4(back):   1 -> 5 -> 2 -> 4
     3 is the shared middle:        1 -> 5 -> 2 -> 4 -> 3
```

The back half is the same length as the front or one shorter, so stopping the weave
when `second.next` is `None` leaves the middle node correctly attached.

## Complexity

- **Time: about n steps.** Find-middle, reverse, and weave are each a single pass.
- **Extra memory: fixed.** Everything is in-place pointer surgery.

## Pitfalls

- The weave stop condition (`while second and second.next`) is fussy. Test both
  even (`[1,2,3,4]`) and odd (`[1,2,3,4,5]`) lengths — an off-by-one here either
  drops the middle node or creates a loop.
- Save `first.next` and `second.next` *before* rewiring, same as ordinary reversal.
  Overwrite first and you lose the rest.
- Empty, single, and two-node lists should come out unchanged; guard early.

## Transfer

This is the archetype of "a hard list problem is a few easy ones composed." You're
reusing [find the middle / 876](../0876-middle-of-the-linked-list/) and
[reverse / 206](../0206-reverse-linked-list/) as subroutines, and the weave is a
cousin of [merge two lists / 21](../0021-merge-two-sorted-lists/). The same
split-reverse-merge combo shows up in Palindrome Linked List / 234 and Sort List /
148.
