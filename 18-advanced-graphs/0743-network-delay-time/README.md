# 743. Network Delay Time

**Pattern:** Single-source shortest path (Dijkstra with a heap)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/network-delay-time/

## The problem in plain words

You have a network of nodes wired by directed cables. Each cable takes a known
amount of time to carry a signal. You send a signal out from one node `k`. How
long until *every* node has received it? If some node can never be reached,
return -1.

The trick is spotting that "time until everyone hears it" equals the *longest*
of the shortest travel times from `k`. The signal fans out along the fastest
route to each node; you're done when the last, most-distant node finally hears
it.

## Why this matters

Underneath this is the most common graph question there is: *given a start point
and weighted connections, what is the cheapest way to reach each other point?*
Dijkstra answers it whenever the weights can't be negative — which covers time,
distance, cost, and latency, since none of those go below zero.

This runs real systems every day. Network routing protocols (OSPF is literally
Dijkstra) compute how packets should flow to minimize delay. Map apps finding
the fastest drive treat road segments as weighted edges. A build system or task
scheduler propagating "this finishes, now the next can start" is measuring the
same longest-shortest-path to know total completion time.

What the good solution buys is speed under scale. A naive repeated relaxation is
`O(V·E)`; the heap-driven version is `O(E log V)`. On a graph with millions of
edges that's the difference between a routing table that updates in
milliseconds and one that stalls.

## Start from the obvious

The definition says "find the earliest each node can be reached." You could keep
sweeping every edge and lowering distances until nothing improves — Bellman-Ford:

```
dist[k] = 0, everything else = infinity
repeat V-1 times:
    for each edge (u, v, w):
        dist[v] = min(dist[v], dist[u] + w)
answer = max(dist) if all finite else -1
```

That's correct and honest. But it re-scans *every* edge on *every* pass, even
edges nowhere near improving. That repeated blind sweeping is the waste.

## Find the waste

Bellman-Ford doesn't know which node to finalize next, so it re-checks all of
them. But here's the key fact when weights are non-negative: **the closest
unvisited node's distance is already final.** Nothing farther away can loop back
and make a closer node even closer — that would require a negative edge.

So instead of sweeping everything, always process the *nearest* unfinalized node
next. A min-heap keyed on "distance so far" hands you that nearest node in
`O(log V)`, and each node gets finalized exactly once.

## The insight

Dijkstra grows a finalized set outward from `k`:

1. Push `(0, k)` onto a min-heap.
2. Pop the smallest-distance node. If already finalized, skip (it's a stale
   duplicate). Otherwise finalize it at that distance.
3. Relax its neighbors: push `(dist + edge_weight, neighbor)`.
4. Repeat until the heap empties.

The answer is `max(dist)` over all finalized nodes — the last one to hear the
signal. If fewer than `n` nodes got finalized, one is unreachable → -1.

## Complexity

- **Time:** `O(E log V)` — every edge can push once, each heap op is `O(log V)`.
- **Space:** `O(V + E)` — the adjacency list plus the heap and distance map.

## Pitfalls

- **Nodes are 1-indexed** here (`1..n`), not 0-indexed. Off-by-one bugs are easy.
- Forgetting the **stale-entry skip** (`if node in dist: continue`). Without it
  the heap can re-process a node via a worse path.
- Returning -1 only when the heap empties isn't enough — you must check that
  **all `n`** nodes were reached, not just that you finished.
- Dijkstra is **wrong with negative edges**. If the problem allowed them you'd
  need Bellman-Ford (see the sibling below).

## Transfer

The move "finalize the nearest frontier node next, using a heap" is the reusable
core. It reappears in
[Cheapest Flights Within K Stops / 787](../0787-cheapest-flights-within-k-stops/)
(shortest path with a hop limit),
[Swim in Rising Water / 778](../0778-swim-in-rising-water/) (Dijkstra where the
path cost is a max, not a sum), and
[Path With Minimum Effort / 1631](https://leetcode.com/problems/path-with-minimum-effort/).
Whenever you need cheapest-reach on non-negative weights, reach for Dijkstra.
