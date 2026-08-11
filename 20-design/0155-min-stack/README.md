# 155. Min Stack

**Pattern:** Augmented stack (carry a running answer alongside the data)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/min-stack/

## The problem in plain words

Build a stack with the usual `push`, `pop`, and `top`, plus one extra:
`getMin()` returns the smallest value currently in the stack. All four operations
must take the same tiny amount of time, no matter how tall the stack gets.

```diagram
   push -2      push 0       push -3
   [ -2 ]       [  0 ]       [ -3 ]  <- top
                [ -2 ]       [  0 ]
                             [ -2 ]

   getMin() must say -3 here, without looking through the pile.
```

## Why this matters

The lesson is a general trick: *when a query over a structure is slow to compute
from scratch, keep the answer up to date as the structure changes instead.* Rather
than recompute the minimum on demand, you carry it forward on every push and
unwind it on every pop.

This shows up whenever a system needs a cheap summary of a changing stack or
window. Undo/redo stacks that report a running total, streaming metrics tracking a
rolling minimum or maximum, and expression evaluators that hold extra state per
frame all use it. The same "keep a companion stack of partial answers" idea drives
monotonic-stack problems like the largest rectangle in a histogram.

What the good solution buys is skipping a costly recompute: `getMin` never scans.
You pay a tiny, fixed bit of bookkeeping on each push and pop so the query is
free — turning what could be a slow-per-call hotspot into a single read.

## Start from the obvious

Keep one normal stack. For `getMin`, walk the whole thing and return the smallest.

```diagram
   stack = [ -2, 0, -3, 5, -1 ]
             ^    ^   ^   ^   ^
             look at every element, track the smallest  -> -3

   n elements means n steps, every single time getMin is called.
```

Correct, but `getMin` costs a full pass. If a caller asks for the minimum after
every push — common in the problems this pattern feeds — the whole thing balloons
to about n-squared work.

## Find the waste

Scanning re-derives something you already knew a moment ago. Before the latest
push, you already knew the minimum of everything below. Pushing `x` can only change
the minimum to `min(x, old_min)` — one comparison. The scan throws that away and
rebuilds it from nothing on every query.

So *remember* it. At every level, store the minimum of the stack up to and
including that level.

## The insight

Keep a second, parallel stack `mins`. When you push `x`, push `min(x, mins[-1])`
onto `mins` (or just `x` if `mins` is empty). When you pop the value stack, pop
`mins` in the same beat. Now `mins[-1]` is always the current minimum.

```diagram
   op        stack           mins            getMin
   push -2   [-2]            [-2]            -2
   push 0    [-2, 0]         [-2, -2]        -2   (min(0,-2) = -2)
   push -3   [-2, 0, -3]     [-2, -2, -3]    -3   (min(-3,-2) = -3)
   pop       [-2, 0]         [-2, -2]        -2   (top of mins is the answer)

   Each level in `mins` remembers the smallest at or below it,
   so the current minimum is always sitting on top -- no search.
```

## Complexity

- **Time: constant per operation.** Push and pop do a fixed bit of extra work;
  `getMin` and `top` are direct reads of the top slot.
- **Space: about n.** The `mins` stack mirrors the value stack. (A common
  space-saver stores only *strictly decreasing* minimums, at the cost of slightly
  trickier pop logic.)

## Pitfalls

- Storing only the single global minimum in one variable. When you pop it, you have
  no idea what the *next* minimum is — you'd have to scan. The per-level companion
  stack is what avoids this.
- Duplicate minimums. If two equal minimums are pushed, popping one must leave the
  other as the min. Pushing `min(x, prev)` each time handles this on its own.
- Forgetting to pop `mins` in lockstep with the value stack.

## Transfer

The core idea — **augment a stack with a companion stack of partial answers** —
reaches past minimums. See
[Implement Queue using Stacks / 232](../0232-implement-queue-using-stacks/) for the
sibling "compose a structure out of stacks," and the monotonic-stack family:
[Daily Temperatures / 739](https://leetcode.com/problems/daily-temperatures/),
[Largest Rectangle in Histogram / 84](https://leetcode.com/problems/largest-rectangle-in-histogram/).
