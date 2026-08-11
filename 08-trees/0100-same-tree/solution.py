"""100. Same Tree — https://leetcode.com/problems/same-tree/

Given two binary trees, decide whether they are identical: same shape and the
same value at every matching position.
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


def is_same_tree(p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:
    """Two trees match iff their roots match and their subtrees match. O(n), O(h).

    Walk both trees in lockstep. At each pair of positions there are three cases:
    - both empty  -> they agree here (True)
    - one empty   -> shapes differ (False)
    - both present-> values must be equal AND both subtrees must be equal
    That third case is the recursion: the "same" relation on trees is defined in
    terms of "same" on their children.
    """
    if p is None and q is None:
        return True
    if p is None or q is None:
        return False
    return (p.val == q.val
            and is_same_tree(p.left, q.left)
            and is_same_tree(p.right, q.right))


def _test() -> None:
    # LeetCode example 1: p=[1,2,3], q=[1,2,3] -> True
    assert is_same_tree(build_tree([1, 2, 3]), build_tree([1, 2, 3])) is True
    # LeetCode example 2: p=[1,2], q=[1,null,2] -> False (shape differs)
    assert is_same_tree(build_tree([1, 2]), build_tree([1, None, 2])) is False
    # LeetCode example 3: p=[1,2,1], q=[1,1,2] -> False (values differ)
    assert is_same_tree(build_tree([1, 2, 1]), build_tree([1, 1, 2])) is False
    # Edge: two empty trees are the same.
    assert is_same_tree(build_tree([]), build_tree([])) is True
    # Edge: one empty, one not.
    assert is_same_tree(build_tree([]), build_tree([1])) is False
    print("is_same_tree: all cases passed")


if __name__ == "__main__":
    _test()
