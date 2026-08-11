"""206. Reverse Linked List — https://leetcode.com/problems/reverse-linked-list/

Given the head of a singly linked list, reverse it and return the new head.

Two implementations: the iterative pointer-flip (the workhorse) and the
recursive version (same idea, told backwards).
"""
from typing import List, Optional


class ListNode:
    def __init__(self, val: int = 0, next: "Optional[ListNode]" = None):
        self.val = val
        self.next = next


def build_list(values: List[int]) -> Optional[ListNode]:
    """Build a linked list from values, return the head (or None)."""
    head: Optional[ListNode] = None
    for v in reversed(values):
        head = ListNode(v, head)
    return head


def to_list(head: Optional[ListNode]) -> List[int]:
    """Collect a linked list back into a Python list for asserts."""
    out: List[int] = []
    while head:
        out.append(head.val)
        head = head.next
    return out


def reverse_iterative(head: Optional[ListNode]) -> Optional[ListNode]:
    """Flip each next-pointer as you walk. O(n) time, O(1) space.

    Key insight: reversing a list is just re-pointing each node's `next` to the
    node *behind* it. Carry a `prev` (what came before) and, at each node, save
    its `next`, redirect it to `prev`, then slide both forward. When you run off
    the end, `prev` is sitting on the old tail — the new head.
    """
    prev: Optional[ListNode] = None
    cur = head
    while cur:
        nxt = cur.next   # save the rest before we clobber the pointer
        cur.next = prev  # reverse this one link
        prev = cur       # slide prev forward
        cur = nxt        # slide cur forward
    return prev


def reverse_recursive(head: Optional[ListNode]) -> Optional[ListNode]:
    """Same flip, expressed via recursion. O(n) time, O(n) call-stack space.

    Reverse everything after `head`, which hands back the new head of that
    reversed tail. Now `head.next` is the last node of that reversed tail, so
    make it point back to `head` and cut `head`'s own forward link. The deepest
    call (the old tail) is the new head and rides back up unchanged.
    """
    if head is None or head.next is None:
        return head
    new_head = reverse_recursive(head.next)
    head.next.next = head  # the node after head now points back to head
    head.next = None       # head becomes the new tail
    return new_head


def _test() -> None:
    assert to_list(reverse_iterative(build_list([1, 2, 3, 4, 5]))) == [5, 4, 3, 2, 1]
    assert to_list(reverse_iterative(build_list([1, 2]))) == [2, 1]
    assert to_list(reverse_iterative(build_list([]))) == []      # empty
    assert to_list(reverse_iterative(build_list([7]))) == [7]    # single node
    # Recursive must agree on every case
    for vals in ([1, 2, 3, 4, 5], [1, 2], [], [7]):
        assert to_list(reverse_recursive(build_list(vals))) == to_list(
            reverse_iterative(build_list(vals))
        )
    print("reverse_linked_list: all cases passed")


if __name__ == "__main__":
    _test()
