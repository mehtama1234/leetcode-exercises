# 84. Largest Rectangle in Histogram

**Pattern:** Monotonic stack (increasing) — find each bar's nearest shorter neighbor
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/largest-rectangle-in-histogram/

## The problem in plain words

You have a row of bars, all the same width but different heights — a bar chart. Draw
the biggest solid rectangle that stays entirely under the skyline. It can span
several bars, but its height can only be as tall as the shortest bar it covers.
Return that maximum area.

```diagram
   heights = [2, 1, 5, 6, 2, 3]

           6
       5 [ # ]
     [ # | # ]           the boxed region is bars 5 and 6, height 5, width 2
     [ # | # ]     3     area = 5 * 2 = 10  <- the answer
   2 [ # | # ]  2  #
   # | # | # ]  #  #
   0   1   2    3  4  5   (bar index)
```

## Why this matters

Underneath is one operation: *for each bar, how far can it stretch sideways before a
shorter bar stops it?* A bar's rectangle is capped by the nearest bar shorter than it
on each side. Name that question and it shows up everywhere. A monotonic stack answers
it for every bar in one pass, instead of re-scanning outward from each bar.

Concrete places this shows up: layout and packing engines fitting the largest free
block into a region; capacity planning, where a pipeline's throughput is capped by its
slowest stage and you want the widest run that sustains a rate; range-minimum queries,
where "how far does this value stay the minimum?" bounds a segment. The same
nearest-shorter-bar skeleton also drives stock spans and rainwater.

What the good solution buys: it turns "expand outward from every bar" into a single
linear pass by resolving each bar exactly once — at the precise moment a shorter bar
proves it can grow no wider.

## Start from the obvious

A rectangle is pinned by its **shortest** bar. So make every bar the shortest one in
turn and see how wide a rectangle of that exact height can grow: walk left and right
while neighbors stay at least as tall.

```diagram
   heights = [2, 1, 5, 6, 2, 3]

   bar 2 (height 5): expand while neighbors >= 5
        left: bar 1 is 1 -> stop.   right: bar 3 is 6 -> ok, bar 4 is 2 -> stop
        width = bars {2,3} = 2,  area = 5 * 2 = 10
   ...repeat for every bar, each re-walking its neighborhood
```

Correct, and the honest first thought. But every bar re-walks its surroundings, and
neighboring bars re-walk almost the same ground — about `n × n` steps.

## Find the waste

The expand loops keep asking the same thing: *where is the first bar strictly shorter
than me, on my left and on my right?* Those two boundaries are all that decide a bar's
rectangle — the height is fixed, and the width is exactly the gap between the nearest
shorter bars on each side. We recompute those boundaries from scratch for every bar,
even though the work overlaps heavily.

## The insight

Keep a stack of bar indices whose **heights strictly increase** from bottom to top.
Walk left to right. When the current bar is shorter than the bar on top of the stack,
that top bar has just met its first shorter bar on the **right** (the current index).
Pop it and resolve it: after popping, the new top is its first shorter bar on the
**left**. The width is everything strictly between those two boundaries.

```diagram
   heights = [2, 1, 5, 6, 2, 3] then a sentinel 0 to flush the stack
   stack holds indices, heights increasing bottom -> top

   i=0 h=2:  push 0                          stack:[0]         (h: 2)
   i=1 h=1:  1 < 2 -> pop 0, left=none, width=1, area=2*1=2
             push 1                          stack:[1]         (h: 1)
   i=2 h=5:  push 2                          stack:[1,2]       (h: 1,5)
   i=3 h=6:  push 3                          stack:[1,2,3]     (h: 1,5,6)
   i=4 h=2:  2<6 pop 3, left=2, width=4-2-1=1, area=6*1=6
             2<5 pop 2, left=1, width=4-1-1=2, area=5*2=10  <-- best
             push 4                          stack:[1,4]       (h: 1,2)
   i=5 h=3:  push 5                          stack:[1,4,5]     (h: 1,2,3)
   i=6 h=0:  0<3 pop 5 area=3*1=3 | 0<2 pop 4 area=2*4=8 | 0<1 pop 1 area=1*6=6
                                                                best stays 10
```

Why keeping the stack increasing makes this one pass: the *moment* a bar gets popped
is exactly the moment both its boundaries are known — the shorter bar on the right is
the current index, the shorter bar on the left is the new stack top. Each bar is
pushed once and popped once, about `2n` operations total, so the nested-looking loop
is actually linear. Each pop resolves one bar's largest rectangle for good.

## Complexity

- **Time:** about `n` steps — every index is pushed once and popped once; the
  sentinel guarantees the stack empties.
- **Extra memory:** about `n` — the stack can hold every bar (a strictly increasing
  input).

## Pitfalls

- Forgetting the trailing sentinel of height 0: bars left on the stack at the end
  never get resolved and you undercount.
- Off-by-one in the width. It's `i - stack[-1] - 1` because both boundaries are
  *exclusive* — they're the first shorter bars, not part of the rectangle.
- `>` vs `>=` in the pop test is fine for correctness here, but be deliberate: with
  strict `>`, equal bars stay stacked and the widest one resolves them all together.
- Use `-1` as the "no left boundary" marker so the width math stays uniform.

## Transfer

This is the **nearest-shorter-bar** skeleton: a monotonic stack that resolves each bar
when its blocking neighbor appears. Siblings that reuse it:
[Trapping Rain Water / 42](../0042-trapping-rain-water/) (nearest *taller* on both
sides), [Online Stock Span / 901](../0901-online-stock-span/) (nearest bigger to the
left), [Next Greater Element I / 496](../0496-next-greater-element-i/). Whenever a
brute force expands outward from every element, ask whether a monotonic stack can hand
you the boundary the instant it exists.
