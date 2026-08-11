# 787. Cheapest Flights Within K Stops

**Pattern:** Shortest path with a hop limit (Bellman-Ford in rounds)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/cheapest-flights-within-k-stops/

## The problem in plain words

You have cities and priced flights between them. Find the cheapest total price to
fly from `src` to `dst` — but you may make at most `k` stops along the way (so at
most `k+1` flights). If no route fits that limit, return -1.

The twist that trips people up: the *cheapest* route and the *fewest-flights*
route are often different. A dirt-cheap price might need five hops; a two-hop
route might cost more. You have to make the price as low as possible **while
staying inside** the hop budget.

```diagram
   0 --100--> 1 --100--> 2 --100--> 0    (loop back)
                         |
   1 --600--> 3          200
                         v
                         3

   goal: 0 -> 3,  at most k=1 stop (so <= 2 flights)

   0->1->3   = 100 + 600 = 700   uses 1 stop   OK
   0->1->2->3= 100+100+200=400   uses 2 stops  too many, forbidden

   cheaper route exists but breaks the budget  ->  answer = 700
```

## Why this matters

The deeper operation is *shortest path under a limit on how many steps you take* —
not just "cheapest," but "cheapest using no more than N steps." That extra
dimension changes everything, because the greedy "finish the nearest node" trick
Dijkstra leans on breaks. A node reached cheaply might have burned your whole hop
budget getting there, so that cheap price isn't actually usable.

Real systems hit this constantly. Flight and logistics pricing engines cap
layovers or transfers. Network routing bounds the number of hops a packet may take
(the TTL field) to stop loops and control delay. Any "cheapest plan with a limit
on the number of moves" — supply chains with a max number of handoffs, currency
conversion chains with a trade limit — is this exact shape.

What the good solution buys is a clean way to fold the step-limit into the
algorithm's *structure* instead of tracking it as extra state. Bellman-Ford
relaxes links in rounds, and "round number" **is** "flights used." So bounding
hops is just: stop after `k+1` rounds. Time is about `k·E` — small and
predictable.

## Start from the obvious

The honest first thought: reach for Dijkstra, since we're minimizing price over
non-negative prices.

```diagram
   dijkstra from src, always pop the cheapest-so-far city
```

But plain Dijkstra locks in a city the moment it is reached cheapest — with no
memory of *how many flights* that took. It may fix a cheap price that used too
many hops, and turn away a pricier route that would have fit the budget. The hop
limit is invisible to it. You'd have to carry hop-count as extra state, and then
you can no longer finish each city just once.

## The insight

Bellman-Ford already thinks in the right unit. It works in **rounds**: each round
relaxes every link once. The key fact:

> After round `i`, `dist[city]` = cheapest price to reach `city` using **at most
> `i` flights**.

So the hop limit isn't a special case — it is just how many rounds you run. At
most `k` stops means at most `k+1` flights, so run exactly `k+1` rounds.

```diagram
   flights: 0->1 (100)  1->2 (100)  0->2 (500)
   src=0  dst=2  k=1  ->  run 2 rounds.   INF = infinity

   start        dist = [ 0, INF, INF ]

   round 1  (<=1 flight)   read from the frozen start:
       0->1: 0+100 = 100  <  INF   set curr[1]=100
       0->2: 0+500 = 500  <  INF   set curr[2]=500
       1->2: 1 is INF at start     no change
                            dist = [ 0, 100, 500 ]

   round 2  (<=2 flights)  read from round-1's frozen dist:
       1->2: 100+100 = 200  <  500  set curr[2]=200
                            dist = [ 0, 100, 200 ]

   dist[2] = 200   (the 0->1->2 route, exactly 2 flights)
```

The **frozen snapshot** each round is the load-bearing detail. If you relaxed into
`dist` in place, a price could chain across two links *within one round*, sneaking
in an extra flight and quietly breaking the hop limit. Reading from the previous
round's frozen `dist` guarantees exactly one new flight per round.

```diagram
   why the snapshot matters (in-place would be WRONG):

   round 1, if we wrote into the SAME array left-to-right:
       0->1 sets dist[1]=100
       1->2 then reads the FRESH dist[1]=100  ->  dist[2]=200
   that used TWO flights inside "round 1" — the budget is now a lie.

   reading from a frozen copy blocks that chain: one flight per round.
```

## Complexity

- **Time: about k·E.** `k+1` rounds, each scanning all `E` flights once. Double
  the hop budget and you roughly double the work.
- **Extra memory: about V.** Two distance arrays of size `n` (`dist` and its
  snapshot).

## Pitfalls

- **k stops = k+1 flights.** Run `k+1` rounds, not `k`. Off-by-one here is the
  classic bug.
- **The snapshot copy is mandatory.** Relaxing in place lets a route take extra
  hops in a single round and corrupts the answer.
- Don't reach for plain Dijkstra — it can't respect the hop budget without being
  reworked to carry hop-count, at which point it is no longer the simple version.
- Handle **`src == dst`** (answer 0) and a genuinely unreachable `dst` (-1).

## Transfer

"Relax links in rounds, where round = steps used" is the reusable trick for any
step-bounded shortest path. It is Bellman-Ford, which is also the go-to when links
can be **negative** (Dijkstra fails there). Compare with
[Network Delay Time / 743](../0743-network-delay-time/), the *unbounded* version,
which gets to use Dijkstra's faster heap. A Dijkstra variant that tracks
`(cost, city, stops)` in the heap solves this too — but the round-based version is
easier to reason about.
