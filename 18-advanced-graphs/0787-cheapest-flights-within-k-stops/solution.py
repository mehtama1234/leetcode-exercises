"""787. Cheapest Flights Within K Stops — https://leetcode.com/problems/cheapest-flights-within-k-stops/

Find the cheapest price from `src` to `dst` using at most `k` intermediate stops
(so at most k+1 flights). Return -1 if no such route exists.

Plain Dijkstra minimizes price but ignores the hop limit — it might reach a city
cheaply only via a long route. The fix is Bellman-Ford's structure: relax edges
in *rounds*, where round i finds the cheapest price reachable using ≤ i flights.
Run exactly k+1 rounds and the hop limit is baked in.
"""
from typing import List


def find_cheapest_price(n: int, flights: List[List[int]], src: int, dst: int, k: int) -> int:
    """Bellman-Ford limited to k+1 rounds. O(k * E) time, O(V) space.

    Key idea: with at most k stops you may take at most k+1 flights. Bellman-Ford
    relaxes edges in rounds; after round i, `dist[city]` holds the cheapest way to
    reach that city using *at most i* flights. So we simply run k+1 rounds.

    The one subtlety: within a single round, every relaxation must read from a
    *snapshot* of the previous round's distances, not from values already updated
    this round. Otherwise a price could hop across two edges inside one round,
    letting the route sneak in extra flights beyond the limit. We copy `dist`
    into `curr` each round to enforce "one flight per round".
    """
    INF = float("inf")
    dist = [INF] * n
    dist[src] = 0

    for _ in range(k + 1):
        curr = dist[:]  # snapshot: this round may add exactly one more flight
        for u, v, price in flights:
            if dist[u] != INF and dist[u] + price < curr[v]:
                curr[v] = dist[u] + price
        dist = curr

    return -1 if dist[dst] == INF else dist[dst]


def _test() -> None:
    # LeetCode examples.
    flights = [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600], [2, 3, 200]]
    assert find_cheapest_price(4, flights, 0, 3, 1) == 700
    # Same graph, k=0 (direct flights only): 0->3 impossible in one hop → -1.
    assert find_cheapest_price(4, flights, 0, 3, 0) == -1

    f2 = [[0, 1, 100], [1, 2, 100], [0, 2, 500]]
    assert find_cheapest_price(3, f2, 0, 2, 1) == 200  # via 1 (2 hops) beats direct 500
    assert find_cheapest_price(3, f2, 0, 2, 0) == 500  # only direct allowed

    # Cheaper multi-hop route exists but exceeds the hop budget → must ignore it.
    f3 = [[0, 1, 1], [1, 2, 1], [2, 3, 1], [0, 3, 10]]
    assert find_cheapest_price(4, f3, 0, 3, 1) == 10   # 3-hop route needs k=2; only direct fits
    assert find_cheapest_price(4, f3, 0, 3, 2) == 3    # now the 3-flight route is allowed

    # Source equals destination: free.
    assert find_cheapest_price(3, f2, 0, 0, 1) == 0
    # Unreachable city.
    assert find_cheapest_price(3, [[0, 1, 5]], 0, 2, 5) == -1
    print("find_cheapest_price: all cases passed")


if __name__ == "__main__":
    _test()
