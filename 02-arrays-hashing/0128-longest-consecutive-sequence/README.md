# 128. Longest Consecutive Sequence

**Pattern:** Hashing (fast presence test + start each run only from its beginning)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/longest-consecutive-sequence/

## The problem in plain words

You have a jumbled bag of integers. Ignoring their positions, what's the longest
chain that steps up by exactly one — like `3,4,5,6` — that you can pull out?
Return the chain's length. The catch: it has to run in about n steps.

```diagram
   nums = [100, 4, 200, 1, 3, 2]

   pull out the chain:  1 -> 2 -> 3 -> 4        length 4
   100 and 200 stand alone                      -> answer: 4
```

## Why this matters

Two moves hide here. First, testing "is `x+1` also in my bag?" in one step,
without paying to sort. Second, measuring each chain exactly once — by starting a
count only at a chain's true beginning, never re-walking a chain you've already
counted from partway in.

Both show up in real work. Finding the longest unbroken run comes up in storage
and networking: merging free disk blocks or memory pages into the largest runs,
joining adjacent address ranges or version numbers, collapsing timestamps into
unbroken stretches. The "handle each connected piece once, from its edge" idea is
how flood-fill and region labeling work in image processing and in grid or maze
code — you start a region only at a cell that begins one.

What you're solving for is staying at about n steps when sorting would drag you to
n log n. You trade a hash set (extra memory) for order, and count only where
nothing extends downward.

## Start from the obvious

Sort the numbers and consecutive ones line up as neighbors; then one walk counts
the longest run of `+1` steps.

```diagram
   sorted(set(nums)) = [1, 2, 3, 4, 100, 200]

   1->2->3->4   run of 4
   4  100       gap, reset
   100 200      gap, reset
   longest = 4
```

Correct and easy to reason about — but sorting is about n log n, and the problem
demands about n. So the sort has to go.

## Find the waste

Sorting puts *every* value in a total order, but you don't need to know how all
the numbers relate. You only need to trace chains upward by ones — a series of "is
`x+1` here?" questions, and a set answers each in one step with no ordering.

But done carelessly, "for each `x`, walk `x, x+1, x+2, …`" re-walks the same chain
over and over.

```diagram
   present = {1,2,3,4}

   start at 3:  3->4              (walked 3,4)
   start at 2:  2->3->4           (walked 3,4 AGAIN)
   start at 1:  1->2->3->4        (walked 3,4 AGAIN)
                ^ the same tail counted three times = wasted work
```

That repeated walking is what would make the set approach about n × n.

## The insight

Walk each chain **only once**, by counting only from a chain's true beginning. A
value `x` begins a chain exactly when `x - 1` is **not** in the set — nothing
extends it downward. From those starts, walk forward while `x+1, x+2, …` exist and
measure the length.

```diagram
   present = {1,2,3,4}

   x=1:  is 0 present? no  -> START.  walk 1,2,3,4       length 4  (best)
   x=2:  is 1 present? yes -> skip (2 is inside a run)
   x=3:  is 2 present? yes -> skip
   x=4:  is 3 present? yes -> skip
                          ^ only the real start does any walking
```

Because the forward walk only ever runs from a start, each value is stepped over
by it at most once across the whole run of the algorithm. That's what keeps the
total at about n steps.

## Complexity

- **Time: about n steps.** Building the set is about n; the `x-1` guard means
  every value is stepped over by the inner walk at most once in total.
- **Extra memory: about n.** The set holds every distinct value.

## Pitfalls

- **The whole trick is the "skip if `x-1` is present" guard.** Without it you
  re-walk chains and quietly drop to about n × n.
- Put values in a **set**, not a list — the "is it present?" test must be one
  step, or the whole bound collapses.
- Duplicates must not inflate the count; the set drops them automatically.
- Empty input returns `0`; a single element returns `1`.

## Transfer

Two reusable ideas: **dump into a set for one-step presence tests**, and **anchor
work at the unique start of a structure so you do it once** (here, "no smaller
neighbor" marks a start). The set-membership half is the same tool from
[Contains Duplicate / 217](../0217-contains-duplicate/) and
[Two Sum / 1](../0001-two-sum/); the "count each connected piece once from its
edge" idea reappears in grid and island problems.
