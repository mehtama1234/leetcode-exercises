# 743. Network Delay Time

**Pattern:** Shortest path from one source (Dijkstra with a heap)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/network-delay-time/

## The problem in plain words

You have nodes wired together by one-way cables. Each cable takes a known amount
of time to pass a signal along. You send a signal out from one node `k`. How long
until *every* node has heard it? If some node can never be reached, return -1.

The one thing to see: "time until everyone hears it" is the *longest* of the
shortest travel times from `k`. The signal races to each node by its fastest
route, and you are done the moment the last, most-distant node finally hears it.

```diagram
   send from node 2       edge weights = travel time

        2 --1--> 1
        |
        1
        v
        3 --1--> 4

   fastest time to each:  1:1   2:0   3:1   4:2
   last to hear it is node 4 at time 2   ->  answer = 2
```

## Why this matters

Underneath the story is the most common graph question there is: *given a start
point and weighted links, what is the cheapest way to reach every other point?*
Dijkstra answers it whenever the weights never go below zero — which covers time,
distance, cost, and delay, since none of those can be negative.

This runs real systems every day. Network routing protocols (OSPF is literally
Dijkstra) work out how packets should flow to keep delay low. Map apps finding
the fastest drive treat road segments as weighted links. A task scheduler that
says "this finishes, now the next can start" is measuring the same
longest-of-the-shortest time to know when the whole job is done.

What the good version buys is speed at scale. Re-checking every link over and
over is about `V·E` steps; the heap-driven version is about `E·log V`. On a graph
with millions of links that is the line between a routing table that updates in
milliseconds and one that stalls.

## Start from the obvious

The definition says "find the earliest each node can be reached." So keep sweeping
every link and lowering distances until nothing improves — that is Bellman-Ford:

```diagram
   dist[k] = 0,  everything else = infinity
   repeat V-1 times:
       for each link (u, v, w):
           dist[v] = min(dist[v], dist[u] + w)
   answer = max(dist) if all finite, else -1
```

Correct and honest. But it re-scans *every* link on *every* pass, even links
nowhere near improving anything. That repeated blind sweeping is the waste.

## Find the waste

Bellman-Ford doesn't know which node to lock in next, so it re-checks all of
them. But here is the key fact when weights never go below zero: **the closest
unfinished node's distance is already final.** Nothing farther away can loop back
and make a closer node even closer — that would need a negative link, and there
are none.

So instead of sweeping everything, always finish the *nearest* unfinished node
next. A min-heap (a bucket that always hands you its smallest item) keyed on
"distance so far" gives you that nearest node in about `log V` steps, and each
node gets locked in exactly once.

## The insight

Dijkstra grows a finished set outward from `k`, always reaching for the nearest
node still on the frontier.

```diagram
   start: send from k=2,  heap = [(0, 2)]     dist = {}

   pop (0,2)  -> lock 2 at 0    push (1,1) (1,3)
                 heap = [(1,1),(1,3)]

   pop (1,1)  -> lock 1 at 1    (no outgoing)
                 heap = [(1,3)]

   pop (1,3)  -> lock 3 at 1    push (2,4)
                 heap = [(2,4)]

   pop (2,4)  -> lock 4 at 2
                 heap = []

   dist = {2:0, 1:1, 3:1, 4:2}    max = 2   <- last node to hear it
```

Pop the smallest-distance node. If it is already finished, skip it — it is a stale
leftover from an earlier, worse path. Otherwise lock it in at that distance and
offer its neighbors `(dist + link_weight, neighbor)` back to the heap. The answer
is the largest locked-in distance. If fewer than `n` nodes got locked in, one is
unreachable, so return -1.

## Complexity

- **Time: about E·log V.** Every link can push a neighbor once, and each heap
  push or pop is about `log V` steps. Roughly, more links means proportionally
  more work with a small log factor on top.
- **Extra memory: about V + E.** The neighbor lists plus the heap and the
  distance map.

## Pitfalls

- **Nodes are 1-indexed** here (`1..n`), not 0-indexed. Off-by-one bugs are easy.
- Forgetting the **stale-entry skip** (`if node in dist: continue`). Without it
  the heap can re-process a node through a worse path.
- Returning -1 only when the heap empties isn't enough — you must check that
  **all `n`** nodes were reached, not just that you ran out of heap.
- Dijkstra is **wrong with negative links**. If the problem allowed them you'd
  need Bellman-Ford (see the sibling below).

## Transfer

The move "finish the nearest frontier node next, using a heap" is the reusable
core. It comes back in
[Cheapest Flights Within K Stops / 787](../0787-cheapest-flights-within-k-stops/)
(shortest path with a hop limit),
[Swim in Rising Water / 778](../0778-swim-in-rising-water/) (Dijkstra where the
path cost is a max, not a sum), and
[Path With Minimum Effort / 1631](https://leetcode.com/problems/path-with-minimum-effort/).
Whenever you need cheapest-reach on non-negative weights, reach for Dijkstra.
