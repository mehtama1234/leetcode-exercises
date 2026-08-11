# 297. Serialize and Deserialize Binary Tree

**Pattern:** Preorder walk that writes a marker for every empty child
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/serialize-and-deserialize-binary-tree/

## The problem in plain words

Write two functions that undo each other: `serialize` turns a tree into a string, and
`deserialize` turns that string back into the identical tree. The format is your
choice — the only rule is that going one way and back gives you exactly what you
started with.

```diagram
        1              serialize ->  "1,2,#,#,3,4,#,#,5,#,#"
       / \
      2   3            deserialize -> the same tree, rebuilt
         / \
        4   5          ('#' marks an empty child slot)
```

## Why this matters

This is the everyday problem of *serialization*: flattening a structure into a linear
form you can store or send, and rebuilding it exactly on the other side. The reusable
lesson is that you must encode the *shape*, not just the contents — writing explicit
markers for the empty children is what makes the flattening reversible.

Real systems do this constantly. Saving an object graph to disk or sending it over a
network (JSON, Protocol Buffers, `pickle`) is exactly this. Databases persist B-tree
pages and restore them; message queues ship structured payloads; caches store and
rehydrate nested objects; save-game files snapshot a scene graph. Every one needs
"shape survives the trip."

What you buy is a compact, unambiguous encoding that rebuilds in one pass — no
guessing at structure, and a format where serialize and deserialize are true
inverses. The honest cost is the extra bytes for the empty markers, which is the
price of never losing the shape.

## Start from the obvious

Just list the values in some order, right?

```diagram
   serialize -> "1,2,3"

   but [1,2,3] could be any of these:
       1          1            1
      / \        /              \
     2   3      2                2
               /                  \
              3                    3
   a bare list of values loses the SHAPE
```

Serialization has to capture structure, not just content.

## The insight: record the gaps too

The missing information is *where the empty children are*. So write them down: every
time a child is absent, emit a marker like `#`. Now the string pins the shape, because
for every node you can see whether each of its two child slots is a real node or a
hole.

Pair that with **preorder** (root, then left, then right) and rebuilding becomes
almost free. Preorder writes tokens in exactly the order you want to consume them, so
`deserialize` reads them front-to-back with one pointer, mirroring the same recursion.

```diagram
   tree:  1        serialize (preorder, # for empty):
         / \
        2   3      visit 1 -> "1"
                     visit 2 -> "2", left #, right #   -> "1,2,#,#"
                     visit 3 -> "3", left #, right #   -> "1,2,#,#,3,#,#"

   deserialize reads the same tokens in the same order:
     "1" -> node 1; build its left from what comes next...
       "2" -> node 2; its left "#" -> None; its right "#" -> None
     back to 1's right...
       "3" -> node 3; left "#" -> None; right "#" -> None
```

The recursion in `deserialize` matches `serialize` exactly, so the tokens line up with
no index math.

## Complexity

- **Time: about n steps** each direction — one token per real node plus one per empty
  slot (there are `n+1` empty slots, so still about n).
- **Extra memory: about n** for the string, plus recursion about the tree height.

## Pitfalls

- Omitting the empty markers — you lose the shape and can't rebuild uniquely.
- Mismatched orders: if `serialize` uses preorder, `deserialize` must consume in
  preorder too. Build left before right.
- Reading values as single characters when they can be negative or multi-digit —
  split on a delimiter like `,` instead.
- Forgetting the empty tree: it should serialize to just `#` and come back as `None`.

## Transfer

"Encode structure with markers, decode by mirroring the traversal" is the general
recipe for tree persistence. It is the flip side of
[Construct from Preorder/Inorder / 105](../0105-construct-binary-tree-from-preorder-and-inorder-traversal/)
— there you rebuild from two *incomplete* readouts; here one readout is enough because
you added the empty markers. A BFS-based format (LeetCode's own bracket notation) is
an equally valid alternative.
