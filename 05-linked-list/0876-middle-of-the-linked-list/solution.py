"""876. Middle of the Linked List — https://leetcode.com/problems/middle-of-the-linked-list/

Return the middle node of a singly linked list. If there are two middle nodes
(even length), return the second one.

Two implementations sit side by side: the honest two-pass count, and the
one-pass fast/slow trick that gets the answer without knowing the length first.
"""
from typing import List, Optional


class ListNode:
    def __init__(self, val: int = 0, next: "Optional[ListNode]" = None):
        self.val = val
        self.next = next


def build_list(values: List[int]) -> Optional[ListNode]:
    """Turn a Python list into a linked list, return its head (or None)."""
    head: Optional[ListNode] = None
    for v in reversed(values):
        head = ListNode(v, head)
    return head


def to_list(head: Optional[ListNode]) -> List[int]:
    """Turn a linked list back into a Python list, for easy asserts."""
    out: List[int] = []
    while head:
        out.append(head.val)
        head = head.next
    return out


def middle_two_pass(head: Optional[ListNode]) -> Optional[ListNode]:
    """Count the nodes, then walk to index n // 2. O(n) time, O(1) space.

    This is the literal reading of "the middle": you cannot know the middle
    index until you know the length, so pass 1 measures and pass 2 walks. It
    works — but it touches most nodes twice, and that repetition is the waste.
    """
    n = 0
    node = head
    while node:
        n += 1
        node = node.next
    node = head
    for _ in range(n // 2):
        assert node is not None
        node = node.next
    return node


def middle(head: Optional[ListNode]) -> Optional[ListNode]:
    """Fast/slow pointers, single pass. O(n) time, O(1) space.

    Key insight: the middle is just "half as far as the end". So run two
    pointers, slow moving one step and fast moving two. When fast falls off the
    end (or its next is None), fast has covered the whole list and slow has
    covered exactly half — landing on the middle. For an even length this
    naturally returns the *second* middle, which is what the problem asks.
    """
    slow = head
    fast = head
    while fast and fast.next:
        slow = slow.next  # type: ignore[union-attr]
        fast = fast.next.next
    return slow


def _test() -> None:
    # LeetCode examples
    assert to_list(middle(build_list([1, 2, 3, 4, 5]))) == [3, 4, 5]
    assert to_list(middle(build_list([1, 2, 3, 4, 5, 6]))) == [4, 5, 6]
    # Edge cases: single node, two nodes
    assert to_list(middle(build_list([1]))) == [1]
    assert to_list(middle(build_list([1, 2]))) == [2]
    # Two-pass version must agree with the fast one on every case
    for vals in ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5, 6], [1], [1, 2]):
        assert to_list(middle_two_pass(build_list(vals))) == to_list(
            middle(build_list(vals))
        )
    print("middle_of_linked_list: all cases passed")


if __name__ == "__main__":
    _test()
