# 206. Reverse Linked List

**Pattern:** In-place pointer flipping (walk with three references)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/reverse-linked-list/

## The problem in plain words

You have a chain of nodes that point forward: `1 -> 2 -> 3`. Turn every arrow
around so it reads `3 -> 2 -> 1`. Return the node that is now the front. Don't
copy the numbers into a new chain — flip the arrows on the nodes you already have.

```diagram
   before:   1 -> 2 -> 3 -> None
   after:    None <- 1 <- 2 <- 3
                              ^ new head
```

## Why this matters

Every node already exists. The only thing "wrong" with the list is the direction
each `next` arrow points. So the real job is small: for each node, make its arrow
point back at the node behind it. The catch is that a singly linked list only lets
you walk forward — the moment you flip an arrow, the way to the rest of the list is
gone unless you saved it first.

This exact move — change a structure while you are still walking through it, one
link at a time, holding only a couple of references — sits under a lot of real
code. Undo/redo stacks and the browser back button hand you events in reverse.
Following a chain of "who called whom" back to its start, or a chain of "next hop"
back to where a packet came from, is the same walk. And reversing a *piece* of a
list is a step inside bigger problems (reorder, palindrome check, reverse in
groups).

What you are buying by doing it in place is one pass and a fixed handful of
pointers, instead of copying every value into an array to reverse it. On a long
list, or in a tight memory budget, that difference is the point.

## Start from the obvious

You could read every value into an array, reverse the array, and build a fresh
list from it.

```diagram
   1 -> 2 -> 3        vals = [1, 2, 3]
                      reverse -> [3, 2, 1]
                      build   -> 3 -> 2 -> 1
```

This works, but it builds a whole second structure to do something that is really
just flipping arrows between nodes you already hold. It costs an extra list's worth
of memory for no reason.

## Find the waste

The array is doing nothing you need. Reversing the list requires zero new nodes.
Each node is already there; its `next` arrow is the only thing pointing the wrong
way. So the actual task is: for each node, point its `next` at the node that
currently sits *before* it. The one danger is that overwriting `cur.next` erases
your path to everything ahead. Save that path first, then flip.

## The insight

Walk the list carrying `prev` — the part you have already reversed, sitting behind
you. At each node do three moves, in this order: remember what's ahead, flip the
arrow backward, then step forward into what you remembered.

```diagram
   step through 1 -> 2 -> 3, one node at a time
   (prev = the reversed part behind us; cur = where we stand)

   start:  prev=None   cur=1     None    1 -> 2 -> 3
   flip 1: prev=1      cur=2     None <- 1    2 -> 3
   flip 2: prev=2      cur=3     None <- 1 <- 2    3
   flip 3: prev=3      cur=None  None <- 1 <- 2 <- 3
                                                  ^ prev = new head
```

The three moves per node, and why each is needed:

```diagram
   standing on cur, prev behind it:

      prev        cur -> nxt -> ...
   1) nxt = cur.next     (save the way forward BEFORE we cut it)
   2) cur.next = prev    (flip: cur now points back at prev)
   3) prev = cur         (cur becomes the front of the reversed part)
      cur = nxt          (step into the saved rest)
```

When `cur` walks off the end and becomes `None`, `prev` is holding the old tail —
which is the new head. Return `prev`.

## Complexity

- **Time: about n steps.** You flip exactly one arrow per node, once.
- **Extra memory: fixed.** Three pointers, no matter how long the list. The
  recursive version does the same work but stacks up about n calls, so it uses
  memory that grows with the list.

## Pitfalls

- **Order matters.** Save `nxt = cur.next` *before* `cur.next = prev`. Do it the
  other way and you strand the rest of the list.
- Return `prev`, not `cur`. When the loop ends `cur` is `None`; `prev` is the new
  head.
- Empty list and single node fall out for free: `prev` ends as `None` or the lone
  node, both correct.

## Transfer

Reversing a list — or a *segment* of one — is a building block, not a
destination. It is the second half of [reorder list / 143](../0143-reorder-list/),
and the same three-pointer flip drives Reverse Nodes in k-Group / 25, Palindrome
Linked List / 234, and Reverse Linked List II / 92. The "save the next link before
you overwrite it" discipline is the muscle memory to keep. It pairs with the
[merge / 21](../0021-merge-two-sorted-lists/) and [find-middle /
876](../0876-middle-of-the-linked-list/) primitives to build harder list problems.
