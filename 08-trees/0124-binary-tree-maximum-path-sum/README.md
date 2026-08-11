# 124. Binary Tree Maximum Path Sum

**Pattern:** Tree DFS that returns one thing upward while tracking another on the side
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/binary-tree-maximum-path-sum/

## The problem in plain words

A path is any connected chain of nodes following parent-child links. It can start and
end anywhere and need not touch the root. Add up the values along a path — what is the
biggest total you can get? Values can be negative, which is what makes this tricky.

```diagram
        -10
        /  \          best path here: 15 -> 20 -> 7  = 42
       9   20         (it bends UP the left arm of 20, through 20, DOWN the right)
          /  \        it does not touch -10 or 9 at all
        15    7
```

## Why this matters

The real task is *finding the best path among a huge number of them in a single
bottom-up pass.* The trick is that each node reports one number to its parent — the
best arm it can extend upward — while a running "best so far" separately tracks a
bent path that peaks locally and can't be extended. Keeping "what I contribute upward"
apart from "what I might be the answer" is the reusable idea.

This shape appears well beyond puzzles. Kadane's maximum-subarray is the 1-D version
of the same "best chain ending here vs. best chain anywhere" split, driving
peak-profit and signal-segment detection. Routing analyses find highest-value paths
through a topology. Hierarchical scoring propagates a summary up a tree while
recording the best local structure seen.

What you buy is one pass instead of enumerating every path: by dropping negative arms
and folding results upward once, you never recompute an overlapping sub-path.

## Start from the obvious

Natural first goal: for every node, compute the best path that passes *through* it,
and take the max over all nodes. The right goal — but the hard part is that a path
through a node can **bend**. It can come up the left arm, cross the node, and go back
down the right arm, like an upside-down V.

```diagram
   a path through 20 that bends:

        20            15 --up--> 20 --down--> 7
       /  \           total = 15 + 20 + 7 = 42
     15    7          this is a valid path, but it is NOT a straight line down
```

So "best path through this node" is not a single downward line — which is exactly what
trips people up.

## The insight: two different quantities

Each node is involved in two measurements, and mixing them up is the classic mistake.

1. **The best path that peaks at this node.** It may use *both* children:
   `node.val + best_left_arm + best_right_arm`. This is a real answer candidate — a
   full bent path.
2. **The best this node can hand to its parent.** A parent linking through this node
   can only continue in a straight line, so this node offers itself plus **at most one**
   arm: `node.val + max(left_arm, right_arm)`. You can't hand both arms up — the parent
   would then have a branch, not a path.

The DFS **returns** quantity 2 (the extendable arm) while **updating a running best**
with quantity 1 (the peak). Any arm with a negative total is worthless — better to
take nothing than subtract — so clamp each arm at 0.

```diagram
   gain(20):
     left  = max(gain(15), 0) = 15
     right = max(gain(7),  0) = 7
     peak here = 20 + 15 + 7 = 42     -> update best -> best = 42
     return 20 + max(15, 7) = 35      -> hand only ONE arm to parent -10

   gain(-10):
     left  = max(gain(9), 0)  = 9
     right = max(gain(20),0)  = 35
     peak here = -10 + 9 + 35 = 34    -> best stays 42 (34 < 42)
     return -10 + max(9,35) = 25
```

## Complexity

- **Time: about n steps** — one visit per node, constant work each.
- **Extra memory: about the tree height**, for the recursion stack.

## Pitfalls

- Returning `node.val + left + right` up to the parent — that hands up a bent path the
  parent can't legally use. Return only one arm.
- Starting the running best at 0 — wrong when every value is negative (`[-3]` should
  give `-3`, not 0). Start at negative infinity.
- Forgetting to clamp arms at 0, so a strongly negative subtree drags a good path
  down instead of being skipped.

## Transfer

"Recurse returning a *restricted* value while a side channel tracks the real answer"
is reusable:
[Diameter of Binary Tree / 543](https://leetcode.com/problems/diameter-of-binary-tree/)
(return depth upward, track the longest bent path globally) is the same shape with
lengths instead of sums, and
[Longest Univalue Path / 687](https://leetcode.com/problems/longest-univalue-path/)
follows it too.
