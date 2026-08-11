"""142. Linked List Cycle II — https://leetcode.com/problems/linked-list-cycle-ii/

Given the head of a linked list, return the node where the cycle begins. If
there is no cycle, return None.

Two implementations: the honest "remember every node" set, and Floyd's two-phase
fast/slow trick that finds the entry point in O(1) space.
"""
from typing import List, Optional, Set


class ListNode:
    def __init__(self, val: int = 0, next: "Optional[ListNode]" = None):
        self.val = val
        self.next = next


def build_cyclic(values: List[int], pos: int) -> Optional[ListNode]:
    """Build a list and wire the tail's next to node at index `pos`.

    `pos == -1` means no cycle. Returns the head. Test helper only.
    """
    nodes = [ListNode(v) for v in values]
    for i in range(len(nodes) - 1):
        nodes[i].next = nodes[i + 1]
    if pos != -1 and nodes:
        nodes[-1].next = nodes[pos]
    return nodes[0] if nodes else None


def index_of(head: Optional[ListNode], node: Optional[ListNode]) -> int:
    """Return the index of `node` walking from head (for asserts). -1 if None."""
    if node is None:
        return -1
    i = 0
    cur = head
    while cur is not None:
        if cur is node:
            return i
        i += 1
        cur = cur.next
    return -1


def detect_cycle_seen(head: Optional[ListNode]) -> Optional[ListNode]:
    """First node seen twice is the cycle's start. O(n) time, O(n) space.

    The honest idea: walk and remember each node. The very first node you meet
    that's already in your memory is, by definition, the point where the path
    loops back — the cycle entrance. Simple, but pays O(n) memory.
    """
    seen: Set[int] = set()
    node = head
    while node:
        if id(node) in seen:
            return node
        seen.add(id(node))
        node = node.next
    return None


def detect_cycle(head: Optional[ListNode]) -> Optional[ListNode]:
    """Floyd's two-phase pointers. O(n) time, O(1) space.

    Phase 1: run slow (1 step) and fast (2 steps) until they meet inside the
    loop (or fast hits None -> no cycle).

    Phase 2 (the clever part): the math of the meeting point says the distance
    from the *head* to the cycle start equals the distance from the *meeting
    point* to the cycle start (going around). So reset one pointer to head and
    advance both one step at a time; they meet exactly at the cycle entrance.
    """
    slow = head
    fast = head
    while fast and fast.next:
        slow = slow.next  # type: ignore[union-attr]
        fast = fast.next.next
        if slow is fast:
            # Phase 2: walk head and meeting point in lockstep.
            ptr = head
            while ptr is not slow:
                ptr = ptr.next  # type: ignore[union-attr]
                slow = slow.next  # type: ignore[union-attr]
            return ptr
    return None


def _test() -> None:
    # LeetCode examples: (values, pos, expected_index)  pos == expected start
    cases = [
        ([3, 2, 0, -4], 1, 1),
        ([1, 2], 0, 0),
        ([1], -1, -1),
        ([], -1, -1),
        ([1, 2, 3, 4], -1, -1),  # no cycle
        ([1], 0, 0),             # self-loop
        ([1, 2, 3, 4, 5], 4, 4),  # cycle at the tail
    ]
    for vals, pos, expected in cases:
        head = build_cyclic(vals, pos)
        assert index_of(head, detect_cycle(head)) == expected, (vals, pos)
        assert index_of(head, detect_cycle_seen(head)) == expected, (vals, pos)
    print("linked_list_cycle_ii: all cases passed")


if __name__ == "__main__":
    _test()
