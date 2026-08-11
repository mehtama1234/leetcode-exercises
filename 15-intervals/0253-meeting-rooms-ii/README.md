# 253. Meeting Rooms II

**Pattern:** Intervals → peak concurrency (min-heap or sweep line)
**Difficulty:** Medium (LeetCode premium)
**Link:** https://leetcode.com/problems/meeting-rooms-ii/

## The problem in plain words

You have a pile of meetings with start and end times. Two meetings that overlap
in time need separate rooms. What's the fewest rooms that can hold all of them?

Standard signature: `min_meeting_rooms(intervals) -> int`.

## The reframing that unlocks it

The answer is **the largest number of meetings happening at the same moment.**
If at some instant five meetings are all live, you need at least five rooms; and
if the maximum overlap is five, five rooms always suffice (you can always assign
a free room to each new meeting). So the whole problem is: *find the peak
concurrency.*

## Start from the obvious

The literal-minded version: pick every distinct time point, count how many
meetings cover it, take the max.

```
peak = 0
for t in all_relevant_times:
    live = count of meetings with start <= t < end
    peak = max(peak, live)
```

Correct, but re-counting from scratch at each time point is `O(n^2)` (or worse if
times are large). The waste is recomputing the live count when it only ever
changes by one — at a start (+1) or an end (−1).

## The insight — two equivalent solutions

### Sweep line (count the +1/−1 events)

Split each meeting into two events: a **start** that adds a room and an **end**
that frees one. Sort starts and ends separately, then walk them together in time
order. Every start bumps a running counter up; every end bumps it down. The
highest value the counter reaches is the number of rooms.

The tie rule matters: when a start and an end land on the *same* time, process the
**end first**. A meeting ending at time `t` frees its room for one starting at `t`
— they don't really overlap. In code, `starts[i] < ends[j]` (strict) means "only
add a room if the next start is strictly before the next free-up," which frees the
room on ties.

### Min-heap of end times

Process meetings in start order, keeping a min-heap of the end times of currently
busy rooms. For each meeting, if the earliest-freeing room is already done
(`heap top <= this start`), reuse it; otherwise open a new room. The peak heap
size is the answer. This is the same counting, but the heap tells you *which*
room frees up first.

Both are `O(n log n)`; pick whichever reads clearer to you.

## Complexity

- **Time:** `O(n log n)` — sorting the events / meetings dominates.
- **Space:** `O(n)` — the heap or the two sorted event lists.

## Pitfalls

- **Tie handling.** `[1,5]` then `[5,10]` need only **one** room. The end at `5`
  must be processed before the start at `5`. Strict `<` in the sweep, and `<=` in
  the heap's "is the room free?" test, both get this right.
- **Pairing the wrong start with the wrong end.** In the sweep you *decouple*
  starts from ends and sort them independently — you're counting concurrency, not
  matching a start to its own end.
- Returning the heap's final size instead of its peak — with the reuse rule the
  heap never shrinks below peak-and-then-some, but track the max to be safe (the
  heap version here returns final size, which equals the peak because every push
  that isn't a reuse grows it and reuses never shrink it below the max needed).
- Empty input is `0`.

## Transfer

"Turn intervals into +1/−1 events and sweep for the peak" is a workhorse: it
solves car-pooling (capacity over a route), the maximum number of overlapping
ranges, and skyline-style problems. It's the counting cousin of
[Meeting Rooms / 252](../0252-meeting-rooms/) (which only asks *is the peak > 1?*)
and the flip side of [Non-overlapping Intervals / 435](../0435-non-overlapping-intervals/)
(which drops intervals to force peak down to 1).
