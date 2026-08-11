# 253. Meeting Rooms II

**Pattern:** Intervals to peak concurrency (min-heap or sweep line)
**Difficulty:** Medium (LeetCode premium)
**Link:** https://leetcode.com/problems/meeting-rooms-ii/

## The problem in plain words

You have a pile of meetings with start and end times. Two meetings that overlap in
time need separate rooms. What is the fewest rooms that can hold all of them?

Standard signature: `min_meeting_rooms(intervals) -> int`.

```diagram
   time:  0  5  10 15 20 25 30
   [0,30]  [==================]
   [5,10]     [==]
   [15,20]           [==]
                ^         ^
   at t=5:  [0,30] and [5,10] both live  -> 2 rooms
   at t=15: [0,30] and [15,20] both live -> 2 rooms
   most-at-once = 2  ->  answer 2
```

## Why this matters

The core operation is **peak concurrency**: over a timeline of things that start and
end, what is the most active at once? You get it by turning intervals into +1/-1
events and tracking a running count — a *sweep line*. That number sizes the resource
you must provision.

This is real capacity planning. Cloud and connection-pool sizing asks "what is the
most simultaneous requests?" to decide how many servers to hold. Call centers use
peak concurrent calls to staff lines. Streaming services size for peak concurrent
viewers. Any pooled resource — rooms, machines, GPUs, licenses — comes down to this
peak count.

What you buy is about n·log n and a small running state via the +1/-1 sweep, instead
of re-counting live intervals at every time point. The number it returns is directly
actionable: the minimum resources that guarantee no one waits.

## The reframing that unlocks it

The answer is **the largest number of meetings happening at the same moment.** If at
some instant five meetings are live, you need at least five rooms; and if the most
overlap ever is five, five rooms always suffice (assign a free room to each new
meeting). So the whole problem is: *find the peak concurrency.*

## Start from the obvious

The literal-minded version: pick every distinct time point, count how many meetings
cover it, take the max.

```
peak = 0
for t in all_relevant_times:
    live = count of meetings with start <= t < end
    peak = max(peak, live)
```

Correct, but re-counting from scratch at each time point is about n × n. The waste is
recomputing the live count when it only ever changes by one — at a start (+1) or an
end (-1).

## The insight — two equivalent solutions

### Sweep line (count the +1/-1 events)

Split each meeting into two events: a **start** that takes a room and an **end** that
frees one. Sort starts and ends separately, then walk them together in time order.
Every start bumps a counter up; every end bumps it down. The highest the counter ever
reaches is the number of rooms.

```diagram
   meetings: [0,30] [5,10] [15,20]
   starts:   0   5   15
   ends:     10  20  30

   walk in time order (end wins on a tie):
   t=0   start -> rooms 1   peak 1
   t=5   start -> rooms 2   peak 2   <- [0,30] and [5,10] both live
   t=10  end   -> rooms 1
   t=15  start -> rooms 2   peak 2   <- [0,30] and [15,20] both live
   t=20  end   -> rooms 1
   t=30  end   -> rooms 0
   peak = 2
```

The tie rule matters: when a start and an end land on the *same* time, process the
**end first** — a meeting ending at `t` frees its room for one starting at `t`, so
they do not really overlap. In code, `starts[i] < ends[j]` (strict) frees the room on
ties.

### Min-heap of end times

Process meetings in start order, keeping a min-heap (a pile that always hands back its
smallest value) of the end times of busy rooms. For each meeting, if the
earliest-freeing room is already done (`heap top <= this start`), reuse it; otherwise
open a new room. The peak heap size is the answer.

```diagram
   meetings sorted by start: [0,30] [5,10] [15,20]
   heap holds end times of busy rooms:

   [0,30]  top? empty   -> new room   heap = [30]
   [5,10]  top 30 <= 5? no  -> new room   heap = [10, 30]   <- 2 rooms now
   [15,20] top 10 <= 15? yes -> reuse     heap = [20, 30]
   most rooms ever = 2
```

Both are about n·log n; pick whichever reads clearer.

## Complexity

- **Time: about n·log n** — sorting the events or meetings dominates.
- **Extra memory: about n** — the heap or the two sorted event lists.

## Pitfalls

- **Tie handling.** `[1,5]` then `[5,10]` need only **one** room. The end at `5` must
  be processed before the start at `5`. Strict `<` in the sweep, and `<=` in the
  heap's "is the room free?" test, both get this right.
- **Pairing the wrong start with the wrong end.** In the sweep you *decouple* starts
  from ends and sort them independently — you are counting concurrency, not matching a
  start to its own end.
- **Returning the heap's final size when it might have shrunk.** With the reuse rule
  here the heap grows to the peak and never drops below it, so its final size equals
  the peak; if you ever let rooms drain, track the max explicitly.
- Empty input is `0`.

## Transfer

"Turn intervals into +1/-1 events and sweep for the peak" is a workhorse: it solves
car-pooling (capacity over a route), the maximum number of overlapping ranges, and
skyline-style problems. It is the counting cousin of
[Meeting Rooms / 252](../0252-meeting-rooms/) (which only asks *is the peak > 1?*) and
the flip side of [Non-overlapping Intervals / 435](../0435-non-overlapping-intervals/)
(which drops intervals to force the peak down to 1).
