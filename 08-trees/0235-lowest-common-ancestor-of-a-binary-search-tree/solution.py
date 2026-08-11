"""235. Lowest Common Ancestor of a Binary Search Tree —
https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-search-tree/

Given a BST and two of its nodes p and q, return their lowest (deepest) common
ancestor — the deepest node that has both p and q somewhere below it (a node can
be an ancestor of itself).
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


def find(root: Optional[TreeNode], val: int) -> Optional[TreeNode]:
    """Locate the node with a given value (helper so tests can pass real nodes)."""
    node = root
    while node:
        if val < node.val:
            node = node.left
        elif val > node.val:
            node = node.right
        else:
            return node
    return None


def lowest_common_ancestor(root: Optional[TreeNode],
                           p: TreeNode, q: TreeNode) -> Optional[TreeNode]:
    """Walk down using BST order. O(h) time, O(1) space.

    The BST property is the whole trick. From any node, if BOTH p and q are
    larger than it, the answer must be to the right, so go right. If both are
    smaller, go left. The moment they fall on opposite sides (or one equals the
    current node), this node is where their paths split — that's the lowest node
    that still has both beneath it, i.e. the lowest common ancestor.
    """
    node = root
    while node:
        if p.val > node.val and q.val > node.val:
            node = node.right
        elif p.val < node.val and q.val < node.val:
            node = node.left
        else:
            return node
    return None


def _test() -> None:
    root = build_tree([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5])
    # LeetCode example 1: p=2, q=8 -> 6 (they split at the root)
    assert lowest_common_ancestor(root, find(root, 2), find(root, 8)).val == 6
    # LeetCode example 2: p=2, q=4 -> 2 (a node is an ancestor of itself)
    assert lowest_common_ancestor(root, find(root, 2), find(root, 4)).val == 2
    # Edge: p=3, q=5 both under 4 -> 4
    assert lowest_common_ancestor(root, find(root, 3), find(root, 5)).val == 4
    # Edge: two-node tree [2,1], p=2 q=1 -> 2
    small = build_tree([2, 1])
    assert lowest_common_ancestor(small, find(small, 2), find(small, 1)).val == 2
    print("lowest_common_ancestor: all cases passed")


if __name__ == "__main__":
    _test()
