"""98. Validate Binary Search Tree — https://leetcode.com/problems/validate-binary-search-tree/

Decide whether a binary tree is a valid BST: every node's value is greater than
everything in its left subtree and less than everything in its right subtree.
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


def is_valid_bst(root: Optional[TreeNode]) -> bool:
    """Carry an allowed (low, high) range down the tree. O(n) time, O(h) space.

    The naive check "left child < node < right child" is NOT enough: a value must
    beat EVERY ancestor it descended from, not just its parent. So each node
    inherits an open interval (low, high) of values it's allowed to take. Going
    left tightens the upper bound to the parent's value; going right raises the
    lower bound to the parent's value. A node is valid iff it sits strictly inside
    its interval and both children are valid under their tightened ranges.
    """
    def valid(node: Optional[TreeNode],
              low: float, high: float) -> bool:
        if node is None:
            return True
        if not (low < node.val < high):
            return False
        return (valid(node.left, low, node.val)
                and valid(node.right, node.val, high))

    return valid(root, float("-inf"), float("inf"))


def _test() -> None:
    # LeetCode example 1: [2,1,3] -> True
    assert is_valid_bst(build_tree([2, 1, 3])) is True
    # LeetCode example 2: [5,1,4,null,null,3,6] -> False (3 and 6 sit right of 5)
    assert is_valid_bst(build_tree([5, 1, 4, None, None, 3, 6])) is False
    # Edge: a grandchild violates an ancestor though it beats its parent.
    #   [5,4,6,null,null,3,7]: 3 is left-subtree of 6 but must also be > 5.
    assert is_valid_bst(build_tree([5, 4, 6, None, None, 3, 7])) is False
    # Edge: single node is a valid BST.
    assert is_valid_bst(build_tree([1])) is True
    # Edge: empty tree is a valid BST.
    assert is_valid_bst(build_tree([])) is True
    print("is_valid_bst: all cases passed")


if __name__ == "__main__":
    _test()
