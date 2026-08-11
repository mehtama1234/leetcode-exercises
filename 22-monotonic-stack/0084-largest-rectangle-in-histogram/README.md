# 84. Largest Rectangle in Histogram

**Pattern:** Monotonic stack (increasing)
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/largest-rectangle-in-histogram/

## The problem in plain words

You have a row of bars of equal width but different heights — a bar chart. Find
the biggest solid rectangle you can draw that stays entirely under the skyline.
The rectangle can span several bars, but its height can only be as tall as the
shortest bar it covers. Return that maximum area.

## Why this matters

Underneath is one operation: *for each element, find how far it can stretch
before something smaller stops it — its nearest smaller neighbour on each side.*
That "how far until I'm blocked" question is everywhere once you name it. A
monotonic stack answers it for every element in a single pass instead of
re-scanning outward from each one.

Concrete places this shows up: skyline and layout engines packing the largest
free block into a region; capacity planning, where the throughput of a pipeline
stage is capped by its slowest step and you want the widest run that sustains a
given rate; and range-min structures in query engines, where "how far does this
value stay the minimum?" bounds a segment. The same nearest-smaller-element
skeleton also drives stock spans and rainwater trapping.

What the good solution buys is time: it turns an O(n²) "expand from every bar"
into O(n) by resolving each bar exactly once — at the precise moment a shorter
bar proves it can grow no further. For a histogram with millions of bars that's
the difference between instant and stalled.

## Start from the obvious

A rectangle is pinned by its **shortest** bar. So make every bar the shortest
one in turn, and see how wide a rectangle of that exact height can grow: walk
left and right while neighbours stay at least as tall.

```
for each bar i:
    expand left  while heights[left-1]  >= heights[i]
    expand right while heights[right+1] >= heights[i]
    area = heights[i] * (right - left + 1)
best = max area over all i
```

Correct, and the honest first thought. But it's `O(n^2)`: every bar re-walks its
neighbourhood, and adjacent bars re-walk almost the same ground.

## Find the waste

The expand loops keep asking the same thing: *where is the first bar strictly
shorter than me, to my left and to my right?* Those two boundaries are all that
decide a bar's rectangle — the height is fixed, the width is exactly the gap
between the nearest shorter bars on each side. We recompute those boundaries from
scratch for every bar even though the work overlaps massively.

## The insight

Keep a stack of bar indices whose **heights strictly increase** from bottom to
top. Walk left to right:

- While the current bar is shorter than the bar on top of the stack, that top bar
  has just met its first shorter bar on the **right** (the current index). Pop it
  and *resolve* it: after popping, the new top is its first shorter bar on the
  **left**. The width is everything strictly between those two boundaries, so
  `width = i - new_top - 1` (or `i` if the stack is now empty).
- Then push the current index.

```
for i, h in enumerate(heights + [0]):   # 0 sentinel flushes the stack
    while stack and heights[stack[-1]] > h:
        top = stack.pop()
        left = stack[-1] if stack else -1
        best = max(best, heights[top] * (i - left - 1))
    stack.append(i)
```

Why monotonic gives O(n): keeping the stack increasing means the *moment* a bar
gets popped is exactly the moment both its boundaries are known. Each bar is
pushed once and popped once — `2n` operations total — so the nested-looking loop
is linear. Each pop "resolves" one bar's largest rectangle for good.

## Complexity

- **Time:** `O(n)` — every index is pushed once and popped once; the sentinel
  guarantees the stack empties.
- **Space:** `O(n)` — the stack can hold every bar (a strictly increasing input).

## Pitfalls

- Forgetting the trailing sentinel (height 0): bars left on the stack at the end
  never get resolved and you undercount.
- Off-by-one in the width. It's `i - stack[-1] - 1` because both boundaries are
  *exclusive* — they're the first shorter bars, not part of the rectangle.
- Using `>=` instead of `>` in the pop test is fine for correctness here (equal
  heights get resolved later against the same-height run), but be deliberate:
  with strict `>`, equal bars stay stacked and the widest one resolves them all.
- Using `-1` as the "no left boundary" marker so the width math stays uniform.

## Transfer

This is the **nearest-smaller-element** skeleton: a monotonic stack that resolves
each element when its blocking neighbour appears. Siblings that reuse it:
[Trapping Rain Water / 42](../0042-trapping-rain-water/) (nearest *taller* on both
sides), [Online Stock Span / 901](../0901-online-stock-span/) (nearest greater to
the left), [Next Greater Element I / 496](../0496-next-greater-element-i/).
Whenever a brute force expands outward from every element, ask whether a
monotonic stack can hand you the boundary the instant it exists.
