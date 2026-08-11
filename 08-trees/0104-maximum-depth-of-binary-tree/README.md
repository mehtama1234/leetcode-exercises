# 104. Maximum Depth of Binary Tree

**Pattern:** Tree recursion (DFS), with a BFS alternative
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/maximum-depth-of-binary-tree/

## The problem in plain words

Starting at the root, how many nodes do you pass through on the longest possible
walk straight down to a leaf? That count is the maximum depth. A tree with just a
root has depth 1; an empty tree has depth 0.

## Start from the obvious

Depth is "how far down can I go". If I'm standing at a node, the deepest I can go
from here is 1 (for me) plus however deep I can go through my deepest child.

```
depth(node):
    if node is empty: return 0
    return 1 + max(depth(left), depth(right))
```

That's the whole solution — and it's the honest first thought, because the
question literally *is* recursive: the depth of a tree is defined in terms of the
depth of its subtrees.

## The insight

There is no "waste" to squeeze out here — the recursive definition is already
optimal. The teaching point is recognizing the shape: **compute an answer for
each subtree, then combine the children's answers into the parent's answer.**
For depth, the combine step is `1 + max(...)`.

If you're worried about a very tall, skinny tree overflowing the call stack, the
same answer comes from BFS: peel the tree off one level at a time and count how
many levels there were. That's the `max_depth_bfs` variant.

## Complexity

- **Time:** `O(n)` — every node is visited once, doing `O(1)` work.
- **Space:** `O(h)` for the recursion (`h` = height). Balanced → `O(log n)`,
  degenerate → `O(n)`. The BFS version uses `O(w)` where `w` is the widest level.

## Pitfalls

- Returning 0 for a single node instead of 1 — the base case is the *empty* tree
  returning 0, not the leaf.
- Using `min` instead of `max` (that's a different problem: minimum depth, which
  also has a subtlety about one-sided nodes).
- Counting edges vs. counting nodes: LeetCode's "depth" counts nodes.

## Transfer

"Solve each subtree, combine at the parent" is the universal tree-DFS template.
It powers [Invert Binary Tree / 226](../0226-invert-binary-tree/),
[Balanced Binary Tree / 110](https://leetcode.com/problems/balanced-binary-tree/),
and [Diameter of Binary Tree / 543](https://leetcode.com/problems/diameter-of-binary-tree/),
which is depth with a twist.
