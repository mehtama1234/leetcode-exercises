# 496. Next Greater Element I

**Pattern:** Monotonic stack (keep a to-do list of values still waiting for a bigger one)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/next-greater-element-i/

## The problem in plain words

You get a long list `nums2` of distinct numbers, and a short list `nums1` whose
values all appear somewhere in `nums2`. For each value in `nums1`, find where it
sits in `nums2` and report the **first number to its right that is bigger**. If
nothing to the right beats it, the answer is `-1`.

```diagram
   nums1 = [4, 1, 2]        nums2 = [1, 3, 4, 2]

   4 sits here:  1  3 [4] 2      look right: 2   nothing bigger -> -1
   1 sits here: [1] 3  4  2      look right: 3   bigger! -> 3
   2 sits here:  1  3  4 [2]     look right: (end) -> -1

   answer = [-1, 3, -1]
```

## Why this matters

Strip the two-list wrapping away and one question is left: *for every position,
who is the next thing to its right that beats it?* That's a fixed fact about each
spot in `nums2` — it doesn't depend on which questions `nums1` happens to ask.

That "next bigger thing downstream" question runs real systems. In a price series,
the next day the price tops today's bounds how long a dip lasts. In monitoring, the
next event that crosses a threshold after each event marks a recovery. Compilers
lean on the same shape: a stack holds operators still waiting for something with
higher precedence to their right.

What the good version buys you: instead of hunting the answer separately for every
question, you compute it once for **every** value in `nums2`, then answer each
question with a single glance at a lookup table.

## Start from the obvious

Do exactly what the problem says. Find the value in `nums2`, then walk rightward
until you hit something bigger.

```diagram
   for each x in nums1:
       find x in nums2, then scan right for the first bigger value

   x=1:  [1] 3 4 2   ->  3      (scanned 1 step)
   x=2:   1 3 4 [2]  ->  -1     (scanned to the end)
          ^ every query re-walks nums2 from its own spot
```

This works. But each question re-scans `nums2` on its own, and neighboring
questions redo almost the same walk. With `m` values in `nums2` and `n` questions,
that's about `n × m` steps — the waste is re-scanning the same stretch again and
again.

## Find the waste

Here's the fact the slow version keeps ignoring: the next-greater answer for a
position in `nums2` never changes. It's decided the moment you look at `nums2`,
long before any question is asked. So compute it **once for every element of
`nums2`**, store it, and every question becomes a one-step lookup.

The trick is doing all `m` of those answers in a single pass instead of `m`
separate scans.

## The insight

Sweep `nums2` left to right, holding a stack of values that are still **waiting**
for their next bigger number. The stack's values strictly decrease from bottom to
top. When the current value `x` is bigger than the top of the stack, `x` is exactly
the next-greater number that the top was waiting for: pop it and record the pair.

Anything left on the stack at the end never found a bigger number, so it's `-1`.

```diagram
   nums2 = [1, 3, 4, 2]      stack holds "still waiting" values (top on right)

   x=1:  stack empty            push 1        stack: [1]
   x=3:  3 > 1  -> 1's answer is 3, pop 1     stack: []
                  push 3                       stack: [3]
   x=4:  4 > 3  -> 3's answer is 4, pop 3     stack: []
                  push 4                       stack: [4]
   x=2:  2 < 4  -> nobody waiting is smaller  push 2   stack: [4, 2]

   leftovers 4 and 2 never got beaten -> answer -1
   resolved map: {1:3, 3:4}
```

Why the stack stays small and the whole sweep stays fast: a value sits on the stack
only while nothing bigger has come along. The first bigger value resolves it and
pops it — for good. Each value is pushed once and popped at most once, so the total
work grows in step with the list, about `m` steps.

Because `nums2` has no repeats, one map from value to its next-greater answer serves
every `nums1` question in a single step.

## Complexity

- **Time: about n + m steps.** One pass over `nums2` builds the map; one pass over
  `nums1` reads it. (The brute force is about `n × m`.)
- **Extra memory: about m.** The map and the stack.

## Pitfalls

- `<` vs `<=` in the pop test: values are distinct here so it doesn't bite, but with
  duplicates the strictness decides whether equal values resolve each other.
- Forgetting the `-1` default for values that never get popped.
- `nums2.index(x)` inside the brute force is itself a full scan — part of why it's
  slow.
- Assuming `nums1` is a contiguous chunk of `nums2`; it's only a *subset of values*,
  which is exactly why "precompute once, then look up" is the clean shape.

## Transfer

The reusable move: **sweep once, keep a stack of items still waiting for a bigger
one, and resolve each item the moment its bigger neighbor appears.** The same stack,
reworded, drives
[Next Greater Element II / 503](https://leetcode.com/problems/next-greater-element-ii/)
(circular array), [Daily Temperatures / 739](https://leetcode.com/problems/daily-temperatures/)
(distance to the next warmer day), and
[Online Stock Span / 901](../0901-online-stock-span/) (nearest bigger to the *left*,
on a stream). The histogram and rainwater problems are the "nearest smaller" mirror.
Whenever you need "the next bigger/smaller thing for everyone," reach for a monotonic
stack.
