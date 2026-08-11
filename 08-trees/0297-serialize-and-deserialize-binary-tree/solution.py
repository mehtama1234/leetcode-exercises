"""297. Serialize and Deserialize Binary Tree —
https://leetcode.com/problems/serialize-and-deserialize-binary-tree/

Turn a binary tree into a string, and turn that string back into the exact same
tree. Any format works as long as serialize -> deserialize round-trips.
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


class Codec:
    """Serialize/deserialize using preorder DFS with explicit null markers.

    A plain list of values is NOT enough to rebuild a tree — you lose the shape.
    The fix is to record the MISSING children too: writing a sentinel ('#') for
    every empty child makes the structure unambiguous. Preorder (root, left,
    right) means deserialize can consume tokens front-to-back and rebuild in the
    exact order they were written, so no index bookkeeping is needed.
    """

    def serialize(self, root: Optional[TreeNode]) -> str:
        """Preorder walk, emitting '#' for None. O(n) time, O(n) space."""
        parts: List[str] = []

        def dfs(node: Optional[TreeNode]) -> None:
            if node is None:
                parts.append("#")
                return
            parts.append(str(node.val))
            dfs(node.left)
            dfs(node.right)

        dfs(root)
        return ",".join(parts)

    def deserialize(self, data: str) -> Optional[TreeNode]:
        """Rebuild by consuming tokens in the same preorder. O(n) time, O(n) space."""
        tokens = iter(data.split(","))

        def build() -> Optional[TreeNode]:
            val = next(tokens)
            if val == "#":
                return None
            node = TreeNode(int(val))
            node.left = build()     # left subtree comes next in preorder
            node.right = build()    # then the right subtree
            return node

        return build()


def _test() -> None:
    codec = Codec()

    def round_trip(values: List[Optional[int]]) -> List[Optional[int]]:
        tree = build_tree(values)
        return to_level_order(codec.deserialize(codec.serialize(tree)))

    # LeetCode example 1: [1,2,3,null,null,4,5] round-trips.
    assert round_trip([1, 2, 3, None, None, 4, 5]) == [1, 2, 3, None, None, 4, 5]
    # Edge: empty tree round-trips to empty.
    assert round_trip([]) == []
    # Edge: single node.
    assert round_trip([1]) == [1]
    # Edge: negative values and a lopsided shape.
    assert round_trip([-5, 3, None, -2]) == [-5, 3, None, -2]
    # Sanity: serialization is a plain comma string.
    assert codec.serialize(build_tree([1, 2, 3])) == "1,2,#,#,3,#,#"
    print("Codec: all cases passed")


if __name__ == "__main__":
    _test()
