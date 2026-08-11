# 100. Same Tree

**Pattern:** Tree recursion (DFS), lockstep traversal
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/same-tree/

## The problem in plain words

You get two trees. Are they exactly the same? "Same" means two things at once:
they have the same shape (a node exists in one exactly where it exists in the
other) **and** the values line up at every matching spot.

## Why this matters

The deeper problem is **structural equality**: deciding whether two recursively
defined things are identical in both shape and content, by walking them in
lockstep and short-circuiting the moment they disagree. The fundamental operation
is a synchronized traversal of two structures.

This shows up constantly. Diff tools and `git` compare tree-shaped data (file
trees, ASTs) to decide what changed. React and other UI frameworks reconcile a
new virtual DOM tree against the old one — "same node here?" is the core question
that decides whether to reuse or repaint. Test frameworks' deep-equal assertions,
JSON/config comparison, and schema-migration checks all reduce to this lockstep
walk.

What you're solving for is **one linear pass that stops early**: you never build
intermediate copies or serialize both sides to compare strings, and a mismatch
near the root ends the work immediately instead of touching every node. It's the
minimal, allocation-free way to answer "are these two the same?".

## Start from the obvious

Compare them position by position, walking both at the same time. Stand on a
node in each tree simultaneously and ask "do these two agree?".

```
same(a, b):
    if both empty: True
    if only one empty: False        # shapes differ here
    return a.val == b.val and same(a.left, b.left) and same(a.right, b.right)
```

This is the natural first thought and it's already the answer — "same tree" is a
recursive property, so the code is a recursive check.

## The insight

The key is enumerating the three cases at each pair of positions cleanly:

1. **Both `None`** — nothing here in either tree, so they agree. Return `True`.
2. **Exactly one `None`** — one tree has a node where the other has a gap. The
   shapes already differ. Return `False`.
3. **Both present** — the local values must match, and then the two left
   subtrees must be the same and the two right subtrees must be the same.

Ordering matters: check the "both empty" case first so that the "one empty" case
can safely assume they're not both empty. The `and` short-circuits, so a mismatch
anywhere stops the walk early.

## Complexity

- **Time:** `O(n)` where `n` is the size of the smaller tree — we stop as soon as
  shapes diverge, and otherwise touch each node once.
- **Space:** `O(h)` for the recursion stack.

## Pitfalls

- Comparing values before handling the `None` cases — `p.val` crashes when `p` is
  `None`.
- Treating "same values in a different shape" as equal. `[1,2]` and `[1,null,2]`
  have the same multiset of values but are **not** the same tree.
- Forgetting that both-empty must return `True`, not `False`.

## Transfer

Lockstep DFS over two trees powers
[Symmetric Tree / 101](https://leetcode.com/problems/symmetric-tree/) (compare a
tree against itself, mirrored) and is the inner check for
[Subtree of Another Tree / 572](../0572-subtree-of-another-tree/), which asks
"is `t` the same tree as some subtree of `s`?".
