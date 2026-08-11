"""547. Number of Provinces — https://leetcode.com/problems/number-of-provinces/

You're given an n x n matrix where isConnected[i][j] == 1 means city i and city j
are directly connected. A "province" is a group of cities connected directly or
indirectly. Count how many provinces there are.

This is "count the connected components of a graph." Two natural tools: Union-Find
(merge connected cities, then count distinct groups) and a flood-fill DFS. The
Union-Find version is the focus because it makes the counting almost trivial:
start with n groups and subtract one every time an edge merges two different groups.
"""
from typing import List


class UnionFind:
    """Disjoint Set Union with path compression + union by rank.

    Maintains disjoint groups and tracks how many groups currently exist. We start
    with n singleton groups; each successful union (one that merges two *different*
    groups) drops the count by one. Both find and union are O(alpha(n)) amortized —
    effectively constant — thanks to the two optimizations below:
      * Path compression flattens the tree during find, so repeat finds are O(1).
      * Union by rank keeps the shorter tree under the taller one, so no chain can
        grow to length n and blow find up to O(n).
    """

    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.rank = [0] * n
        self.count = n  # number of disjoint groups right now

    def find(self, x: int) -> int:
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:          # compress the path to the root
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a: int, b: int) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False                       # already same group -> nothing merges
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        self.count -= 1                        # two groups became one
        return True


def findCircleNum(isConnected: List[List[int]]) -> int:
    """Count provinces via Union-Find. O(n^2 * alpha(n)) time, O(n) space.

    Union every directly-connected pair. Because the matrix is symmetric, we only
    scan the upper triangle (j > i). After all merges, the number of distinct groups
    IS the number of provinces — no extra counting pass needed.
    """
    n = len(isConnected)
    uf = UnionFind(n)
    for i in range(n):
        for j in range(i + 1, n):
            if isConnected[i][j] == 1:
                uf.union(i, j)
    return uf.count


def findCircleNum_dfs(isConnected: List[List[int]]) -> int:
    """Alternative: flood-fill DFS. Same O(n^2) time, O(n) space.

    Kept to show the other honest answer. Walk over cities; each time you find one
    not yet visited, that's a new province, so mark its whole reachable set visited
    with a DFS. The count of "new starts" is the number of provinces. Union-Find is
    preferable when connections arrive incrementally; DFS is fine for a fixed matrix.
    """
    n = len(isConnected)
    seen = [False] * n

    def dfs(city: int) -> None:
        seen[city] = True
        for nxt in range(n):
            if isConnected[city][nxt] == 1 and not seen[nxt]:
                dfs(nxt)

    provinces = 0
    for city in range(n):
        if not seen[city]:
            provinces += 1
            dfs(city)
    return provinces


def _test() -> None:
    # Official LeetCode examples.
    ex1 = [[1, 1, 0], [1, 1, 0], [0, 0, 1]]
    assert findCircleNum(ex1) == 2
    assert findCircleNum_dfs(ex1) == 2

    ex2 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    assert findCircleNum(ex2) == 3
    assert findCircleNum_dfs(ex2) == 3

    # Edge: single city -> one province.
    assert findCircleNum([[1]]) == 1

    # Edge: all cities connected in a chain -> one province.
    chain = [
        [1, 1, 0, 0],
        [1, 1, 1, 0],
        [0, 1, 1, 1],
        [0, 0, 1, 1],
    ]
    assert findCircleNum(chain) == 1
    assert findCircleNum_dfs(chain) == 1

    print("number_of_provinces: all cases passed")


if __name__ == "__main__":
    _test()
