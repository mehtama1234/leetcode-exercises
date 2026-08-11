# 235. Lowest Common Ancestor of a Binary Search Tree

**Pattern:** BST ordered walk
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-search-tree/

## The problem in plain words

Given a binary **search** tree and two of its nodes, find the deepest node that
has both of them somewhere below it. "Below it" includes itself — a node counts
as its own ancestor. That deepest shared ancestor is the point where the paths
down to the two nodes split apart.

## Why this matters

The deeper problem is **finding where two paths through a hierarchy diverge** —
the deepest point that still contains both targets. In a BST the ordering gives
you a shortcut: the split point is the first node that sits *between* the two
values. The fundamental operation is a single guided descent driven by
comparisons, not a search of the whole tree.

This "lowest common ancestor" question is genuinely useful. Version-control
systems find the merge base of two branches — the LCA in the commit tree — to do
a three-way merge. Taxonomies and category trees compute the most specific shared
parent of two items. Access-control and org hierarchies ask "what's the narrowest
scope containing both of these?" Routing over tree topologies uses the meeting
point of two root paths.

What you're solving for is **O(h) time and O(1) space**: because the BST's order
tells you which way to turn at each node, you never store paths or explore
branches that can't contain the answer. It's the payoff for data that keeps
itself sorted — the structure answers the query by being walked once.

## Start from the obvious

In a general binary tree you'd have to search both subtrees and bubble the answer
up (that's the harder problem 236). Your first instinct here might be the same:
find both nodes, record their root-to-node paths, and walk the paths until they
diverge.

```
path_p = path from root to p
path_q = path from root to q
last common node in the two paths is the answer
```

Correct, but it ignores the gift the problem gives you: this is a **search** tree.

## Find the waste

Recording full paths and comparing them re-derives information the BST ordering
already hands you for free. In a BST, at every node you instantly know which side
any value lives on: smaller values are strictly left, larger strictly right. So
you don't need to explore or store anything — you can *steer*.

## The insight

Start at the root and compare both target values to the current node:

- Both **greater** than the current node → both live to the right → go right.
- Both **smaller** → both live to the left → go left.
- Otherwise they've split (one on each side, or one equals the current node) →
  the current node is the lowest common ancestor. Return it.

The first node where the two targets stop agreeing on direction is exactly the
split point, and because we descended greedily it's the *lowest* such node.

```
if p.val > node.val and q.val > node.val: node = node.right
elif p.val < node.val and q.val < node.val: node = node.left
else: return node
```

## Complexity

- **Time:** `O(h)` — we take one step down per loop, never backtracking. Balanced
  → `O(log n)`, degenerate → `O(n)`.
- **Space:** `O(1)` — just a moving pointer, no recursion or path storage.

## Pitfalls

- Using the general-tree LCA algorithm and missing the point — it works but
  throws away the BST speedup.
- Strict vs. non-strict comparison: the `else` branch must fire when a target
  **equals** the current node, so a node can be returned as its own ancestor.
- Assuming both nodes are present; the problem guarantees they are, so no absent
  case to handle here.

## Transfer

"Use the ordering to steer instead of search" is the essence of every BST
operation: insertion, deletion, and
[Search in a BST / 700](https://leetcode.com/problems/search-in-a-binary-search-tree/).
When the tree is *not* a BST, fall back to
[LCA of a Binary Tree / 236](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/),
which recurses and combines results from both sides.
