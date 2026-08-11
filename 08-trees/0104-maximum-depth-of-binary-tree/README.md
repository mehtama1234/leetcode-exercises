# 104. Maximum Depth of Binary Tree

**Pattern:** Tree recursion (fold each child's answer up into the parent)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/maximum-depth-of-binary-tree/

## The problem in plain words

Start at the top of the tree and walk straight down to a leaf. Count the nodes you
pass through. Take the longest such walk — that count is the depth. A single node
has depth 1. An empty tree has depth 0.

```diagram
        3          walk down-left:  3 -> 9          = 2 nodes
       / \         walk down-right: 3 -> 20 -> 15   = 3 nodes
      9  20        walk down-right: 3 -> 20 -> 7    = 3 nodes
        /  \
      15    7      longest = 3   ->  depth is 3
```

## Why this matters

The real question hiding here is: *how do you answer something about a whole tree
by only ever looking at one node and its two children?* You never hold the whole
tree in your head. You ask each child "how deep are you?", take the deeper answer,
and add one for yourself. Each node hands a single number up to its parent.

That "children report a number, the parent combines them and reports up" shape is
the backbone of almost every tree algorithm. `du` sums each folder's size from its
subfolders' sizes the same way. Layout engines measure how deeply nested a
component tree is before rendering. And tree *height* itself governs speed
elsewhere: a database index stays fast only while its height stays small, so
implementations track exactly this number to catch a tree that has degraded into a
long chain.

What you buy is one walk that touches each node once. No node is ever measured
twice, because a child computes its own depth and reports it, and the parent trusts
that report.

## Start from the obvious

Depth is "how far down can I go from here". Standing on a node, the deepest walk is
myself (that's 1) plus the deepest walk through whichever child goes further down.

```diagram
   depth(3) = 1 + max( depth(9), depth(20) )
                          |          |
                          1     1 + max(depth(15), depth(7))
                          |                1          1
                       leaf: 1        = 1 + max(1, 1) = 2

   depth(3) = 1 + max(1, 2) = 3
```

That is the whole solution, and it is the honest first thought, because the
question is already recursive: a tree's depth is defined using the depth of its
subtrees.

## The insight

There is no slow version to speed up here — the recursive definition is already
the best you can do. The teaching point is the *shape*: solve each subtree first,
then combine the children's two answers into the parent's answer. For depth the
combine step is `1 + max(left, right)`.

The base case anchors everything: an **empty** tree returns 0. Notice it is the
empty tree, not the leaf, that returns 0 — a leaf gets `1 + max(0, 0) = 1`.

```diagram
   None        -> 0          (nothing below, no depth)
   leaf 15     -> 1 + max(depth(None), depth(None))
              -> 1 + max(0, 0) = 1
```

If a very tall, skinny tree would overflow the call stack, the same answer comes
from peeling the tree off one level at a time and counting the levels — that is the
`max_depth_bfs` variant.

## Complexity

- **Time: about n steps.** Every node is visited once and does a constant amount of
  work (one `max`, one add).
- **Extra memory: about the height of the tree.** That is the depth of the call
  stack. A balanced tree gives about `log n`; a chain gives about `n`.

## Pitfalls

- Returning 0 for a single node. The base case is the *empty* tree returning 0, so
  a lone node returns 1.
- Using `min` instead of `max` — that is a different problem (minimum depth), which
  has its own trap around one-sided nodes.
- Counting edges instead of nodes. LeetCode's "depth" counts nodes.

## Transfer

"Solve each subtree, combine at the parent" is the universal tree template. It
drives [Invert Binary Tree / 226](../0226-invert-binary-tree/),
[Same Tree / 100](../0100-same-tree/),
[Balanced Binary Tree / 110](https://leetcode.com/problems/balanced-binary-tree/),
and [Diameter of Binary Tree / 543](https://leetcode.com/problems/diameter-of-binary-tree/),
which is depth with one extra twist.
