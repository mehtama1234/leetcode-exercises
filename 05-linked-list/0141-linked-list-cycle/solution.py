"""141. Linked List Cycle — https://leetcode.com/problems/linked-list-cycle/

Given the head of a linked list, return True if the list contains a cycle
(some node's `next` points back to an earlier node), else False.

Two implementations: the honest "remember every node we've seen" set, and the
O(1)-space fast/slow (Floyd's) trick that needs no extra memory.
"""
from typing import List, Optional, Set


class ListNode:
    def __init__(self, val: int = 0, next: "Optional[ListNode]" = None):
        self.val = val
        self.next = next


def build_list(values: List[int]) -> Optional[ListNode]:
    """Build a plain (acyclic) linked list from values, return the head."""
    head: Optional[ListNode] = None
    for v in reversed(values):
        head = ListNode(v, head)
    return head


def build_cyclic(values: List[int], pos: int) -> Optional[ListNode]:
    """Build a list, then wire the last node's next to node at index `pos`.

    `pos == -1` means no cycle. This is only a test helper — it lets us create
    the cyclic inputs LeetCode describes without drawing them by hand.
    """
    nodes = [ListNode(v) for v in values]
    for i in range(len(nodes) - 1):
        nodes[i].next = nodes[i + 1]
    if pos != -1 and nodes:
        nodes[-1].next = nodes[pos]
    return nodes[0] if nodes else None


def has_cycle_seen(head: Optional[ListNode]) -> bool:
    """Remember every node visited; a repeat means a cycle. O(n) time/space.

    The honest first idea: a cycle is exactly "we came back to a node we already
    stood on". So store visited nodes in a set and check membership as we walk.
    Correct, but it pays O(n) memory just to detect a yes/no fact.
    """
    seen: Set[int] = set()
    node = head
    while node:
        if id(node) in seen:
            return True
        seen.add(id(node))
        node = node.next
    return False


def has_cycle(head: Optional[ListNode]) -> bool:
    """Floyd's fast/slow pointers. O(n) time, O(1) space.

    Key insight: if there's a cycle, a pointer moving 2 steps per turn will
    lap a pointer moving 1 step and they must eventually land on the same node
    — like a faster runner catching a slower one on a circular track. If there's
    no cycle, the fast pointer just runs off the end (`None`) and we return
    False. No extra memory needed.
    """
    slow = head
    fast = head
    while fast and fast.next:
        slow = slow.next  # type: ignore[union-attr]
        fast = fast.next.next
        if slow is fast:
            return True
    return False


def _test() -> None:
    # LeetCode examples (values, pos, expected)
    cases = [
        ([3, 2, 0, -4], 1, True),
        ([1, 2], 0, True),
        ([1], -1, False),
        ([], -1, False),
        ([1, 2, 3, 4], -1, False),  # no cycle
        ([1], 0, True),             # single node pointing to itself
    ]
    for vals, pos, expected in cases:
        head = build_cyclic(vals, pos)
        assert has_cycle(head) == expected, (vals, pos)
        assert has_cycle_seen(head) == expected, (vals, pos)
    print("linked_list_cycle: all cases passed")


if __name__ == "__main__":
    _test()
