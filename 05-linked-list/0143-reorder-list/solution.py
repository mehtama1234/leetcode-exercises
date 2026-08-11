"""143. Reorder List — https://leetcode.com/problems/reorder-list/

Reorder a list L0 -> L1 -> ... -> Ln-1 -> Ln into
L0 -> Ln -> L1 -> Ln-1 -> L2 -> Ln-2 -> ...  in place.

Solved by composing three list primitives: find the middle, reverse the second
half, then weave the two halves together.
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


def reorder_list(head: Optional[ListNode]) -> None:
    """Reorder in place by combining three known list moves. O(n) time, O(1) space.

    The target pattern is exactly "front, back, front, back, ...". That's what
    you get by splitting the list in half, reversing the back half, and then
    interleaving the two. Each step is a standard list primitive:

      1. Fast/slow to find the midpoint (start of the second half).
      2. Reverse the second half in place (pointer flips).
      3. Merge the first half and reversed second half by alternating nodes.
    """
    if head is None or head.next is None:
        return

    # 1. Find the middle. `slow` ends at the start of the second half.
    slow: ListNode = head
    fast: Optional[ListNode] = head
    while fast and fast.next:
        slow = slow.next  # type: ignore[assignment]
        fast = fast.next.next

    # 2. Reverse the second half (everything from `slow` onward).
    prev: Optional[ListNode] = None
    cur: Optional[ListNode] = slow
    while cur:
        nxt = cur.next
        cur.next = prev
        prev = cur
        cur = nxt
    # `prev` is now the head of the reversed second half.

    # 3. Weave: first = head, second = prev. The second half is <= first half,
    #    so we stop when `second` runs out.
    first: Optional[ListNode] = head
    second: Optional[ListNode] = prev
    while second and second.next:
        f_next = first.next   # type: ignore[union-attr]
        s_next = second.next
        first.next = second   # type: ignore[union-attr]
        second.next = f_next
        first = f_next
        second = s_next


def _test() -> None:
    # LeetCode examples
    h = build_list([1, 2, 3, 4])
    reorder_list(h)
    assert to_list(h) == [1, 4, 2, 3]

    h = build_list([1, 2, 3, 4, 5])
    reorder_list(h)
    assert to_list(h) == [1, 5, 2, 4, 3]

    # Edge cases: single, two, empty
    h = build_list([1])
    reorder_list(h)
    assert to_list(h) == [1]

    h = build_list([1, 2])
    reorder_list(h)
    assert to_list(h) == [1, 2]

    h = build_list([])
    reorder_list(h)
    assert to_list(h) == []

    print("reorder_list: all cases passed")


if __name__ == "__main__":
    _test()
