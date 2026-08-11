# 143. Reorder List

**Pattern:** Compose list primitives (find middle + reverse + merge)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/reorder-list/

## The problem in plain words

Given `1 -> 2 -> 3 -> 4 -> 5`, rearrange it to `1 -> 5 -> 2 -> 4 -> 3`: first
node, then last, then second, then second-to-last, and so on — zig-zagging from
the outside in. Do it in place (rewire nodes, don't just copy values into a new
list, and don't return anything).

## Start from the obvious

Read the target pattern literally: alternate "next from the front" and "next
from the back". With random access that's trivial:

```
arr = [all nodes]
i, j = 0, len(arr) - 1
while i < j:
    link arr[i] -> arr[j] -> arr[i+1]
    i += 1; j -= 1
```

Correct, but it's `O(n)` extra space for the array — and a linked list has no
back-index, so "the node at the end" is exactly what's expensive to reach
repeatedly.

## Find the waste

The array only exists to give us the list *from both ends at once*. There's a
cheaper way to get that: if you cut the list in half and **reverse the second
half**, then the second half is already ordered back-to-front. Now "front, back,
front, back" is just "take one from each half, alternating" — a plain merge, no
indexing.

## The insight

Three primitives you already know, run in sequence:

```
# 1. Find the middle with fast/slow.
slow, fast = head, head
while fast and fast.next:
    slow = slow.next; fast = fast.next.next

# 2. Reverse from slow to the end (the three-pointer flip).
prev = None
while slow:
    nxt = slow.next; slow.next = prev; prev = slow; slow = nxt
# prev = head of reversed second half

# 3. Weave the two halves, alternating nodes.
first, second = head, prev
while second and second.next:
    f, s = first.next, second.next
    first.next = second; second.next = f
    first, second = f, s
```

The second half is the same length or one shorter than the first, so stopping
when `second.next` is `None` leaves the middle node correctly attached.

## Complexity

- **Time:** `O(n)` — each of find-middle, reverse, and merge is a single pass.
- **Space:** `O(1)` — everything is in-place pointer surgery.

## Pitfalls

- The merge stop condition (`while second and second.next`) is fussy. Test both
  even (`[1,2,3,4]`) and odd (`[1,2,3,4,5]`) lengths — off-by-one here either
  drops the middle node or creates a cycle.
- Save `first.next` and `second.next` *before* rewiring, same as ordinary list
  reversal — overwrite first and you lose the rest.
- Empty / single / two-node lists should come out unchanged; guard early.

## Transfer

This is the archetype of "hard list problem = compose easy ones". You're reusing
[find the middle / 876](../0876-middle-of-the-linked-list/) and
[reverse / 206](../0206-reverse-linked-list/) as subroutines. The same
split-reverse-merge combo shows up in Palindrome Linked List / 234 and Sort List
/ 148.
