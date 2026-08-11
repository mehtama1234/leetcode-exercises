"""19. Remove Nth Node From End of List — https://leetcode.com/problems/remove-nth-node-from-end-of-list/

Remove the nth node counting from the end of the list and return the head.

Two implementations: the honest two-pass (count length, then delete), and the
one-pass gap-of-n trick that finds the target from the end directly.
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


def remove_nth_two_pass(head: Optional[ListNode], n: int) -> Optional[ListNode]:
    """Count length, then walk to the node before the target. O(n) time, O(1) space.

    "nth from the end" is really "the (length - n)th from the front". So pass 1
    measures the length; pass 2 walks to the node just before the target and
    unlinks it. A dummy head in front makes deleting the real head no special
    case. Correct, but it walks most nodes twice.
    """
    dummy = ListNode(0, head)
    length = 0
    node = head
    while node:
        length += 1
        node = node.next
    # Walk to the node right before the (length - n)th-from-front target.
    before = dummy
    for _ in range(length - n):
        assert before.next is not None
        before = before.next
    before.next = before.next.next  # type: ignore[union-attr]
    return dummy.next


def remove_nth(head: Optional[ListNode], n: int) -> Optional[ListNode]:
    """One pass with two pointers held n apart. O(n) time, O(1) space.

    Key insight: keep two pointers exactly n+1 nodes apart. Advance the lead
    pointer n+1 steps first, then move both together until the lead falls off
    the end. Now the trailing pointer sits precisely on the node *before* the
    one to delete — no length count needed. The dummy head handles deleting the
    first node uniformly.
    """
    dummy = ListNode(0, head)
    lead: Optional[ListNode] = dummy
    trail: ListNode = dummy
    # Open a gap of n+1 so trail lands just before the target.
    for _ in range(n + 1):
        assert lead is not None
        lead = lead.next
    while lead:
        lead = lead.next
        trail = trail.next  # type: ignore[assignment]
    trail.next = trail.next.next  # type: ignore[union-attr]
    return dummy.next


def _test() -> None:
    # LeetCode examples
    assert to_list(remove_nth(build_list([1, 2, 3, 4, 5]), 2)) == [1, 2, 3, 5]
    assert to_list(remove_nth(build_list([1]), 1)) == []
    assert to_list(remove_nth(build_list([1, 2]), 1)) == [1]
    # Edge cases: remove the head, remove the tail
    assert to_list(remove_nth(build_list([1, 2]), 2)) == [2]      # remove head
    assert to_list(remove_nth(build_list([1, 2, 3]), 1)) == [1, 2]  # remove tail
    # Two-pass must agree with one-pass on every case
    for vals, n in (([1, 2, 3, 4, 5], 2), ([1], 1), ([1, 2], 1), ([1, 2], 2), ([1, 2, 3], 1)):
        assert to_list(remove_nth_two_pass(build_list(vals), n)) == to_list(
            remove_nth(build_list(vals), n)
        )
    print("remove_nth_from_end: all cases passed")


if __name__ == "__main__":
    _test()
