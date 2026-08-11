# 42. Trapping Rain Water

**Pattern:** Monotonic stack (decreasing) / two pointers
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/trapping-rain-water/

## The problem in plain words

The array is a cross-section of terrain: each number is the height of a wall one
unit wide. After rain, water pools in the dips. Water can sit above a spot only
up to the shorter of the two tallest walls flanking it — anything higher spills
off the low side. Count the total trapped water.

## Why this matters

The core operation is: *for each position, how high can it be held up before it
leaks — bounded by the tallest barrier on each side?* You're computing, per cell,
`min(best-so-far-from-left, best-so-far-from-right)`. That "bounded by the weaker
of two flanks" shape recurs far beyond puzzles.

Concrete places: terrain and flood modelling in GIS, where you flood-fill basins
up to their lowest surrounding ridge; buffer and backpressure analysis, where a
queue between two stages fills only to the height its neighbours permit; and
container/bin packing on an uneven floor, where usable volume is capped by the
lowest rim. Any "fill a valley until it overflows the nearest lip" reasoning is
this problem.

The payoff is resource. The brute force recomputes both flanking maxima for every
cell — O(n²) and, for a long profile, hopelessly slow. The monotonic stack and
the two-pointer method each make one pass: the stack fills water in horizontal
slabs, resolving a valley the moment its right wall appears; the two-pointer
version does it in O(1) extra space by always advancing the weaker side.

## Start from the obvious

Water above column `i` is `min(tallest left, tallest right) - height[i]` (or 0).
So for each column, scan both directions for the tallest wall:

```
for each i:
    left_max  = max(height[0..i])
    right_max = max(height[i..n-1])
    water += min(left_max, right_max) - height[i]
```

Correct and readable. But it's `O(n^2)`: every column rescans the whole array for
maxima it mostly already knows.

## Find the waste

Those two maxima barely change as `i` moves by one — yet we recompute them from
scratch each time. There are two clean ways to stop repeating the work.

**Precompute the flanks** (the simplest fix): one left-to-right pass filling
`left_max[i]`, one right-to-left pass filling `right_max[i]`, then a final pass
summing. That's already O(n) time / O(n) space. The monotonic stack is the same
idea done in a *single* pass, resolving water as walls appear.

## The insight (monotonic stack)

Keep a stack of indices with **non-increasing** heights — a descending wall on
the left waiting for a taller wall on the right. When the current bar is taller
than the stack top, that top is a **valley floor** that just found its right
wall. Pop it and resolve the slab of water above it:

```
for i, h in enumerate(height):
    while stack and height[stack[-1]] < h:
        bottom = stack.pop()
        if not stack: break            # no left wall -> water spills off
        left  = stack[-1]              # left wall
        width = i - left - 1
        bounded = min(height[left], h) - height[bottom]
        total += width * bounded
    stack.append(i)
```

Why monotonic gives O(n): the descending stack guarantees that when a taller bar
arrives, every floor it clears has *both* walls known — left wall is the new top,
right wall is `i`. Each index is pushed and popped once. Each pop "resolves" one
horizontal layer of trapped water for good.

**Two pointers (tightest).** Walk inward from both ends, tracking `left_max` and
`right_max`. The side with the smaller running max is the binding constraint, so
that column can be settled immediately — its water is fixed by the weaker side,
regardless of what's still hidden on the other. O(n) time, O(1) space.

## Complexity

- **Brute:** O(n²) time, O(1) space.
- **Stack / precomputed flanks:** O(n) time, O(n) space.
- **Two pointers:** O(n) time, O(1) space — the winner when memory is tight.

## Pitfalls

- Empty input and single bars trap 0 — handle `[]` before touching indices.
- In the stack version, `break` when the stack empties after a pop: a floor with
  no left wall leaks off the left edge and traps nothing.
- Water is measured in **horizontal slabs** here, not per-column columns; mixing
  the two mental models causes double counting.
- In two pointers, advance the pointer on the side with the **smaller** max and
  update its max *before* adding water, or you count the current bar wrong.

## Transfer

This is the nearest-**taller**-element cousin of the histogram problem — same
monotonic-stack skeleton, opposite comparison. See
[Largest Rectangle in Histogram / 84](../0084-largest-rectangle-in-histogram/)
(nearest shorter on both sides). The two-pointer "advance the weaker side" trick
also drives [Container With Most Water / 11](../../03-two-pointers/0011-container-with-most-water/).
Whenever a value is capped by "the weaker of two running bests," reach for one of
these two shapes.
