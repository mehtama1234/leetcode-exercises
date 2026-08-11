# 332. Reconstruct Itinerary

**Pattern:** Use every edge once (Hierholzer's algorithm) with alphabetical tie-breaking
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/reconstruct-itinerary/

## The problem in plain words

You're handed a pile of one-way plane tickets, each a `[from, to]` pair. Arrange
them into a single trip that uses *every ticket exactly once*, starting from
`"JFK"`. Such a trip is guaranteed to exist. If several valid trips exist, return
the one that reads smallest in alphabetical order when you list the airport codes
in order.

So: use every ticket once, start at a fixed airport, break ties alphabetically.

```diagram
   tickets:  JFK->MUC   MUC->LHR   LHR->SFO   SFO->SJC

   JFK -> MUC -> LHR -> SFO -> SJC

   every ticket used exactly once, one connected trip
```

## Why this matters

Each ticket is a one-way link that must be used exactly once. A walk that covers
every link exactly once is an **Eulerian path** — a walk that uses each edge once —
a classic since Euler's 1736 bridges of Königsberg. This is a different family from
shortest-path problems: you are not minimizing a cost, you are *consuming every
link* while staying on one connected walk.

The pattern is the backbone of real routing-and-sequencing work. DNA assembly
stitches overlapping reads by finding an Eulerian path through a graph of
fragments — this is how genomes get pieced back together. The "Chinese Postman"
route for mail carriers, snowplows, and street-sweepers is this. Drawing a figure
"without lifting your pen" is the same question.

What Hierholzer's algorithm buys is doing this in **linear time in the number of
tickets** (about `E` steps, or `E·log E` with the alphabetical ordering) instead
of backtracking over a huge number of ticket arrangements. The subtle payoff is
*correctness*: a naive greedy walk can strand tickets in a dead end, and
Hierholzer's "get stuck, then splice" step provably avoids that.

## Start from the obvious

The naive idea: greedily fly out along the alphabetically-smallest ticket each
time, hoping to use them all.

```diagram
   at JFK -> take smallest next hop -> repeat, and hope
```

This **fails**. Picking the smallest next hop can march you into a dead-end airport
while unused tickets sit elsewhere — you get stuck partway with tickets still in
hand. Watch it break:

```diagram
   tickets:  JFK->A   JFK->B   A->JFK

   greedy takes JFK->A (A < B),  then A->JFK,  then JFK->B ... land at B.
   trip: JFK -> A -> JFK -> B    all 3 tickets used — this one happens to work.

   but reorder the choice:  if greedy took JFK->B first (dead end at B),
   it strands A->JFK and JFK->A.  the ORDER you finish tickets matters,
   and pure forward greed can't see it coming.
```

## The insight

Hierholzer's trick: walk forward greedily, but when you get **stuck** (no unused
ticket leaves the airport you're on), that airport must be an *end point* of the
trail from here — so record it and back up. Because airports get finalized in the
order you get stuck, they come out **reversed**, and any side-loop you finished
earlier lands in exactly the right place.

```diagram
   tickets:  JFK->A   JFK->B   A->JFK        smallest-first per airport

   stack           route (finalized)      note
   [JFK]           []                     start
   [JFK,A]         []                     JFK: take A (smallest)
   [JFK,A,JFK]     []                     A: only ticket -> JFK
   [JFK,A,JFK,B]   []                     JFK: only B left -> B
   [JFK,A,JFK]     [B]                     B stuck -> pop to route
   [JFK,A]         [B,JFK]                 JFK empty now -> pop
   [JFK]           [B,JFK,A]               A empty -> pop
   []              [B,JFK,A,JFK]           JFK empty -> pop

   reverse route:  JFK -> A -> JFK -> B    <- the answer
```

The stuck airport gets appended and we retreat; any airport that still had a detour
gets fully explored *before* it is popped. That is what splices the side-loops into
the right spot. For the **alphabetically smallest** result, store each airport's
destinations in a **min-heap** (a bucket that always hands you its smallest item)
so "follow the smallest unused ticket" is one pop. Smallest-first plus Hierholzer's
retreat provably gives the alphabetically minimal Eulerian path.

## Complexity

- **Time: about E·log E.** Every ticket is pushed and popped from a heap once
  (`E` heap operations, each about `log E`). Without the alphabetical rule it would
  be about `E`.
- **Extra memory: about E.** The per-airport heaps, the walking stack, and the
  route all grow with the number of tickets.

## Pitfalls

- **Forgetting to reverse** the collected route — it is built end-to-front.
- Trying **pure forward greedy** and getting stranded — the whole point is the
  get-stuck-then-prepend step.
- Not enforcing alphabetical order structurally: sorting once won't stay sorted as
  tickets are consumed; a **min-heap per airport** keeps "smallest unused" cheap.
- Assuming the graph is simple — there can be **repeated tickets** (two identical
  edges) and airports visited many times; the heap handles duplicates fine.

## Transfer

Hierholzer's "walk, get stuck, splice back in reverse" is the reusable engine for
use-every-edge-once problems. It underlies
[Valid Arrangement of Pairs / 2097](https://leetcode.com/problems/valid-arrangement-of-pairs/)
(the same reconstruction without a fixed start), de Bruijn sequence construction,
and route-covering ("postman") problems. Whenever the task is "use every edge
exactly once as one connected walk," reach for Hierholzer rather than backtracking.
