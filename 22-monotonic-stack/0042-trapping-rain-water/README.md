# 42. Trapping Rain Water

**Pattern:** Monotonic stack (decreasing) / two pointers
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/trapping-rain-water/

## The problem in plain words

The array is a cross-section of terrain: each number is the height of a wall one unit
wide. After rain, water pools in the dips. Water can sit above a spot only up to the
shorter of the two tallest walls flanking it — anything higher spills off the low
side. Count the total trapped water.

```diagram
   height = [0,1,0,2,1,0,1,3,2,1,2,1]

                              #
              #      w  w  w  # #    w  #      w = trapped water
      #  w  # #  w  w  #  #  # # #  # #
   _  #  #  # #  #  #  #  #  # # #  # #
   0  1  0  2  1  0  1  3  2  1  2  1

   total trapped = 6 units of water
```

## Why this matters

The core operation: *for each spot, how high can it hold water before it leaks — set
by the tallest wall on each side?* You're computing, per cell, `min(tallest to the
left, tallest to the right) - height`. That "bounded by the weaker of two flanks"
shape recurs far beyond puzzles.

Concrete places: terrain and flood modeling, where you fill a basin up to its lowest
surrounding ridge; buffer and backpressure analysis, where a queue between two stages
fills only as high as its neighbors permit; container packing on an uneven floor, where
usable volume is capped by the lowest rim. Any "fill a valley until it overflows the
nearest lip" reasoning is this problem.

The payoff is resource. The brute force recomputes both flanking maxima for every cell —
about `n × n` and hopeless on a long profile. The monotonic stack and the two-pointer
method each make one pass: the stack fills water in flat horizontal slabs, resolving a
valley the moment its right wall appears; the two-pointer version does it with a fixed,
tiny amount of extra memory by always advancing the weaker side.

## Start from the obvious

Water above column `i` is `min(tallest left, tallest right) - height[i]` (or 0). So for
each column, scan both directions for the tallest wall.

```diagram
   height = [4, 2, 0, 3, 2, 5]      column i=2 (height 0)

   tallest to its left  = max(4,2,0) = 4
   tallest to its right = max(3,2,5) = 5
   water here = min(4,5) - 0 = 4

   ...but every column rescans the whole array for maxima it mostly already knows
```

Correct and readable. But it's about `n × n`: every column re-scans the entire array
for maxima that barely change.

## Find the waste

Those two flanking maxima shift only slightly as `i` moves by one — yet we recompute
them from scratch each time. Two clean ways to stop repeating the work.

**Precompute the flanks** (the simplest fix): one left-to-right pass filling
`left_max[i]`, one right-to-left pass filling `right_max[i]`, then a final pass summing.
That's already one linear pass each. The monotonic stack is the same idea done in a
*single* sweep, resolving water as walls appear.

## The insight (monotonic stack)

Keep a stack of indices with **non-increasing** heights — a descending wall on the left,
waiting for a taller wall on the right. When the current bar is taller than the stack
top, that top is a **valley floor** that just found its right wall. Pop it and resolve
the slab of water sitting above it: the left wall is the new top, the right wall is the
current bar, and the water depth is the shorter of the two walls minus the floor.

```diagram
   height = [4, 1, 3]    (a simple pit)
   stack holds indices, heights non-increasing bottom -> top

   i=0 h=4:  push 0                    stack:[0]     (walls: 4)
   i=1 h=1:  1 < 4, no pop, push 1     stack:[0,1]   (walls: 4,1)
   i=2 h=3:  3 > 1 -> floor is index 1 (height 1)
             pop 1.  left wall = index 0 (h=4), right wall = index 2 (h=3)
             depth = min(4,3) - 1 = 2
             width = 2 - 0 - 1 = 1
             water += 1 * 2 = 2
             3 < 4, stop.  push 2      stack:[0,2]

   total = 2
```

Why the descending stack makes this one pass: when a taller bar arrives, every floor it
clears has *both* walls known — the left wall is the new top, the right wall is the
current index. Each index is pushed once and popped once. Each pop resolves one flat
layer of trapped water for good.

**Two pointers (tightest on memory).** Walk inward from both ends, tracking `left_max`
and `right_max`. The side with the smaller running max is the binding constraint, so that
column can be settled immediately — its water is fixed by the weaker side, whatever's
still hidden on the other. One pass, constant extra memory.

```diagram
   height = [4, 2, 0, 3, 2, 5]
   L->                          <-R      left_max=4, right_max=5

   left_max(4) <= right_max(5): the LEFT side binds. settle column at L, step L right.
   at h=2: water += 4-2 = 2 | at h=0: water += 4-0 = 4 | at h=3: water += 4-3 = 1 ...
   always advance the weaker wall; its side's max is what caps the water there.
```

## Complexity

- **Brute:** about `n × n` time, tiny extra memory.
- **Stack / precomputed flanks:** about `n` time, about `n` extra memory.
- **Two pointers:** about `n` time, constant extra memory — the winner when memory is
  tight.

## Pitfalls

- Empty input and single bars trap 0 — handle `[]` before touching indices.
- In the stack version, stop the inner loop when the stack empties after a pop: a floor
  with no left wall leaks off the left edge and traps nothing.
- Water is measured in **horizontal slabs** here, not per-column straws; mixing the two
  mental models causes double counting.
- In two pointers, advance the pointer on the side with the **smaller** max and update
  its max *before* adding water, or you count the current bar wrong.

## Transfer

This is the nearest-**taller**-bar cousin of the histogram problem — same monotonic-stack
skeleton, opposite comparison. See
[Largest Rectangle in Histogram / 84](../0084-largest-rectangle-in-histogram/) (nearest
shorter on both sides). The two-pointer "advance the weaker side" trick also drives
[Container With Most Water / 11](../../03-two-pointers/0011-container-with-most-water/).
Whenever a value is capped by "the weaker of two running bests," reach for one of these
two shapes.
