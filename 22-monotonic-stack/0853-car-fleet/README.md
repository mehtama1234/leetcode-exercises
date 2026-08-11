# 853. Car Fleet

**Pattern:** Sort, then a monotonic stack over arrival times
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/car-fleet/

## The problem in plain words

Cars share a one-lane road, all heading to the same target. Each has a start
position and a fixed speed. Nobody can pass: a faster car that catches a slower one
ahead just bunches up behind it, and from then on they move together. A group moving
together is a **fleet** (a lone car is also a fleet). Count how many separate fleets
reach the target.

```diagram
   target = 12.  road runs left (far) to right (target).

   pos:  0    3    5      8    10        12=TARGET
         c1   c3   c4     c2   c0        |
   time: 12   3    7      1    1         |   time = (12 - pos)/speed
                                         |
   c0 and c2 both arrive at t=1; the slower cars behind can't beat them.
   Cars settle into 3 fleets.
```

## Why this matters

Strip the traffic story away and the question is: *does this item catch the one
ahead, or start a new group?* — decided by one derived number (time to reach the
target) compared against the item in front. It's a merge-along-a-line problem: order
by position, then fold anyone who would overtake into the group ahead.

Concrete places this shows up: convoy and traffic simulation (the literal case); job
or packet pipelines where a fast producer stalls behind a slow one and they proceed
at the bottleneck's rate; any "no overtaking" queue — a single-lane toll, a conveyor,
an ordered event stream where a later-but-faster item can only catch up, never jump
ahead. The number of fleets is the number of independent bottlenecks.

What the good solution buys: the main cost is the sort; after that a single linear
pass settles every car. You skip an "everyone checks everyone" simulation because
each car only ever interacts with the fleet directly ahead of it.

## Start from the obvious

Simulate the physics: step time forward, move every car, and whenever one reaches
another, glue them together and cap the faster one to the slower speed. Correct, but
it's a fiddly loop, and all those pairwise interactions push toward "everyone checks
everyone" work.

Better first thought: since no car can pass, a car's fate depends only on the car
**directly ahead** toward the target. So sort by position and reason front to back.

## The insight

Two cars end up in the same fleet exactly when the one behind would reach the target
**no later** than the one ahead — it catches up before the finish line. So:

1. Compute each car's free-running arrival time: `(target - position) / speed`.
2. Sort cars by position, **closest to the target first**.
3. Walk them outward, keeping a stack of the arrival times of fleet *leaders*.

A car whose arrival time is greater than the current leader's is slower — it can
never catch up, so it starts a new fleet (push it). Otherwise it catches the fleet
ahead and merges in (absorbed, nothing pushed).

```diagram
   sorted nearest-target-first:  pos=10 t=1 | pos=8 t=1 | pos=5 t=7 | pos=3 t=3 | pos=0 t=12

   stack holds leader arrival times (increasing outward from target)

   t=1 : stack empty       -> push   stack:[1]        new fleet (leader arrives t=1)
   t=1 : 1 <= 1            -> merge  stack:[1]        catches the fleet ahead
   t=7 : 7  > 1            -> push   stack:[1,7]      slower, new fleet
   t=3 : 3 <= 7            -> merge  stack:[1,7]      catches the t=7 fleet
   t=12: 12 > 7            -> push   stack:[1,7,12]   slowest, new fleet

   fleets = stack size = 3
```

Why this is a monotonic stack: the stack holds strictly **increasing** arrival times
from the target outward. A car whose time is `<=` the current leader's is dominated —
it catches the fleet ahead and is resolved right away; only a strictly slower car
survives to push a new leader. Each car is settled in one step after the sort, and
the number of pushes is the number of fleets.

## Complexity

- **Time:** dominated by the sort, about `n log n` (roughly: sorting `n` items). The
  stack pass that follows is linear, about `n` steps.
- **Extra memory:** about `n` — the sorted pairs and the stack of leader times.

## Pitfalls

- **Sort direction.** Process nearest-to-target first. Sorting the other way breaks
  the "car ahead governs" logic.
- **`<=` vs `<`.** A car arriving at *exactly* the same time as the leader ahead still
  merges (they meet at the target). Merge on `time <= leader`, push only on strictly
  greater.
- Use real (float) division for the times, or scale carefully. Integer division
  silently mis-merges cars.
- Empty input is 0 fleets; a single car is 1.
- The largest arrival time in any group toward the back is that fleet's true leader —
  the stack tracks exactly those leaders.

## Transfer

This is the monotonic-stack idea applied *after* a sort: a running frontier that
absorbs everything it dominates and only grows on a strictly new extreme — the same
skeleton as [Next Greater Element I / 496](../0496-next-greater-element-i/) and the
histogram/rainwater problems, here over derived arrival times. The "coalesce along a
sorted line" move also relates to
[Merge Intervals / 56](../../15-intervals/0056-merge-intervals/). Whenever items can
only merge with a neighbor in sorted order, sort first, then sweep with a stack.
