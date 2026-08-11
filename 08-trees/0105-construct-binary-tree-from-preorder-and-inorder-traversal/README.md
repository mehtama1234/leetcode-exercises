# 105. Construct Binary Tree from Preorder and Inorder Traversal

**Pattern:** Divide and conquer using traversal structure
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/construct-binary-tree-from-preorder-and-inorder-traversal/

## The problem in plain words

You're given two readouts of the same tree — its **preorder** sequence (root,
then left subtree, then right subtree) and its **inorder** sequence (left
subtree, then root, then right subtree). Rebuild the actual tree. There's exactly
one tree that produces both.

## Why this matters

The deeper problem is **reconstructing a structure from two different linear
serializations of it** — neither readout alone pins down the shape, but together
they do. The fundamental operation is: use one stream to find the root/pivot, use
the other to split the remaining data into independent sub-problems, then recurse.
It's divide-and-conquer driven by ordering information.

This is a real, recurring engineering shape. Deserializers rebuild an object graph
from a flat byte or token stream. Parsers turn a linear sequence of tokens back
into a syntax tree, and disassemblers reconstruct control-flow structure from a
straight-line instruction listing. Anywhere you've flattened a hierarchy to store
or transmit it, something has to invert that — this is the inversion.

What you're solving for is **doing it in one efficient pass** rather than
re-scanning: the naive version re-searches `inorder` at every node for O(n²); a
value→index hash map makes each split O(1), giving O(n) total. The lesson is that
picking the right auxiliary index turns a quadratic rebuild into a linear one.

## Start from the obvious

What does each traversal tell you on its own?

- **Preorder** always lists the **root first**. So `preorder[0]` is the root of
  the whole tree.
- **Inorder** lists the left subtree, then the root, then the right subtree. So
  if you know the root's value, its position in `inorder` cleanly splits inorder
  into "the left subtree's values" and "the right subtree's values".

That's already a plan: take the root from preorder, split inorder around it,
recurse on each half.

## The insight

Combine the two facts. Once `preorder[0]` gives the root, find that value's index
`mid` in `inorder`. Everything to the **left** of `mid` in inorder is the left
subtree; everything to the **right** is the right subtree. The *count* of
left-subtree values also tells you how many of the following preorder entries
belong to the left subtree.

The clean way to manage the preorder side is to consume it front-to-back with a
single pointer. Preorder is root → left → right, so if you always build the left
child before the right child, the next value you pull from preorder is always the
correct next root:

```
helper(lo, hi):           # bounds into inorder
    if lo > hi: return None
    root = TreeNode(next(preorder))   # consume roots in preorder order
    mid = index_of(root.val in inorder)
    root.left  = helper(lo, mid - 1)  # LEFT first...
    root.right = helper(mid + 1, hi)  # ...then right
    return root
```

Precompute a value → inorder-index map so each split is `O(1)` instead of a
linear scan.

## Complexity

- **Time:** `O(n)` — one node built per value, with `O(1)` split lookups thanks
  to the map.
- **Space:** `O(n)` — the index map plus `O(h)` recursion stack.

Without the map, the repeated `index()` scans make it `O(n^2)` — that's the waste
the hash map removes, the same trade as Two Sum.

## Pitfalls

- Building the **right** subtree before the left while consuming preorder with a
  shared pointer — the roots come out in the wrong order.
- Rescanning inorder for the root each time (`O(n^2)`) instead of using a map.
- Assumes all values are **unique** (LeetCode guarantees this); with duplicates
  the split is ambiguous and this approach breaks.

## Transfer

Same idea, different pairing:
[Construct from Inorder and Postorder / 106](https://leetcode.com/problems/construct-binary-tree-from-inorder-and-postorder-traversal/)
— postorder's *last* element is the root, so consume it back-to-front and build
right before left. The general move ("one traversal locates the root, another
splits the children") also underlies serialize/deserialize
([297](../0297-serialize-and-deserialize-binary-tree/)).
