"""124. Binary Tree Maximum Path Sum —
https://leetcode.com/problems/binary-tree-maximum-path-sum/

Find the largest possible sum of values along any path in the tree. A path is a
connected sequence of nodes (parent-child links), and it need not pass through
the root.
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


def max_path_sum(root: Optional[TreeNode]) -> int:
    """One DFS that returns a 'downward gain' but records a global best. O(n), O(h).

    The trick is that each node plays TWO roles, so the recursion returns one
    thing but updates another:
    - As the highest point of a path, a node can join its BEST left downward gain
      AND its best right downward gain: total = node.val + left + right. This is
      a candidate for the global answer (a full 'peak' path).
    - But what it can hand UP to its parent is only a straight-line path: the node
      plus AT MOST ONE side, because a parent can't use both of a child's arms.
    So we clamp each side's gain at 0 (never take a negative arm), update a global
    best with the peak, and return node.val + max(left, right) upward.
    """
    best = float("-inf")

    def gain(node: Optional[TreeNode]) -> int:
        nonlocal best
        if node is None:
            return 0
        left = max(gain(node.left), 0)    # drop negative arms
        right = max(gain(node.right), 0)
        best = max(best, node.val + left + right)   # path peaking here
        return node.val + max(left, right)          # what we can extend upward

    gain(root)
    return int(best)


def _test() -> None:
    # LeetCode example 1: [1,2,3] -> 6 (2 + 1 + 3)
    assert max_path_sum(build_tree([1, 2, 3])) == 6
    # LeetCode example 2: [-10,9,20,null,null,15,7] -> 42 (15 + 20 + 7)
    assert max_path_sum(build_tree([-10, 9, 20, None, None, 15, 7])) == 42
    # Edge: all negatives -> pick the single least-bad node.
    assert max_path_sum(build_tree([-3])) == -3
    assert max_path_sum(build_tree([-2, -1])) == -1
    # Edge: single positive node.
    assert max_path_sum(build_tree([5])) == 5
    print("max_path_sum: all cases passed")


if __name__ == "__main__":
    _test()
