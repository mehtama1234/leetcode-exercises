# 853. Car Fleet

**Pattern:** Monotonic stack (over arrival times) + sort
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/car-fleet/

## The problem in plain words

Cars are on a one-lane road heading to the same target, each at a fixed start
position and speed. Nobody can pass: a faster car that catches a slower one ahead
just bunches up behind it and they move together from then on. A group moving
together is a **fleet** (one car alone is also a fleet). Count how many separate
fleets arrive at the target.

## Why this matters

The core operation is *"does this item catch the one ahead, or does it start a
new group?"* — decided by comparing a single derived number (time to reach the
target) against the item in front. It's a merging-along-a-line question: order by
position, then coalesce anyone who would overtake into the group ahead.

Concrete places this shows up: traffic and convoy simulation (the literal case);
packet or job pipelining where a fast producer stalls behind a slow one and they
proceed at the bottleneck rate; and any "no-overtake" queue — a single-lane
toll, a conveyor, an ordered event stream where a later-but-faster item can only
catch up, never jump ahead. The count of fleets is the count of independent
bottlenecks.

What the good solution buys is time and clarity. The dominant cost is the
`O(n log n)` sort; after that a single linear stack pass settles every car. You
avoid an `O(n²)` pairwise "who catches whom" simulation by realising each car
only ever interacts with the fleet directly ahead.

## Start from the obvious

Simulate: advance time, move every car, and whenever one reaches another, glue
them and cap the faster one to the slower speed. Correct, but it's a physics loop
— fiddly, and pairwise interactions make it easy to hit `O(n²)`.

Better first thought: since no car can pass, a car's fate depends only on the car
**directly ahead** of it toward the target. So sort by start position and reason
front-to-back.

## The insight

Two cars end in the same fleet exactly when the one behind would reach the target
**no later** than the one ahead — i.e. it catches up before the finish. So:

1. Compute each car's free-running arrival time: `(target - position) / speed`.
2. Sort cars by position, **closest to the target first**.
3. Walk them outward, keeping a stack of the arrival times of fleet *leaders*.

```
cars = sort by position, nearest target first
for pos, spd in cars:
    time = (target - pos) / spd
    if not stack or time > stack[-1]:
        stack.append(time)     # slower -> can't catch up -> NEW fleet leader
    # else time <= stack[-1]   # catches the fleet ahead -> merges, absorbed
return len(stack)
```

Why this is a monotonic stack: the stack holds strictly **increasing** arrival
times from the target outward. A car whose time is `<=` the current leader's is
"dominated" — it catches the fleet ahead and is resolved (popped from
consideration) immediately; only a strictly slower car survives to push a new
leader. Each car is settled in O(1) after the sort, and the number of pushes is
the number of fleets.

## Complexity

- **Time:** `O(n log n)` — the sort dominates; the stack pass is `O(n)`.
- **Space:** `O(n)` — the sorted pairs and the stack of leader times.

## Pitfalls

- **Sort direction.** Process nearest-to-target first. Sorting the wrong way
  breaks the "car ahead governs" logic.
- **`<=` vs `<`.** A car arriving at *exactly* the same time as the leader ahead
  still merges (they meet at the target), so merge on `time <= leader` and only
  push on strictly greater.
- Use real division (float) for times, or scale carefully; integer division
  silently mis-merges cars.
- Empty input is 0 fleets; a single car is 1.
- The car with the largest arrival time in any suffix is the fleet's true leader
  — the stack tracks exactly those leaders.

## Transfer

This is the monotonic-stack idea applied after a sort: a running "frontier" that
absorbs everything dominated and only grows on a strictly new extreme — the same
skeleton as [Next Greater Element I / 496](../0496-next-greater-element-i/) and
the histogram/rainwater problems, here over derived arrival times. The
"coalesce along a sorted line" move also relates to
[Merge Intervals / 56](../../15-intervals/0056-merge-intervals/). Whenever items
can only merge with a neighbour in sorted order, sort then sweep with a stack.
