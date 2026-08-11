# 787. Cheapest Flights Within K Stops

**Pattern:** Shortest path with a hop limit (Bellman-Ford in rounds)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/cheapest-flights-within-k-stops/

## The problem in plain words

You have cities and priced flights between them. Find the cheapest total price to
fly from `src` to `dst` — but you're only allowed at most `k` stops along the
way (so at most `k+1` flights). If no route fits that limit, return -1.

The twist that trips people up: the *cheapest* route and the *fewest-flights*
route are often different cities apart. A dirt-cheap price might require five
hops; a two-hop route might cost more. You have to minimize price **subject to**
the hop budget.

## Why this matters

The deeper operation is *shortest path under a constraint on path length* — not
just "cheapest," but "cheapest using no more than N steps." That extra dimension
changes everything, because the greedy "finalize the nearest node" trick that
Dijkstra relies on breaks: a node reached cheaply might have used up your whole
hop budget, so it's not actually usable.

Real systems hit this constantly. Flight and logistics pricing engines cap
layovers or transfers. Network routing bounds the number of hops a packet may
take (TTL) to prevent loops and control latency. Any "cheapest plan with a limit
on the number of moves" — supply chains with a max number of handoffs, currency
conversion chains with a trade limit — is this exact shape.

What the good solution buys is a clean way to fold the step-limit into the
algorithm's *structure* rather than tracking it as extra state. Bellman-Ford
relaxes edges in rounds, and "round number" **is** "flights used." So bounding
hops is just: stop after `k+1` rounds. Time is `O(k·E)` — small and predictable.

## Start from the obvious

The honest first thought: reach for Dijkstra, since we're minimizing price over
non-negative weights.

```
dijkstra from src, pop cheapest node each time
```

But plain Dijkstra finalizes a city the moment it's reached cheapest — with no
memory of *how many flights* that took. It may lock in a cheap price that used
too many hops, and reject a pricier route that would've fit the budget. The hop
limit is invisible to it. You'd have to carry hop-count as extra state, and then
you can no longer finalize each city just once.

## The insight

Bellman-Ford already thinks in the right unit. It works by **rounds**: in each
round it relaxes every edge once. Crucially:

> After round `i`, `dist[city]` = cheapest price to reach `city` using **at most
> `i` flights**.

So the hop limit isn't a special case — it's just how many rounds you run. At
most `k` stops means at most `k+1` flights, so run exactly `k+1` rounds:

```
dist[src] = 0, everything else = infinity
repeat (k+1) times:
    curr = copy of dist            # snapshot — one flight added this round
    for each flight (u, v, price):
        curr[v] = min(curr[v], dist[u] + price)
    dist = curr
answer = dist[dst], or -1 if still infinity
```

The **snapshot copy** is the subtle load-bearing detail. If you relaxed into
`dist` in place, a price could chain across two edges *within one round*,
sneaking in an extra flight and quietly exceeding the hop limit. Reading from
the previous round's frozen `dist` guarantees exactly one new flight per round.

## Complexity

- **Time:** `O(k · E)` — `k+1` rounds, each scanning all `E` flights once.
- **Space:** `O(V)` — two distance arrays of size `n` (`dist` and its snapshot).

## Pitfalls

- **k stops = k+1 flights.** Run `k+1` rounds, not `k`. Off-by-one here is the
  classic bug.
- **The snapshot copy is mandatory.** Relaxing in place lets a route take extra
  hops in a single round and corrupts the answer.
- Don't reach for plain Dijkstra — it can't respect the hop budget without being
  reworked to carry hop-count, at which point it's no longer the simple version.
- Handle **`src == dst`** (answer 0) and genuinely unreachable `dst` (-1).

## Transfer

"Relax edges in rounds, where round = steps used" is the reusable trick for any
step-bounded shortest path. It generalizes Bellman-Ford, which is also the go-to
when edges can be **negative** (Dijkstra fails there). Compare with
[Network Delay Time / 743](../0743-network-delay-time/), which is the *unbounded*
version and so gets to use Dijkstra's faster heap. A Dijkstra variant that tracks
`(cost, city, stops)` in the heap solves this too — but the round-based version
is simpler to reason about.
