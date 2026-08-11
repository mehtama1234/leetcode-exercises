"""743. Network Delay Time — https://leetcode.com/problems/network-delay-time/

A signal starts at node `k` and travels along directed edges, each with a travel
time. Return how long until *every* node has received it, or -1 if some node can
never be reached.

That "time until the last node hears it" is just the largest shortest-path
distance from `k`. So the whole problem is one single-source shortest-path run,
and Dijkstra is the tool because all the times (weights) are non-negative.
"""
from typing import List, Dict, Tuple
import heapq


def network_delay_time(times: List[List[int]], n: int, k: int) -> int:
    """Dijkstra from source `k`. O(E log V) time, O(V + E) space.

    Dijkstra grows a frontier of "already-finalized" nodes. It always pulls the
    unfinalized node with the smallest known distance next — because with
    non-negative edges, nothing discovered later can undercut it. A min-heap keyed
    on distance gives us that "smallest next" in O(log V).

    The answer is the moment the *slowest-to-reach* node is reached: the max over
    all finalized distances. If any node is never popped, it's unreachable → -1.
    """
    graph: Dict[int, List[Tuple[int, int]]] = {node: [] for node in range(1, n + 1)}
    for u, v, w in times:
        graph[u].append((v, w))

    dist: Dict[int, int] = {}          # node -> finalized shortest time
    heap: List[Tuple[int, int]] = [(0, k)]  # (distance-so-far, node)

    while heap:
        d, node = heapq.heappop(heap)
        if node in dist:
            # Already finalized with a smaller distance; this is a stale entry.
            continue
        dist[node] = d
        for nei, w in graph[node]:
            if nei not in dist:
                heapq.heappush(heap, (d + w, nei))

    if len(dist) < n:
        return -1  # some node was never reached
    return max(dist.values())


def _test() -> None:
    # LeetCode example: signal from node 2 reaches all in 2 units.
    assert network_delay_time([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2) == 2
    # Two nodes, direct edge.
    assert network_delay_time([[1, 2, 1]], 2, 1) == 1
    # Node 2 can't reach node 1 (edge goes the other way) → unreachable.
    assert network_delay_time([[1, 2, 1]], 2, 2) == -1
    # Single node, no edges: it already "has" the signal at time 0.
    assert network_delay_time([], 1, 1) == 0
    # Two paths to the same node; the shorter one wins.
    assert network_delay_time([[1, 2, 4], [1, 3, 1], [3, 2, 1]], 3, 1) == 2
    print("network_delay_time: all cases passed")


if __name__ == "__main__":
    _test()
