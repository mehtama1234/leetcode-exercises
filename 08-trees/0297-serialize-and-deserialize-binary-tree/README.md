# 297. Serialize and Deserialize Binary Tree

**Pattern:** Preorder DFS with null markers
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/serialize-and-deserialize-binary-tree/

## The problem in plain words

Write two functions that are inverses of each other: `serialize` turns a tree
into a string, and `deserialize` turns that string back into the identical tree.
The format is your choice — the only requirement is that going one way and back
gives you exactly what you started with.

## Start from the obvious

Just list the values in some traversal order, right?

```
serialize: "1,2,3,4,5"
```

The trap: a bare list of values loses the **shape**. The values `[1,2,3]` could be
a root with two children, or a left-leaning chain, or a right-leaning chain — the
string can't tell them apart. Serialization has to capture structure, not just
content.

## The insight: record the gaps too

The missing information is *where the empty children are*. So record them
explicitly: every time a child is absent, write a sentinel like `#`. Now the
string encodes the full shape, because for every node you can see whether each of
its two child slots is a real node or a hole.

Pair that with **preorder** (root, then left, then right) and deserialization
becomes almost free. Preorder writes tokens in exactly the order you want to
rebuild them, so you consume them front-to-back with a single pointer:

```
serialize(node):
    if node is None: emit "#"; return
    emit node.val
    serialize(node.left)
    serialize(node.right)

deserialize():
    val = next token
    if val == "#": return None
    node = TreeNode(val)
    node.left  = deserialize()   # next tokens are the left subtree
    node.right = deserialize()   # then the right subtree
    return node
```

The recursion structure of `deserialize` mirrors `serialize` exactly, which is
why the tokens line up without any index math.

## Complexity

- **Time:** `O(n)` for each direction — one token per real node plus one per null
  slot (there are `n+1` null slots, so still `O(n)`).
- **Space:** `O(n)` for the string, plus `O(h)` recursion depth.

## Pitfalls

- Omitting null markers — you lose the shape and can't reconstruct uniquely.
- Mismatched orders: if `serialize` uses preorder, `deserialize` must consume in
  preorder too. Build left before right.
- Parsing values as strings when they can be negative or multi-digit — split on a
  delimiter (`,`) rather than reading single characters.
- Forgetting the empty tree: it should serialize to just `#` and come back as
  `None`.

## Transfer

The "encode structure with sentinels, decode by mirroring the traversal" idea is
the general recipe for tree persistence. It's the flip side of
[Construct from Preorder/Inorder / 105](../0105-construct-binary-tree-from-preorder-and-inorder-traversal/)
(there you reconstruct from two *incomplete* traversals; here one traversal is
enough because you added the null markers). BFS-based serialization (LeetCode's
own bracket format) is an equally valid alternative.
