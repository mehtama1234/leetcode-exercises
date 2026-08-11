"""104. Maximum Depth of Binary Tree — https://leetcode.com/problems/maximum-depth-of-binary-tree/

Return the number of nodes on the longest path from the root down to a leaf.
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


def max_depth(root: Optional[TreeNode]) -> int:
    """Depth of a tree = 1 + the deeper of its two subtrees. O(n) time, O(h) space.

    "Longest path to a leaf" is recursive by nature: the longest path through the
    root is the root itself (1) plus the longest path in whichever child subtree
    goes deeper. An empty tree has depth 0 — that's the base case that anchors
    the whole recursion.
    """
    if root is None:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))


def max_depth_bfs(root: Optional[TreeNode]) -> int:
    """Same answer by counting levels. O(n) time, O(w) space (w = widest level).

    Kept as a contrast: instead of recursing, walk the tree level by level and
    count how many levels there are. Useful when the recursion depth would blow
    the stack on a very tall tree, and it's the natural shape for BFS problems.
    """
    if root is None:
        return 0
    levels = 0
    queue = [root]
    while queue:
        levels += 1
        nxt = []
        for node in queue:
            if node.left:
                nxt.append(node.left)
            if node.right:
                nxt.append(node.right)
        queue = nxt
    return levels


def _test() -> None:
    # LeetCode example 1: [3,9,20,null,null,15,7] -> 3
    t1 = build_tree([3, 9, 20, None, None, 15, 7])
    assert max_depth(t1) == 3
    assert max_depth_bfs(t1) == 3
    # LeetCode example 2: [1,null,2] -> 2
    t2 = build_tree([1, None, 2])
    assert max_depth(t2) == 2
    assert max_depth_bfs(t2) == 2
    # Edge: empty tree has depth 0.
    assert max_depth(build_tree([])) == 0
    # Edge: single node has depth 1.
    assert max_depth(build_tree([1])) == 1
    print("max_depth: all cases passed")


if __name__ == "__main__":
    _test()
