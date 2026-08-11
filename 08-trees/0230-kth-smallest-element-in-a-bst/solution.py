"""230. Kth Smallest Element in a BST —
https://leetcode.com/problems/kth-smallest-element-in-a-bst/

Given a binary search tree and an integer k, return the k-th smallest value
(1-indexed).
"""
from typing import List, Optional


class TreeNode:
    def __init__(self, val: int = 0,
                 left: "Optional[TreeNode]" = None,
                 right: "Optional[TreeNode]" = None) -> None:
        self.val = val
        self.left = left
        self.right = right


def build_tree(values: List[Optional[int]]) -> Optional[TreeNode]:
    """Build a tree from a level-order list, using None for missing nodes."""
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = [root]
    i = 1
    while queue and i < len(values):
        node = queue.pop(0)
        if i < len(values):
            v = values[i]; i += 1
            if v is not None:
                node.left = TreeNode(v)
                queue.append(node.left)
        if i < len(values):
            v = values[i]; i += 1
            if v is not None:
                node.right = TreeNode(v)
                queue.append(node.right)
    return root


def kth_smallest(root: Optional[TreeNode], k: int) -> int:
    """In-order walk, stop at the k-th node. O(h + k) time, O(h) space.

    An in-order traversal of a BST visits values in sorted order: everything left
    of a node is smaller, so you fully drain the left subtree before emitting the
    node, then handle the right. That means the k-th node you emit is the k-th
    smallest value. We use an explicit stack so we can stop the instant we've
    counted k out, without walking the rest of the tree.
    """
    stack: List[TreeNode] = []
    node = root
    while stack or node:
        # Go as far left as possible, stacking the path.
        while node:
            stack.append(node)
            node = node.left
        node = stack.pop()          # smallest unvisited node
        k -= 1
        if k == 0:
            return node.val
        node = node.right           # then explore its right subtree
    return -1  # unreachable when 1 <= k <= number of nodes


def _test() -> None:
    # LeetCode example 1: [3,1,4,null,2], k=1 -> 1
    assert kth_smallest(build_tree([3, 1, 4, None, 2]), 1) == 1
    # LeetCode example 2: [5,3,6,2,4,null,null,1], k=3 -> 3
    assert kth_smallest(build_tree([5, 3, 6, 2, 4, None, None, 1]), 3) == 3
    # Edge: last element (largest) via k = n
    t = build_tree([5, 3, 6, 2, 4, None, None, 1])  # sorted: 1,2,3,4,5,6
    assert kth_smallest(t, 6) == 6
    # Edge: single node, k=1
    assert kth_smallest(build_tree([1]), 1) == 1
    print("kth_smallest: all cases passed")


if __name__ == "__main__":
    _test()
