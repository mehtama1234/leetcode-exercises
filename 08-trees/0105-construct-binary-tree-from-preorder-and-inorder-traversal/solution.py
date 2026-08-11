"""105. Construct Binary Tree from Preorder and Inorder Traversal —
https://leetcode.com/problems/construct-binary-tree-from-preorder-and-inorder-traversal/

Rebuild the unique binary tree given its preorder and inorder value sequences.
"""
from typing import List, Optional, Dict


class TreeNode:
    def __init__(self, val: int = 0,
                 left: "Optional[TreeNode]" = None,
                 right: "Optional[TreeNode]" = None) -> None:
        self.val = val
        self.left = left
        self.right = right


def to_level_order(root: Optional[TreeNode]) -> List[Optional[int]]:
    """Flatten to a level-order list (trailing Nones trimmed) for tests."""
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


def build_tree(preorder: List[int], inorder: List[int]) -> Optional[TreeNode]:
    """Reconstruct the tree. O(n) time, O(n) space.

    Two facts do all the work:
    - Preorder visits root FIRST, so preorder[0] is always the current root.
    - Inorder visits left subtree, then root, then right subtree. So once we know
      the root's value, its position in inorder splits inorder into "everything
      left of the root" (the left subtree) and "everything right" (the right
      subtree). The size of that left part tells us how many of the next preorder
      values belong to the left subtree.
    We pull roots off the front of preorder in order and recurse on the inorder
    slice bounds. A value->index map makes the split lookup O(1).
    """
    index: Dict[int, int] = {val: i for i, val in enumerate(inorder)}
    self_pre = iter(preorder)

    def helper(lo: int, hi: int) -> Optional[TreeNode]:
        if lo > hi:
            return None
        root_val = next(self_pre)          # next root in preorder order
        root = TreeNode(root_val)
        mid = index[root_val]              # split point in inorder
        root.left = helper(lo, mid - 1)    # build left before right — matches
        root.right = helper(mid + 1, hi)   # preorder's root->left->right order
        return root

    return helper(0, len(inorder) - 1)


def _test() -> None:
    # LeetCode example 1
    root = build_tree([3, 9, 20, 15, 7], [9, 3, 15, 20, 7])
    assert to_level_order(root) == [3, 9, 20, None, None, 15, 7]
    # LeetCode example 2: single node
    assert to_level_order(build_tree([-1], [-1])) == [-1]
    # Edge: empty input
    assert build_tree([], []) is None
    # Edge: left-leaning chain preorder=[1,2,3], inorder=[3,2,1]
    assert to_level_order(build_tree([1, 2, 3], [3, 2, 1])) == [1, 2, None, 3]
    print("build_tree: all cases passed")


if __name__ == "__main__":
    _test()
