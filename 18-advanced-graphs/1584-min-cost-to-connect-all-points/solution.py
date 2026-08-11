"""1584. Min Cost to Connect All Points — https://leetcode.com/problems/min-cost-to-connect-all-points/

Given points on a plane, connecting two costs their Manhattan distance. Wire all
points together (any point reachable from any other) for the least total cost.

This is a Minimum Spanning Tree: pick a subset of the possible connections that
touches every point, forms no cycles, and has the smallest total weight. Two
classic MST builders are shown — Prim (grow one tree) and Kruskal (merge
cheapest edges via union-find).
"""
from typing import List, Tuple
import heapq


def min_cost_connect_points_prim(points: List[List[int]]) -> int:
    """Prim's MST. O(n^2 log n) time, O(n) space (dense graph, all pairs).

    Prim grows a single tree from one seed point. At each step it adds the
    cheapest edge that reaches a point *not yet in the tree*. A min-heap of
    (cost, point) candidate edges gives us that cheapest crossing edge quickly.
    Because every pair of points is connectable, the graph is dense — but the
    heap still only ever holds edges out of the current tree.
    """
    n = len(points)
    if n <= 1:
        return 0

    def dist(i: int, j: int) -> int:
        (x1, y1), (x2, y2) = points[i], points[j]
        return abs(x1 - x2) + abs(y1 - y2)

    in_tree = [False] * n
    total = 0
    edges: int = 0
    heap: List[Tuple[int, int]] = [(0, 0)]  # (cost to attach, point index); seed point 0 free

    while heap and edges < n:
        cost, i = heapq.heappop(heap)
        if in_tree[i]:
            continue  # stale candidate — this point already joined via a cheaper edge
        in_tree[i] = True
        total += cost
        edges += 1
        # Offer every not-yet-connected point as a new candidate from point i.
        for j in range(n):
            if not in_tree[j]:
                heapq.heappush(heap, (dist(i, j), j))
    return total


class _DSU:
    """Union-Find with path compression + union by rank, for Kruskal."""

    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # path compression
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False  # already connected — adding this edge would make a cycle
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def min_cost_connect_points_kruskal(points: List[List[int]]) -> int:
    """Kruskal's MST. O(n^2 log n) time, O(n^2) space (holds all edges).

    Kruskal sorts *every* possible edge cheapest-first and adds an edge only if
    its two endpoints aren't already connected — union-find answers "already
    connected?" in near-constant time. Stop once the tree spans all n points
    (n-1 edges accepted). Kept beside Prim so the two philosophies are visible:
    Prim grows one tree, Kruskal merges many.
    """
    n = len(points)
    if n <= 1:
        return 0

    edges: List[Tuple[int, int, int]] = []
    for i in range(n):
        x1, y1 = points[i]
        for j in range(i + 1, n):
            x2, y2 = points[j]
            edges.append((abs(x1 - x2) + abs(y1 - y2), i, j))
    edges.sort()

    dsu = _DSU(n)
    total = 0
    used = 0
    for w, i, j in edges:
        if dsu.union(i, j):
            total += w
            used += 1
            if used == n - 1:
                break  # spanning tree complete
    return total


def _test() -> None:
    cases = [
        ([[0, 0], [2, 2], [3, 10], [5, 2], [7, 0]], 20),
        ([[3, 12], [-2, 5], [-4, 1]], 18),
        ([[0, 0]], 0),                       # one point: nothing to connect
        ([[0, 0], [1, 1]], 2),               # two points: their distance
        ([[-1000000, -1000000], [1000000, 1000000]], 4000000),  # far apart
    ]
    for points, expected in cases:
        assert min_cost_connect_points_prim(points) == expected, points
        # Kruskal must agree with Prim on every case (both find an MST cost).
        assert min_cost_connect_points_kruskal(points) == expected, points
    print("min_cost_connect_points: all cases passed")


if __name__ == "__main__":
    _test()
