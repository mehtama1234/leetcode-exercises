# 206. Reverse Linked List

**Pattern:** In-place pointer manipulation (three-pointer walk)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/reverse-linked-list/

## The problem in plain words

Take a singly linked list `1 -> 2 -> 3` and turn it into `3 -> 2 -> 1`. Return
the new head. Do it by re-wiring the existing nodes, not by copying values.

## Start from the obvious

You *could* dump all the values into an array, reverse the array, and rebuild a
list:

```
vals = [n.val for n in nodes]
vals.reverse()
return build_list(vals)
```

That works but it's wasteful: it allocates a whole second structure to do
something that's really just flipping arrows between nodes you already have.

## Find the waste

Reversing a list doesn't require new nodes at all. Each node already exists; the
only thing "wrong" is the direction of its `next` pointer. So the real job is:
for every node, make its `next` point to the node that currently comes *before*
it. The catch — the moment you overwrite `cur.next`, you lose your way to the
rest of the list. So save it first.

## The insight

Walk the list carrying `prev` (the part already reversed, behind you). At each
node do three moves in this exact order:

```
prev = None
cur = head
while cur:
    nxt = cur.next   # 1. remember the rest before we cut it loose
    cur.next = prev  # 2. flip this link to point backward
    prev = cur       # 3. this node is now the front of the reversed part
    cur = nxt        #    advance into the saved rest
return prev          # cur fell off the end; prev is the old tail = new head
```

Three pointers, one pass, zero extra allocation.

## Complexity

- **Time:** `O(n)` — one link flipped per node.
- **Space:** `O(1)` iterative. The recursive version is also `O(n)` time but
  uses `O(n)` stack frames.

## Pitfalls

- **Order matters.** Save `nxt = cur.next` *before* setting `cur.next = prev`;
  reverse them and you strand the rest of the list.
- Return `prev`, not `cur`. When the loop ends `cur` is `None`; `prev` is the new
  head.
- Empty list and single node: the loop handles both — `prev` ends as `None` or
  the lone node respectively.

## Transfer

Reversing a list (or a *segment* of one) is a building block, not a destination.
It powers [reorder list / 143](../0143-reorder-list/) (reverse the second half),
Reverse Nodes in k-Group / 25, Palindrome Linked List / 234, and Reverse Linked
List II / 92. The three-pointer flip is the muscle memory to internalise.
