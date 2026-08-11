"""684. Redundant Connection — https://leetcode.com/problems/redundant-connection/

A tree on n nodes has exactly n-1 edges. We're given n edges (one extra), which
creates exactly one cycle. Return the last edge (in input order) that can be
removed so the graph becomes a tree again.

The key realization: the extra edge is the first one that connects two nodes that
are *already connected*. So we process edges in order and, for each, ask "are these
two endpoints already in the same connected group?" That membership question is
exactly what Union-Find (Disjoint Set Union) answers in near-constant time.
"""
from typing import List


class UnionFind:
    """Disjoint Set Union with path compression + union by rank.

    We track a collection of disjoint groups and support two operations:
      find(x)  -> a canonical representative ("root") of x's group
      union(a,b) -> merge the two groups; returns False if they were already merged

    Two nodes are in the same group iff find(a) == find(b). Both operations run in
    O(alpha(n)) amortized time — alpha is the inverse Ackermann function, which is
    <= 4 for any n you can store. Effectively constant.

    Why so fast? Two optimizations working together:
      * Path compression: find() re-points every node it walks straight to the root,
        so future finds on that chain are O(1). Trees get flat as you use them.
      * Union by rank: always hang the shorter tree under the taller one, so trees
        never grow taller than necessary. Without this, a naive union can build a
        linked list of length n and make find() O(n).
    """

    def __init__(self, n: int) -> None:
        # 1-indexed nodes 1..n; each node starts as its own group (its own root).
        self.parent = list(range(n + 1))
        self.rank = [0] * (n + 1)  # upper bound on tree height per root

    def find(self, x: int) -> int:
        # Walk up to the root, compressing the path as we go.
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:          # second pass: point everyone at root
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a: int, b: int) -> bool:
        """Merge the groups of a and b. Return False if they were already one group."""
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False                       # already connected -> this edge is redundant
        # Attach the shorter tree under the taller one.
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def findRedundantConnection(edges: List[List[int]]) -> List[int]:
    """Return the last edge that closes a cycle. O(n * alpha(n)) time, O(n) space.

    Process edges in the given order. For each edge (u, v), try to union them. The
    first time union() reports "already connected," this edge is the one whose two
    endpoints already had a path between them — i.e. it created the cycle. Since we
    go in input order, it is automatically the last such edge the problem asks for.
    """
    uf = UnionFind(len(edges))  # nodes are labeled 1..n, and there are n edges here
    for u, v in edges:
        if not uf.union(u, v):
            return [u, v]
    return []  # guaranteed unreachable by problem constraints


def _test() -> None:
    # Official LeetCode examples.
    assert findRedundantConnection([[1, 2], [1, 3], [2, 3]]) == [2, 3]
    assert findRedundantConnection(
        [[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]]
    ) == [1, 4]

    # Edge: the redundant edge is the very last one.
    assert findRedundantConnection([[1, 2], [2, 3], [3, 1]]) == [3, 1]

    # Edge: tiny graph, two nodes joined twice.
    assert findRedundantConnection([[1, 2], [1, 2]]) == [1, 2]

    # Direct check on the UnionFind primitive itself.
    uf = UnionFind(4)
    assert uf.union(1, 2) is True
    assert uf.union(3, 4) is True
    assert uf.find(1) == uf.find(2)
    assert uf.find(1) != uf.find(3)
    assert uf.union(2, 3) is True             # merges the two pairs into one group
    assert uf.find(1) == uf.find(4)
    assert uf.union(1, 4) is False            # now already connected

    print("redundant_connection: all cases passed")


if __name__ == "__main__":
    _test()
