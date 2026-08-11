# 11. Container With Most Water

**Pattern:** Two pointers (start wide, drop the weaker side)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/container-with-most-water/

## The problem in plain words

Each number is the height of a vertical wall. Pick two walls; they hold water
between them. The amount is the **distance between the walls** times the **height
of the shorter wall** — water spills over the lower one. Find the most water any
pair can hold.

```diagram
   height:  1  8  6  2  5  4  8  3  7
            |  |  |  |  |  |  |  |  |
   pick walls at index 1 (h=8) and index 8 (h=7):
            width = 8 - 1 = 7
            height = min(8, 7) = 7
            water = 7 * 7 = 49
```

## Why this matters

The value of a pair depends on the *weaker* of two ends and the *width* between
them. The one reusable move: start as wide as possible, and each step throw away
the end that can never do better — so you never re-check a pair you've already
beaten.

That "the shorter side caps the result, so give it up" logic runs real capacity
problems. The speed of a network path is set by its slowest link — the weak wall.
A load balancer's throughput is set by its tightest resource. Anywhere the answer
is pinned by a bottleneck and you're hunting for the best span, this is the shape.

What the good version buys you is one sweep instead of testing every pair. On a
big input that is the difference between a query that returns and one that stalls.

## Start from the obvious

The problem talks about pairs, so try every pair and keep the best.

```diagram
   for each i:
     for each j after i:
       water = (j - i) * min(height[i], height[j])
       keep the largest
```

Correct, done. But on a list of length n that is about n × n steps — double the
input and the work roughly quadruples. And most of those pairs are hopeless. The
question is: which ones can we skip without checking?

## Find the waste

Two things make water: **width** and the **shorter wall**. Start at the widest
possible container — the leftmost and rightmost walls. From here you can only move
*inward*, so width can only shrink from now on.

So the only way a later pair beats this one is a *taller short wall*. Now look at
the current pair and the shorter of the two walls. If we keep that short wall and
move the taller wall inward:

```diagram
   left=0 (h=1)                          right=8 (h=7)
     |                                     |
     v                                     v
     1   8   6   2   5   4   8   3   7
     ^ the short wall (h=1) caps this pair at width*1

   keep the short wall, move the tall wall in ->
     width goes DOWN, height still capped by that same h=1
     -> strictly worse. no point checking it.
```

So the short wall is done — every container that keeps it is narrower and no
taller. Drop it: move the shorter wall's pointer inward and hope the next wall is
taller.

## The insight

Two pointers at the ends. Measure the water, then move whichever wall is **shorter**
one step inward. Repeat until they meet, remembering the best.

```diagram
   1  8  6  2  5  4  8  3  7      best = 0
   L                       R   water=(8)*min(1,7)=8    L is shorter -> L++   best=8
      L                    R   water=(7)*min(8,7)=49   R is shorter -> R--   best=49
      L                 R      water=(6)*min(8,3)=18   R is shorter -> R--
      L              R         water=(5)*min(8,8)=40   tie -> move either
      L           R            water=(4)*min(8,4)=16   R -> R--
      ... pointers keep closing in ...
   answer: 49
```

Each move drops only containers that can't beat what we've measured, so one inward
sweep is enough. Nothing worth checking is skipped.

## Complexity

- **Time: about n steps.** The two pointers only move inward and meet after n
  moves total.
- **Extra memory: constant.** Two indices and a running best.

## Pitfalls

- **Moving the taller wall** (or always moving one fixed side) can step right past
  the real answer. Move the *shorter* one.
- Height is `min(left, right)`, not the sum or the max — water pours over the lower
  wall.
- Ties (`height[left] == height[right]`): move either side; the pair you'd get by
  keeping one is no taller and strictly narrower.
- Width is `right - left` (indices), not `right - left + 1`.

## Transfer

This is the "start at the widest setup and give up the provably-worse end" flavor
of two pointers — different from the sum-target sweep in
[Two Sum II / 167](../0167-two-sum-ii-input-array-is-sorted/), but the same
converging-pointer skeleton. The transferable habit is *proving why an end can be
dropped*, which also underlies harder greedy-pointer problems like
*Trapping Rain Water / 42*.
