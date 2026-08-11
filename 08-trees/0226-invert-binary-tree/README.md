# 226. Invert Binary Tree

**Pattern:** Tree recursion (DFS)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/invert-binary-tree/

## The problem in plain words

Take a binary tree and flip it into its mirror image. Every node keeps its
value, but its two children trade places — and this happens at *every* level,
all the way down.

## Why this matters

Underneath the meme-famous puzzle is a real pattern: **applying a transformation
uniformly to every node of a recursive structure**, where the transform at each
node (swap the children) plus recursion on the subtrees produces the whole result.
The fundamental operation is a structural map/rewrite over a tree.

That operation is everywhere real trees get manipulated. Compilers and linters
rewrite abstract syntax trees — constant folding, desugaring, reordering
commutative operands — by walking and transforming each node. DOM/UI code mirrors
or reorders layout subtrees for right-to-left languages. Graphics and geometry
code reflects hierarchical scene graphs. Any "normalize this nested structure"
task is a tree rewrite of exactly this form.

What you're solving for is a **single O(n) pass, O(height) stack**, mutating in
place with no extra copy of the tree. The deeper lesson is recognizing that a
transformation defined recursively ("the mirror of a tree is a tree whose swapped
subtrees are themselves mirrored") maps straight onto code with no cleverness
required — which is why it's a favorite warm-up.

## Start from the obvious

What does "mirror" mean at a single node? Its left child should become its right
child and vice versa. But its children have children too, and those need to be
mirrored as well.

```
mirror(node):
    node.left, node.right = mirror of node.right, mirror of node.left
```

The honest first thought is: I have to visit every node and swap. The only real
question is how to make "the whole subtree below also gets mirrored" fall out
automatically.

## The insight

The definition of a mirrored tree is itself recursive: a tree's mirror is a tree
whose **left** subtree is the mirror of the original **right** subtree, and whose
**right** subtree is the mirror of the original **left** subtree.

So you don't manage the recursion by hand. You invert the right side, invert the
left side, then assign them crossed over:

```
root.left, root.right = invert(root.right), invert(root.left)
```

The base case is the empty tree — an empty tree looks the same in a mirror, so
return `None` unchanged. Because Python evaluates the whole right-hand side
before assigning, the swap is safe even without a temp variable.

## Complexity

- **Time:** `O(n)` — each node is visited exactly once and does `O(1)` work.
- **Space:** `O(h)` where `h` is the height, for the recursion call stack. A
  balanced tree gives `O(log n)`; a degenerate (linked-list-shaped) tree gives
  `O(n)`.

## Pitfalls

- Swapping the children **before** you recurse but forgetting to recurse into
  the new positions — you'll only mirror the top level.
- Using a temp variable incorrectly in languages without tuple assignment
  (`a = b; b = a` loses `a`). Python's `a, b = b, a` avoids this.
- Forgetting the empty-tree base case, causing a `None.left` crash.

## Transfer

The move "the transformed tree is defined in terms of transformed subtrees, so
recurse then combine" is the core of nearly every tree problem:
[Maximum Depth / 104](../0104-maximum-depth-of-binary-tree/),
[Same Tree / 100](../0100-same-tree/),
[Symmetric Tree / 101](https://leetcode.com/problems/symmetric-tree/) (which is
literally "is this tree its own mirror?").
