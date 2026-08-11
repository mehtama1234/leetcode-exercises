# 100. Same Tree

**Pattern:** Tree recursion, walking two trees in lockstep
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/same-tree/

## The problem in plain words

You get two trees. Are they exactly the same? "Same" means two things at once: the
same shape (a node sits in one exactly where it sits in the other) **and** the same
value at every matching spot.

```diagram
      p            q            same?
      1            1
     / \          / \
    2   3        2   3      -> YES  (same shape, same values)

      1            1
     /              \
    2                2       -> NO  (2 is on the left vs. the right)
```

## Why this matters

Strip the story away and the job is: *decide if two nested things are identical, by
walking them side by side and stopping the instant they disagree.* You stand on a
position in each tree at the same time and ask one question — "do these two agree
right here?" — then step into the children together.

This lockstep walk runs real tools. Diff tools and `git` compare tree-shaped data
to see what changed. UI frameworks reconcile a new virtual DOM against the old one;
"same node here?" is the question that decides reuse versus repaint. Deep-equal
assertions in test frameworks and config comparison are the same walk.

What you buy is one pass that quits early: no copies, no serializing both sides into
strings to compare — a mismatch near the top ends the work immediately.

## Start from the obvious

Compare position by position, walking both trees together. Stand on a node in each
and ask "do these agree, and do their children agree?".

```diagram
   same(p, q):
     both empty?        -> True   (nothing here, they agree)
     exactly one empty? -> False  (one has a node, the other a gap)
     both present?      -> values equal AND left-subtrees same
                                        AND right-subtrees same
```

This first thought is already the answer — "same tree" is a recursive property, so
the code is a recursive check. There is no slow version to fix.

## The insight

Everything rides on handling the three cases at each pair of positions cleanly, in
the right order:

1. **Both `None`** — nothing in either tree here, so they agree. Return `True`.
2. **Exactly one `None`** — one tree has a node where the other has a hole. Shapes
   already differ. Return `False`.
3. **Both present** — the values must match, and then the two left subtrees must be
   the same and the two right subtrees must be the same.

Check "both empty" first so the "one empty" case can safely assume they are not both
empty. The `and` short-circuits, so a disagreement anywhere stops the whole walk.

```diagram
   p:  1        q:  1
      / \          / \
     2   3        2   4

   compare 1 vs 1: equal -> recurse
     compare 2 vs 2: equal, both leaves -> True
     compare 3 vs 4: 3 != 4 -> False       <- and short-circuits here
   overall: False   (right subtrees never fully walked past this point)
```

## Complexity

- **Time: about n steps**, where n is the size of the smaller tree — we stop as
  soon as shapes diverge, and otherwise touch each node once.
- **Extra memory: about the height of the tree**, for the call stack.

## Pitfalls

- Reading `p.val` before handling the `None` cases — that crashes when `p` is
  `None`.
- Treating "same values, different shape" as equal. `[1,2]` and `[1,null,2]` hold
  the same values but are not the same tree.
- Forgetting that both-empty must return `True`, not `False`.

## Transfer

Lockstep DFS over two trees also drives
[Symmetric Tree / 101](https://leetcode.com/problems/symmetric-tree/) (compare a
tree against its own mirror) and is the inner check inside
[Subtree of Another Tree / 572](../0572-subtree-of-another-tree/), which asks "is
`t` the same tree as some subtree of `s`?".
