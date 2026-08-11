"""323. Number of Connected Components in an Undirected Graph
https://leetcode.com/problems/number-of-connected-components-in-an-undirected-graph/

Given n nodes labeled 0..n-1 and an undirected edge list, count how many separate
connected pieces the graph has.

Start with n lonely nodes = n components. Every edge that joins two nodes which
were NOT already in the same piece merges two pieces into one, dropping the count
by 1. Union-Find makes "are these already together?" an O(1)-ish question.
"""
from typing import List


def count_components(n: int, edges: List[List[int]]) -> int:
    """Union-Find (disjoint set union). Near O(n + e * α(n)) time, O(n) space.

    Think of each node as its own club at the start, so there are n clubs. Walk
    the edges. For an edge (a, b): if a and b are already in the same club, this
    edge is redundant and changes nothing. If they're in different clubs, the edge
    fuses those two clubs into one — so the number of clubs drops by 1. The final
    count is the answer.

    `find` returns a node's club representative and compresses the path so future
    lookups are flat; `union` links one club's root under the other's rank so the
    trees stay shallow. Together they give effectively constant-time operations.
    """
    parent = list(range(n))     # parent[i] = i means i is its own root (a club)
    rank = [0] * n              # rough tree height, to keep unions balanced
    count = n                   # start with n isolated components

    def find(x: int) -> int:
        # Path compression: point every node on the way directly at the root.
        root = x
        while parent[root] != root:
            root = parent[root]
        while parent[x] != root:
            parent[x], x = root, parent[x]
        return root

    def union(a: int, b: int) -> bool:
        ra, rb = find(a), find(b)
        if ra == rb:
            return False  # already in the same component; edge adds nothing
        # Attach the shorter tree under the taller one (union by rank).
        if rank[ra] < rank[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        if rank[ra] == rank[rb]:
            rank[ra] += 1
        return True

    for a, b in edges:
        if union(a, b):
            count -= 1  # two components just merged into one
    return count


def _test() -> None:
    # Official examples
    assert count_components(5, [[0, 1], [1, 2], [3, 4]]) == 2
    assert count_components(5, [[0, 1], [1, 2], [2, 3], [3, 4]]) == 1

    # Edge cases
    assert count_components(4, []) == 4              # no edges -> all isolated
    assert count_components(1, []) == 1             # single node
    # Redundant edge inside one component doesn't lower the count.
    assert count_components(3, [[0, 1], [1, 2], [0, 2]]) == 1
    assert count_components(0, []) == 0             # no nodes

    print("count_components: all cases passed")


if __name__ == "__main__":
    _test()
