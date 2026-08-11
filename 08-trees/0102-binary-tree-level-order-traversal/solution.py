"""102. Binary Tree Level Order Traversal —
https://leetcode.com/problems/binary-tree-level-order-traversal/

Return the node values grouped by depth: a list of levels, top to bottom, each
level read left to right.
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


def level_order(root: Optional[TreeNode]) -> List[List[int]]:
    """Breadth-first, one level per iteration. O(n) time, O(w) space.

    The key move is to snapshot the queue's size at the start of each round: that
    count is exactly how many nodes live on the current level. Pop exactly that
    many, collecting their values into one sublist, and enqueue their children —
    which become the next level. Freezing the count before we start adding
    children is what keeps the levels from bleeding into each other.
    """
    result: List[List[int]] = []
    if root is None:
        return result
    queue = [root]
    while queue:
        level_size = len(queue)          # nodes on this level, frozen now
        level: List[int] = []
        for _ in range(level_size):
            node = queue.pop(0)
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)
    return result


def _test() -> None:
    # LeetCode example 1: [3,9,20,null,null,15,7] -> [[3],[9,20],[15,7]]
    t1 = build_tree([3, 9, 20, None, None, 15, 7])
    assert level_order(t1) == [[3], [9, 20], [15, 7]]
    # LeetCode example 2: [1] -> [[1]]
    assert level_order(build_tree([1])) == [[1]]
    # LeetCode example 3: [] -> []
    assert level_order(build_tree([])) == []
    # Edge: left-leaning tree -> one node per level
    assert level_order(build_tree([1, 2, None, 3])) == [[1], [2], [3]]
    print("level_order: all cases passed")


if __name__ == "__main__":
    _test()
