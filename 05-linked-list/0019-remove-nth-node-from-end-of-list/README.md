# 19. Remove Nth Node From End of List

**Pattern:** Two pointers with a fixed gap + dummy head
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/remove-nth-node-from-end-of-list/

## The problem in plain words

Delete the node that is `n`th from the *end* of the list (n=1 is the last node)
and return the head. A singly linked list only lets you walk forward, so "from
the end" is the awkward part.

## Start from the obvious

"nth from the end" is just "(length − n)th from the front". You can count first,
then walk:

```
length = count all nodes            # pass 1
before = walk (length - n) steps    # pass 2, stop at the node before target
before.next = before.next.next      # unlink
```

Correct and `O(n)`. But it walks the list roughly twice, and it needs a dummy
node in front so that deleting the *first* node isn't a special case.

## Find the waste

The whole first pass exists only to learn the length. But we don't need the
number — we need a pointer positioned relative to the end. If we could park one
pointer `n` nodes ahead of another and slide them together, the trailing one
would automatically be `n` from the end when the leader hits the end. No count
needed.

## The insight

Use a dummy head, then open a gap of exactly `n + 1` between two pointers:

```
dummy = ListNode(0, head)
lead = trail = dummy
for _ in range(n + 1):    # push lead n+1 ahead
    lead = lead.next
while lead:               # slide both until lead runs off the end
    lead = lead.next
    trail = trail.next
trail.next = trail.next.next   # trail is now just before the target
return dummy.next
```

Why `n + 1` and not `n`? Because we want `trail` to stop on the node *before* the
one we delete, so we can splice it out. The dummy guarantees such a "before"
node always exists — even when the target is the real head.

## Complexity

- **Time:** `O(n)` — a single pass; `lead` traverses the list once.
- **Space:** `O(1)` — two pointers plus the dummy.

## Pitfalls

- Off-by-one on the gap: `n` steps leaves `trail` *on* the target (can't unlink
  it); `n + 1` leaves it just before. Get this wrong and you delete the wrong
  node or crash.
- Deleting the head: without the dummy you'd need a separate branch. The dummy
  makes `dummy.next = dummy.next.next` handle it for free — and you return
  `dummy.next`, not the original `head`.
- The problem guarantees `1 <= n <= length`, so you don't have to defend against
  `n` too large — but the `assert` in the code documents the assumption.

## Transfer

"Two pointers a fixed distance apart" is the reusable move for anything phrased
relative to the end of a forward-only structure: find the kth-from-last node,
and it pairs with the dummy-head trick used across list-editing problems like
[merge two lists / 21](../0021-merge-two-sorted-lists/) and Remove Linked List
Elements / 203.
