# 105. Construct Binary Tree from Preorder and Inorder Traversal

**Pattern:** Split into halves — one readout names the root, the other splits the children
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/construct-binary-tree-from-preorder-and-inorder-traversal/

## The problem in plain words

You get two readouts of the same tree. **Preorder** lists root, then the whole left
subtree, then the whole right subtree. **Inorder** lists the left subtree, then the
root, then the right subtree. Rebuild the actual tree. Exactly one tree produces both.

```diagram
   preorder = [3, 9, 20, 15, 7]     (root always comes first)
   inorder  = [9, 3, 15, 20, 7]     (root sits between its two subtrees)

   the tree they both describe:
        3
       / \
      9  20
        /  \
      15    7
```

## Why this matters

The real task is *rebuilding a structure from two flat readouts of it* — neither
readout alone pins down the shape, but together they do. The move: use one stream to
find the root, use the other to split the rest into two independent sub-problems, then
solve each the same way. That is divide-and-conquer driven by ordering.

This shape recurs in engineering. Deserializers rebuild an object graph from a flat
byte stream. Parsers turn a linear sequence of tokens back into a syntax tree.
Disassemblers reconstruct control-flow structure from a straight-line instruction
listing. Anywhere you flattened a hierarchy to store or send it, something has to
invert that.

What you buy is doing it in one efficient pass. The naive version re-scans inorder at
every node — about `n²` work; a value→index map makes each split a single lookup,
bringing it to about `n`. Picking the right lookup table turns a quadratic rebuild
into a linear one.

## Start from the obvious

What does each readout tell you on its own?

- **Preorder** lists the **root first**. So `preorder[0]` is the root of the whole
  tree.
- **Inorder** lists left, then root, then right. So once you know the root's value,
  its position in inorder splits inorder cleanly into "left subtree's values" and
  "right subtree's values."

```diagram
   root = preorder[0] = 3
   find 3 in inorder:  [9 | 3 | 15, 20, 7]
                        ^^^      ^^^^^^^^^^
                      left of 3   right of 3
   left subtree values  = {9}
   right subtree values = {15, 20, 7}
```

That is already a plan: take the root from preorder, split inorder around it, recurse
on each half.

## The insight

Combine the two facts. `preorder[0]` gives the root; find its index `mid` in inorder.
Everything left of `mid` is the left subtree, everything right is the right subtree.
The *count* of left-subtree values also tells you how many of the following preorder
entries belong to the left subtree.

The clean way to feed the preorder side is a single pointer moving front-to-back.
Preorder is root → left → right, so if you always build the **left** child before the
right, the next value you pull is always the correct next root.

```diagram
   preorder pointer walks: 3, then 9, then 20, then 15, then 7

   build(3):  mid of 3 in inorder splits -> left={9}, right={15,20,7}
     build LEFT first -> next preorder value is 9
       build(9): its inorder slice is empty on both sides -> leaf
     build RIGHT      -> next preorder value is 20
       build(20): splits -> left={15}, right={7}
         build(15) -> leaf,  build(7) -> leaf
```

Precompute a value→inorder-index map so each split is a single lookup instead of a
scan.

## Complexity

- **Time: about n steps** — one node built per value, each split a constant-time map
  lookup.
- **Extra memory: about n** — the index map, plus recursion about the tree height.

Without the map, the repeated `index()` scans make it about `n²` — that is the waste
the map removes, the same trade as Two Sum.

## Pitfalls

- Building the **right** subtree before the left while sharing one preorder pointer —
  the roots come out in the wrong order.
- Rescanning inorder for the root each time (about `n²`) instead of using the map.
- Assumes all values are **unique** (LeetCode guarantees it); with duplicates the
  split point is ambiguous and this approach breaks.

## Transfer

Same idea, different pairing:
[Construct from Inorder and Postorder / 106](https://leetcode.com/problems/construct-binary-tree-from-inorder-and-postorder-traversal/)
— postorder's *last* element is the root, so consume it back-to-front and build the
right child before the left. The general move ("one readout names the root, the other
splits the children") also underlies
[serialize/deserialize / 297](../0297-serialize-and-deserialize-binary-tree/).
