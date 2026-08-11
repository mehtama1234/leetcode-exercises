# 155. Min Stack

**Pattern:** Augmented stack (carry a running answer alongside the data)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/min-stack/

## The problem in plain words

Build a stack with the usual `push`, `pop`, and `top`, plus one extra:
`getMin()` returns the smallest value currently in the stack. All four
operations must run in O(1) time.

## Why this matters

The real lesson here is a general trick: *when a query over a structure is
expensive to compute from scratch, maintain the answer incrementally as the
structure changes.* Instead of recomputing the minimum on demand, you carry it
forward with every push and unwind it with every pop.

This shows up whenever a system needs a "cheap summary" of a changing stack or
window. Undo/redo stacks that must report a running aggregate, streaming metrics
that track a rolling minimum/maximum, and expression evaluators that keep
auxiliary state per frame all use it. The same "keep a companion stack of
partial answers" idea powers monotonic-stack problems like the largest rectangle
in a histogram and stock-span calculations.

What the good solution buys is **avoiding a costly recompute**: `getMin` never
scans. You pay a tiny, constant amount of bookkeeping on each push/pop so that
the query is free, turning a potential O(n)-per-call hotspot into O(1).

## Start from the obvious

Keep one normal stack. For `getMin`, walk it and return the smallest.

```
def getMin(self):
    return min(self.stack)   # O(n) every call
```

Correct, but `getMin` is O(n). If a caller queries the minimum after every push
(common in the problems this pattern feeds), the whole thing becomes O(n^2).

## Find the waste

Scanning re-derives something we already knew a moment ago. Before the latest
push, we already knew the minimum of everything below. Pushing `x` can only
change the minimum to `min(x, old_min)` — a single comparison. We are throwing
that away and rebuilding it from scratch each query.

So *remember* it. At every level, store the minimum of the stack up to that
level.

## The insight

Keep a second, parallel stack `mins`. When you push `x`, push
`min(x, mins[-1])` onto `mins` (or just `x` if empty). When you pop the value
stack, pop `mins` too. Now `mins[-1]` is always the current minimum.

```
push(x):  stack.push(x); mins.push(min(x, mins.top() if mins else x))
pop():    stack.pop();  mins.pop()
getMin(): return mins.top()
```

Every level carries its own answer, so the current minimum is always sitting on
top — no search.

## Complexity

- **Time:** `O(1)` for every operation. Push/pop do a constant amount of extra
  work; `getMin` and `top` are direct reads.
- **Space:** `O(n)` — the `mins` stack mirrors the value stack. (A common
  optimization stores only *strictly decreasing* minimums to save space, at the
  cost of slightly trickier pop logic.)

## Pitfalls

- Storing only the single global minimum in one variable. When you pop it, you
  have no idea what the *next* minimum is — you'd have to scan. The per-level
  companion stack is what avoids this.
- Duplicate minimums. If two equal minimums are pushed, popping one must leave
  the other as the min. Pushing `min(x, prev)` each time handles this naturally.
- Forgetting to pop `mins` in lockstep with the value stack.

## Transfer

The core idea — **augment a stack with a companion stack of partial answers** —
generalizes far beyond minimums. See
[Implement Queue using Stacks / 232](../0232-implement-queue-using-stacks/) for
the sibling "compose a structure out of stacks," and the monotonic-stack family:
[Daily Temperatures / 739](https://leetcode.com/problems/daily-temperatures/),
[Largest Rectangle in Histogram / 84](https://leetcode.com/problems/largest-rectangle-in-histogram/).
