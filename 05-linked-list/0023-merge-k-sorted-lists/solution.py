"""23. Merge k Sorted Lists — https://leetcode.com/problems/merge-k-sorted-lists/

Given an array of k sorted linked lists, merge them all into one sorted list
and return its head.

Two implementations: the naive "merge them one at a time" and the optimal
divide-and-conquer pairwise merge (with a heap variant noted in the README).
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


def _merge_two(
    l1: Optional[ListNode], l2: Optional[ListNode]
) -> Optional[ListNode]:
    """Merge two sorted lists (the reusable subroutine from problem 21)."""
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
    tail.next = l1 if l1 else l2
    return dummy.next


def merge_k_lists_naive(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """Fold the lists one at a time into an accumulator. O(k * N) time.

    The obvious idea: merge list 0 with list 1, then merge that with list 2, and
    so on. It's correct, but the growing accumulator gets re-walked on every
    step — after i merges it may hold i lists' worth of nodes, so total work is
    roughly N + 2N/k + ... which sums to O(k * N). That repeated re-walking of
    the accumulator is the waste the optimal version removes.
    """
    result: Optional[ListNode] = None
    for lst in lists:
        result = _merge_two(result, lst)
    return result


def merge_k_lists(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """Divide and conquer: pair up and merge. O(N log k) time, O(1) extra.

    Instead of one growing accumulator, merge the lists in pairs so each round
    halves how many lists remain: k -> k/2 -> k/4 -> ... -> 1. Every node is
    touched once per round and there are log k rounds, giving O(N log k). This
    mirrors the merge step of merge sort, one level up.
    """
    if not lists:
        return None
    while len(lists) > 1:
        merged: List[Optional[ListNode]] = []
        for i in range(0, len(lists), 2):
            a = lists[i]
            b = lists[i + 1] if i + 1 < len(lists) else None
            merged.append(_merge_two(a, b))
        lists = merged
    return lists[0]


def _test() -> None:
    # LeetCode example
    lists = [build_list([1, 4, 5]), build_list([1, 3, 4]), build_list([2, 6])]
    assert to_list(merge_k_lists([build_list([1, 4, 5]), build_list([1, 3, 4]), build_list([2, 6])])) == [
        1, 1, 2, 3, 4, 4, 5, 6,
    ]
    # Edge cases from LeetCode: empty array, array of one empty list
    assert to_list(merge_k_lists([])) == []
    assert to_list(merge_k_lists([build_list([])])) == []
    # Mixed empties and a single list
    assert to_list(merge_k_lists([build_list([]), build_list([1]), build_list([])])) == [1]
    # Naive must agree with the optimal on every case
    for arr in (
        [[1, 4, 5], [1, 3, 4], [2, 6]],
        [],
        [[]],
        [[], [1], []],
        [[5], [1, 2, 3], [4]],
    ):
        opt = to_list(merge_k_lists([build_list(a) for a in arr]))
        naive = to_list(merge_k_lists_naive([build_list(a) for a in arr]))
        assert opt == naive, arr
    print("merge_k_sorted_lists: all cases passed")


if __name__ == "__main__":
    _test()
