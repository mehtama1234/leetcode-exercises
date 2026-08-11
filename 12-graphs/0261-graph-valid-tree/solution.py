"""261. Graph Valid Tree — https://leetcode.com/problems/graph-valid-tree/

Given n nodes labeled 0..n-1 and an undirected edge list, decide whether the graph
is a valid tree: fully connected AND with no cycles.

A tree is exactly "connected + acyclic". There's a shortcut: a connected graph on
n nodes is a tree iff it has exactly n-1 edges. So check the edge count first,
then check connectivity — together they force acyclicity for free.
"""
from typing import List


def valid_tree(n: int, edges: List[List[int]]) -> bool:
    """Edge-count shortcut + one connectivity pass. O(n + e) time, O(n + e) space.

    Two facts about trees on n nodes:
      1. A tree has exactly n-1 edges.
      2. A tree is connected.
    And the key theorem: any graph satisfying BOTH is automatically acyclic — with
    only n-1 edges, being connected leaves no room for an extra edge to close a
    loop. So we don't need a separate cycle check: verify edge count == n-1, then
    verify the whole thing is one connected piece.
    """
    if n == 0:
        return True  # vacuously a tree (no nodes to connect, no cycle)
    if len(edges) != n - 1:
        return False  # too few -> disconnected; too many -> must contain a cycle

    # Build adjacency and do one DFS from node 0. If we can reach all n nodes,
    # the graph is connected; combined with n-1 edges that makes it a tree.
    adj: List[List[int]] = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    seen = set()
    stack = [0] if n > 0 else []
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        for nb in adj[node]:
            if nb not in seen:
                stack.append(nb)

    return len(seen) == n


def _test() -> None:
    # Official examples
    assert valid_tree(5, [[0, 1], [0, 2], [0, 3], [1, 4]]) is True
    assert valid_tree(5, [[0, 1], [1, 2], [2, 3], [1, 3], [1, 4]]) is False  # cycle

    # Edge cases
    assert valid_tree(1, []) is True                 # single node, no edges
    assert valid_tree(2, []) is False                # disconnected (needs 1 edge)
    assert valid_tree(2, [[0, 1]]) is True           # minimal 2-node tree
    # Right edge count (n-1) but disconnected: a triangle + an isolated node.
    assert valid_tree(4, [[0, 1], [1, 2], [0, 2]]) is False
    assert valid_tree(0, []) is True                 # empty graph is trivially a tree

    print("valid_tree: all cases passed")


if __name__ == "__main__":
    _test()
