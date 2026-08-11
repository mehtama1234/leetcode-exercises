"""572. Subtree of Another Tree — https://leetcode.com/problems/subtree-of-another-tree/

Given a big tree `root` and a small tree `subRoot`, decide whether `subRoot`
appears as a subtree of `root` — same shape and values, hanging off some node.
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
    """Identical shape and values (see problem 100)."""
    if p is None and q is None:
        return True
    if p is None or q is None:
        return False
    return (p.val == q.val
            and is_same_tree(p.left, q.left)
            and is_same_tree(p.right, q.right))


def is_subtree(root: Optional[TreeNode], sub: Optional[TreeNode]) -> bool:
    """Try to match `sub` at every node of `root`. O(n*m) time, O(h) space.

    A subtree isn't just "does the value appear somewhere" — it's "is there a node
    whose ENTIRE tree below it equals `sub`?". So the plan is two nested ideas:
    - walk every node of `root` (that's the outer search), and
    - at each one, ask "is the whole tree rooted here identical to `sub`?" using
      the exact same-tree check from problem 100.
    An empty `sub` is a subtree of anything (vacuously true); a non-empty `sub`
    can't be a subtree of an empty `root`.
    """
    if sub is None:
        return True
    if root is None:
        return False
    if is_same_tree(root, sub):
        return True
    return is_subtree(root.left, sub) or is_subtree(root.right, sub)


def _test() -> None:
    # LeetCode example 1: root=[3,4,5,1,2], sub=[4,1,2] -> True
    r1 = build_tree([3, 4, 5, 1, 2])
    s1 = build_tree([4, 1, 2])
    assert is_subtree(r1, s1) is True
    # LeetCode example 2: root=[3,4,5,1,2,null,null,null,null,0], sub=[4,1,2] -> False
    r2 = build_tree([3, 4, 5, 1, 2, None, None, None, None, 0])
    s2 = build_tree([4, 1, 2])
    assert is_subtree(r2, s2) is False
    # Edge: identical trees — the whole thing is a subtree of itself.
    assert is_subtree(build_tree([1, 1]), build_tree([1, 1])) is True
    # Edge: sub must match a subtree ALL the way down. Here root's every node
    # still has a child, so [1] (a lone leaf) is NOT a subtree of [1,2].
    assert is_subtree(build_tree([1, 2]), build_tree([1])) is False
    # But a real leaf does match: [1] IS a subtree of [1,1] via the left child.
    assert is_subtree(build_tree([1, 1]), build_tree([1])) is True
    # Edge: empty sub is a subtree of anything.
    assert is_subtree(build_tree([1]), build_tree([])) is True
    print("is_subtree: all cases passed")


if __name__ == "__main__":
    _test()
