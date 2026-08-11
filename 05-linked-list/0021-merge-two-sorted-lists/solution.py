"""21. Merge Two Sorted Lists — https://leetcode.com/problems/merge-two-sorted-lists/

Given the heads of two sorted linked lists, splice them into one sorted list
and return its head.

One clean function: a dummy-headed merge that stitches nodes together in order.
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


def merge_two_lists(
    l1: Optional[ListNode], l2: Optional[ListNode]
) -> Optional[ListNode]:
    """Zip two sorted lists together. O(n + m) time, O(1) extra space.

    Because both inputs are already sorted, the next node of the answer is
    always whichever of the two current heads is smaller. So keep a `tail`
    pointer and repeatedly attach the smaller head, advancing that list. A dummy
    node in front means we never special-case "which list starts the result".
    When one list runs out, the other is already sorted — attach it wholesale.
    We reuse the existing nodes; nothing is copied.
    """
    dummy = ListNode()
    tail = dummy
    while l1 and l2:
        if l1.val <= l2.val:
            tail.next = l1
            l1 = l1.next
        else:
            tail.next = l2
            l2 = l2.next
        tail = tail.next
    # At most one list is non-empty; splice the remainder on directly.
    tail.next = l1 if l1 else l2
    return dummy.next


def _test() -> None:
    # LeetCode examples
    assert to_list(merge_two_lists(build_list([1, 2, 4]), build_list([1, 3, 4]))) == [
        1, 1, 2, 3, 4, 4,
    ]
    assert to_list(merge_two_lists(build_list([]), build_list([]))) == []
    assert to_list(merge_two_lists(build_list([]), build_list([0]))) == [0]
    # Edge cases: one list fully precedes the other, unequal lengths
    assert to_list(merge_two_lists(build_list([1, 2, 3]), build_list([4, 5, 6]))) == [
        1, 2, 3, 4, 5, 6,
    ]
    assert to_list(merge_two_lists(build_list([5]), build_list([1, 2, 3]))) == [
        1, 2, 3, 5,
    ]
    print("merge_two_sorted_lists: all cases passed")


if __name__ == "__main__":
    _test()
