# 235. Lowest Common Ancestor of a Binary Search Tree

**Pattern:** BST guided walk — let the ordering steer you instead of searching
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-search-tree/

## The problem in plain words

Given a binary **search** tree and two of its nodes, find the deepest node that has
both of them somewhere below it. "Below it" includes itself — a node counts as its
own ancestor. That deepest shared ancestor is exactly where the paths down to the two
nodes split apart.

```diagram
          6
        /   \
       2     8        p=2, q=8  -> paths split at the root 6   -> LCA is 6
      / \   / \
     0   4 7   9      p=2, q=4  -> 4 is below 2, so LCA is 2 (its own ancestor)
        / \
       3   5          p=3, q=5  -> both below 4              -> LCA is 4
```

## Why this matters

The real question is *where do two paths through a hierarchy diverge* — the deepest
point that still contains both targets. In a plain tree you would have to search both
sides and bubble the answer up. But a BST hands you a shortcut: the split point is the
first node that sits *between* the two values, and you find it with one guided descent
driven by comparisons.

This "lowest common ancestor" question is genuinely useful. Version-control systems
find the merge base of two branches — the LCA in the commit tree — for a three-way
merge. Taxonomies compute the most specific shared parent of two items.
Access-control and org hierarchies ask "what's the narrowest scope containing both of
these?".

What you buy is a walk that costs only the tree height, with a single moving pointer:
the ordering tells you which way to turn, so you never store paths or explore
branches that can't contain the answer.

## Start from the obvious

In a general tree you would record both root-to-node paths and compare them.

```diagram
   path to p:  6 -> 2
   path to q:  6 -> 8
   last node they share, reading down, is the answer:  6
```

Correct — but it ignores the gift the problem gives you: this is a *search* tree.

## Find the waste

Recording full paths and comparing them re-derives information the ordering already
hands you for free. In a BST, at every node you instantly know which side any value
lives on: smaller values are strictly left, larger strictly right. So you don't need
to store or explore — you can *steer*.

## The insight

Start at the root and compare *both* targets to the current node:

- Both **greater** than this node -> both live to the right -> go right.
- Both **smaller** -> both live to the left -> go left.
- Otherwise they have split (one on each side, or one equals this node) -> this node
  is the lowest common ancestor. Return it.

```diagram
   find LCA of 3 and 5, starting at 6:

   at 6: 3<6 and 5<6      -> both smaller -> go LEFT to 2
   at 2: 3>2 and 5>2      -> both larger  -> go RIGHT to 4
   at 4: 3<4 but 5>4      -> they SPLIT   -> answer is 4
```

The first node where the two targets stop agreeing on direction is the split point,
and because we descended greedily it is the *lowest* such node.

## Complexity

- **Time: about the tree height** — one step down per loop, never backtracking.
  Balanced is about `log n`; a chain is about `n`.
- **Extra memory: constant** — just a moving pointer, no recursion or stored paths.

## Pitfalls

- Using the general-tree LCA algorithm — it works but throws away the BST speedup.
- The `else` branch must fire when a target *equals* the current node, so a node can
  be returned as its own ancestor.
- Assuming both nodes are present; the problem guarantees it, so there is no
  absent case to handle.

## Transfer

"Use the ordering to steer instead of search" is the essence of every BST operation:
insertion, deletion, and
[Search in a BST / 700](https://leetcode.com/problems/search-in-a-binary-search-tree/).
When the tree is *not* a BST, fall back to
[LCA of a Binary Tree / 236](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/),
which recurses and combines results from both sides.
