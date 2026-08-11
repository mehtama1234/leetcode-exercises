# 226. Invert Binary Tree

**Pattern:** Tree recursion (transform each node, let the subtrees transform themselves)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/invert-binary-tree/

## The problem in plain words

Flip a binary tree into its mirror image. Each node keeps its value, but its two
children trade places — and this happens at *every* node, all the way down.

```diagram
        4                 4
       / \               / \
      2   7    ---->     7   2
     / \ / \            / \ / \
    1  3 6  9          9  6 3  1

   left and right swap at every level, top to bottom
```

## Why this matters

The real move is: *apply the same small change to every node of a nested
structure, and make the whole thing update by itself.* The change here is "swap the
two children." You do not manage the descent by hand — you state what a mirrored
tree is, in terms of smaller mirrored trees, and the recursion does the rest.

That "walk a tree and rewrite each node" operation is everywhere real trees get
edited. Compilers rewrite syntax trees — folding constants, reordering operands
that commute. UI code mirrors layout subtrees for right-to-left languages. Graphics
code reflects scene graphs. Any "normalize this nested thing" job is a tree rewrite
of this exact form.

What you buy is one pass that touches each node once, editing the tree in place with
no second copy. The lesson is spotting that a recursively-defined transform maps
straight onto code — which is why this is a classic warm-up.

## Start from the obvious

What does "mirror" mean at a single node? Its left child should end up on the right
and its right child on the left. But those children have children too, and each of
those subtrees must also be mirrored.

```diagram
   at node 2:              want:
        2                    2
       / \        ---->     / \
      1   3                3   1

   ...but if 1 and 3 had subtrees, those must flip too
```

The honest first thought: I have to visit every node and swap. The only real
question is how to make "and everything below also flips" happen without me tracking
it.

## The insight

The definition of a mirrored tree is itself recursive: a tree's mirror is a tree
whose **left** subtree is the mirror of the original **right** subtree, and whose
**right** subtree is the mirror of the original **left** subtree.

So you invert the right side, invert the left side, and assign them crossed over. The
recursion handles every deeper level for you.

```diagram
   invert(4):
      L = invert(node 7 subtree)   -> returns the mirrored 7-subtree
      R = invert(node 2 subtree)   -> returns the mirrored 2-subtree
      4.left, 4.right = L, R       (crossed: old-right lands on the left)
      return 4

   each invert(...) call did the same crossing for its own children
```

The base case is the empty tree — a mirror of nothing is nothing, so return `None`
unchanged. Python evaluates the whole right-hand side before assigning, so
`a, b = invert(b), invert(a)` swaps safely with no temp variable.

## Complexity

- **Time: about n steps.** Each node is visited once and swaps two pointers.
- **Extra memory: about the height of the tree**, for the call stack. Balanced is
  about `log n`; a chain is about `n`.

## Pitfalls

- Swapping the children but forgetting to recurse into them — you would only mirror
  the top level.
- In a language without tuple assignment, writing `a = b; b = a` loses `a`. Python's
  `a, b = b, a` sidesteps that.
- Forgetting the empty-tree base case, which crashes on `None.left`.

## Transfer

"The transformed tree is defined in terms of transformed subtrees, so recurse then
combine" is the heart of nearly every tree problem:
[Maximum Depth / 104](../0104-maximum-depth-of-binary-tree/),
[Same Tree / 100](../0100-same-tree/), and
[Symmetric Tree / 101](https://leetcode.com/problems/symmetric-tree/), which asks
"is this tree its own mirror?".
