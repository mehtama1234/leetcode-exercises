"""332. Reconstruct Itinerary — https://leetcode.com/problems/reconstruct-itinerary/

Given a list of airline tickets [from, to], reconstruct one trip that uses *every*
ticket exactly once, starting from "JFK". Among all valid trips, return the one
that is smallest in lexical order.

Each ticket is a directed edge and must be used once — that is an *Eulerian path*
(a walk covering every edge exactly once). Hierholzer's algorithm builds it; the
"smallest lexical order" is enforced by always taking the alphabetically-first
unused edge, achieved cleanly with a min-heap of destinations per airport.
"""
from typing import List, Dict
import heapq
from collections import defaultdict


def find_itinerary(tickets: List[List[str]]) -> List[str]:
    """Hierholzer's algorithm with lexical (heap) tie-breaking. O(E log E) time.

    Why this works: a valid itinerary using every ticket once is an Eulerian path.
    Hierholzer walks forward greedily, and when it gets *stuck* (no unused edge
    out of the current airport), that airport must be the end of the trip — so we
    prepend it to the answer and back up. Nodes finalize in reverse, so we build
    the route back-to-front.

    Lexical smallest: at each airport, always follow the alphabetically-smallest
    unused destination. A min-heap per airport gives that in O(log) per pop. The
    greedy "smallest edge first" combined with Hierholzer's stuck-then-prepend
    provably yields the lexically smallest Eulerian path.
    """
    graph: Dict[str, List[str]] = defaultdict(list)
    for src, dst in tickets:
        heapq.heappush(graph[src], dst)  # min-heap => smallest destination pops first

    route: List[str] = []
    stack: List[str] = ["JFK"]

    while stack:
        airport = stack[-1]
        if graph[airport]:
            # Still have an unused outgoing ticket — follow the smallest one.
            stack.append(heapq.heappop(graph[airport]))
        else:
            # Stuck: this airport is the current end of the trail. Retreat.
            route.append(stack.pop())

    return route[::-1]  # built back-to-front, so reverse


def _test() -> None:
    # LeetCode example 1.
    assert find_itinerary(
        [["MUC", "LHR"], ["JFK", "MUC"], ["SFO", "SJC"], ["LHR", "SFO"]]
    ) == ["JFK", "MUC", "LHR", "SFO", "SJC"]

    # Example 2: two routes from JFK; lexical order picks ATL first.
    assert find_itinerary(
        [["JFK", "SFO"], ["JFK", "ATL"], ["SFO", "ATL"], ["ATL", "JFK"], ["ATL", "SFO"]]
    ) == ["JFK", "ATL", "JFK", "SFO", "ATL", "SFO"]

    # Single ticket.
    assert find_itinerary([["JFK", "A"]]) == ["JFK", "A"]

    # Must reuse an airport; greedy-smallest could dead-end if naive, Hierholzer
    # handles it. Here JFK->KUL would strand ORD's ticket, so NRT must come first.
    assert find_itinerary(
        [["JFK", "KUL"], ["JFK", "NRT"], ["NRT", "JFK"]]
    ) == ["JFK", "NRT", "JFK", "KUL"]

    print("find_itinerary: all cases passed")


if __name__ == "__main__":
    _test()
