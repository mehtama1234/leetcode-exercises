"""226. Invert Binary Tree — https://leetcode.com/problems/invert-binary-tree/

Mirror a binary tree left-to-right: at every node, swap its two children, all
the way down. The result is the tree you'd see in a mirror.
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
    """Build a tree from a level-order list, using None for missing nodes.

    This is the LeetCode input format: read values breadth-first, and every
    non-None value that comes up gets attached as the next open child slot.
    """
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


def to_level_order(root: Optional[TreeNode]) -> List[Optional[int]]:
    """Flatten back to a level-order list (trailing Nones trimmed) for tests."""
    out: List[Optional[int]] = []
    queue = [root]
    while queue:
        node = queue.pop(0)
        if node is None:
            out.append(None)
        else:
            out.append(node.val)
            queue.append(node.left)
            queue.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out


def invert_tree(root: Optional[TreeNode]) -> Optional[TreeNode]:
    """Swap children at every node. O(n) time, O(h) space for the call stack.

    Inverting a tree means: the mirror of a node is a node whose left subtree is
    the mirror of the original right subtree, and vice versa. That sentence is
    already recursive — so trust the recursion to invert each side, then swap.
    The base case is the empty tree, which is its own mirror.
    """
    if root is None:
        return None
    root.left, root.right = invert_tree(root.right), invert_tree(root.left)
    return root


def _test() -> None:
    # LeetCode example 1: [4,2,7,1,3,6,9] -> [4,7,2,9,6,3,1]
    t1 = build_tree([4, 2, 7, 1, 3, 6, 9])
    assert to_level_order(invert_tree(t1)) == [4, 7, 2, 9, 6, 3, 1]
    # LeetCode example 2: [2,1,3] -> [2,3,1]
    t2 = build_tree([2, 1, 3])
    assert to_level_order(invert_tree(t2)) == [2, 3, 1]
    # Edge: empty tree stays empty.
    assert invert_tree(build_tree([])) is None
    # Edge: single node is its own mirror.
    assert to_level_order(invert_tree(build_tree([1]))) == [1]
    print("invert_tree: all cases passed")


if __name__ == "__main__":
    _test()
