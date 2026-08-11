# 332. Reconstruct Itinerary

**Pattern:** Eulerian path (Hierholzer's algorithm) with lexical tie-breaking
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/reconstruct-itinerary/

## The problem in plain words

You're handed a pile of one-way plane tickets, each a `[from, to]` pair. Arrange
them into a single trip that uses *every ticket exactly once*, starting from
`"JFK"`. It's guaranteed such a trip exists. If several valid trips exist, return
the one that is smallest in alphabetical order when you read the airport codes in
sequence.

So: use every edge once, start at a fixed node, break ties alphabetically.

## Why this matters

Each ticket is a directed edge that must be traversed exactly once. A walk that
covers every edge exactly once is an **Eulerian path** — a classic since Euler's
1736 bridges of Königsberg. This is fundamentally different from the shortest-path
family: you're not minimizing a cost, you're *consuming every edge* while staying
on a single connected walk.

The pattern is the backbone of real routing-and-sequencing work. DNA fragment
assembly stitches overlapping reads by finding an Eulerian path through a de
Bruijn graph — this is how genomes get reconstructed. The "Chinese Postman"
route for mail carriers, snowplows, and street-sweepers is Eulerian routing.
Drawing a figure "without lifting your pen" is the same question.

What Hierholzer's algorithm buys is doing this in **linear time in the number of
edges** (`O(E)`, or `O(E log E)` with lexical ordering) instead of backtracking
over exponentially many ticket arrangements. The subtle payoff is *correctness*:
a naive greedy walk can strand tickets in a dead end, and Hierholzer's
"stuck-then-splice" mechanism provably avoids that.

## Start from the obvious

The naive idea: greedily fly out along the alphabetically-smallest ticket each
time, hoping to use them all.

```
at JFK, always take the smallest next destination, repeat
```

This **fails**. Picking the smallest next hop can march you into a dead-end
airport while unused tickets remain elsewhere — you get stuck partway with
tickets still in hand. The order in which you *finish* edges matters, and pure
forward greed doesn't account for it.

## The insight

Hierholzer's trick: walk forward greedily, but when you get **stuck** (no unused
ticket leaves the current airport), that airport must be an *endpoint* of the
trail from here — so record it and back up. Because airports finalize in the
order you get stuck, they come out **reversed**:

```
push JFK on a stack
while the stack isn't empty:
    look at the top airport
    if it still has an unused outgoing ticket:
        follow the smallest one (push destination)
    else:
        it's a dead end for now — pop it onto the route
answer = route reversed
```

The stuck airport gets appended and we retreat; any airport that still had a
detour gets fully explored *before* it's popped. That's exactly what splices the
side-loops into the right place. For the **lexically smallest** result, store each
airport's destinations in a **min-heap** so "follow the smallest unused ticket" is
one `heappop`. Greedy-smallest + Hierholzer's retreat provably yields the
alphabetically minimal Eulerian path.

## Complexity

- **Time:** `O(E log E)` — every ticket is pushed and popped from a heap once
  (`E` heap ops at `O(log E)`). Without the lexical requirement it'd be `O(E)`.
- **Space:** `O(E)` — the adjacency heaps, the traversal stack, and the route
  all scale with the number of tickets.

## Pitfalls

- **Forgetting to reverse** the collected route — it's built end-to-front.
- Trying **pure forward greedy** and getting stranded — the whole point is the
  stuck-then-prepend step.
- Not enforcing lexical order structurally: sorting once won't stay sorted as
  edges are consumed; a **min-heap per airport** keeps "smallest unused" cheap.
- Assuming the graph is simple — there can be **repeated tickets** (parallel
  edges) and airports visited multiple times; the heap handles duplicates fine.

## Transfer

Hierholzer's "walk, get stuck, splice back in reverse" is the reusable Eulerian
engine. It underlies
[Valid Arrangement of Pairs / 2097](https://leetcode.com/problems/valid-arrangement-of-pairs/)
(the same Eulerian-path reconstruction without the fixed start), de Bruijn
sequence construction, and route-covering ("postman") problems. Whenever the task
is "use every edge exactly once as one connected walk," reach for Hierholzer
rather than backtracking.
