# 876. Middle of the Linked List

**Pattern:** Fast/slow pointers (two pointers on a list)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/middle-of-the-linked-list/

## The problem in plain words

You have a singly linked list. Return the node in the middle. If the list has an
even number of nodes there are two "middles" — return the second one.

## Start from the obvious

You can only find the middle *index* if you know the length. So count first,
then walk halfway:

```
n = number of nodes         # pass 1: walk the whole list counting
node = head
for _ in range(n // 2):     # pass 2: walk to the middle index
    node = node.next
return node
```

That's correct and `O(n)`. It's the honest first thought — but notice it walks
the list essentially twice.

## Find the waste

The two passes exist only because we insisted on knowing `n` before moving. But
"middle" has a cheaper definition: it is the point you reach when you've gone
*half* as far as the end. If something could measure "half the distance to the
end" while walking, we'd never need a separate counting pass.

## The insight

Move two pointers at different speeds. `slow` takes one step per turn, `fast`
takes two. By the time `fast` reaches the end of the list, it has travelled
twice as far — so `slow` sits at exactly the halfway point.

```
while fast and fast.next:
    slow = slow.next
    fast = fast.next.next
return slow          # slow is now the middle
```

The loop condition does the work of choosing the correct middle for even
lengths: `fast` stops when it or its `next` is `None`, and that leaves `slow`
on the *second* of the two middles — exactly what the problem wants.

## Complexity

- **Time:** `O(n)` — one pass; `fast` covers the list once.
- **Space:** `O(1)` — two pointers, nothing allocated.

## Pitfalls

- Loop guard must be `while fast and fast.next`. Drop the `fast.next` check and
  `fast.next.next` blows up with a `NoneType` error on even-length lists.
- Off-by-one: starting both pointers at `head` (not one at `head.next`) is what
  gives the *second* middle. If a problem wanted the first middle, you'd start
  `fast` one node ahead.
- Empty list: the loop never runs and `slow` stays `None`, which is correct.

## Transfer

Fast/slow pointers are the backbone of many list problems: cycle detection
([141](../0141-linked-list-cycle/), [142](../0142-linked-list-cycle-ii/)),
finding the nth-from-end node ([19](../0019-remove-nth-node-from-end-of-list/)),
and splitting a list in half for
[reorder](../0143-reorder-list/). Whenever you need a position defined
*relative to the end* without knowing the length up front, reach for two
pointers at different speeds.
