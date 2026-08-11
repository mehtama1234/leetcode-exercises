# 572. Subtree of Another Tree

**Pattern:** Tree recursion (DFS) — search × exact-match
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/subtree-of-another-tree/

## The problem in plain words

You have a big tree and a small tree. Does the small tree appear inside the big
one as a **subtree** — meaning: is there some node in the big tree such that the
entire tree hanging off that node is identical (shape and values) to the small
tree? A subtree must go all the way to its leaves; you can't stop partway.

## Why this matters

The deeper problem is **pattern matching inside a structure**: scanning every
position of a big recursive object for an exact structural copy of a smaller one.
It composes two primitives — *search* (visit each candidate node) and
*exact-match* (structural equality, problem 100) — which is why "search × match"
recurs across so many tasks.

Concretely: compilers and refactoring/lint tools hunt an AST for a code pattern
to flag or rewrite it (find every `x + 0`, detect duplicated subexpressions).
Diff and plagiarism tools locate a subtree of one document inside another. HTML/DOM
queries and CSS-like selectors match structural sub-patterns in a page. Chemistry
and bioinformatics do subgraph/substructure search on molecule and phylogenetic
trees.

What you're solving for is **an honest O(n·m) worst case** from the naive
match-at-every-node approach — and the awareness that you can do better: hashing
each subtree (Merkle-style) or serializing both trees and running string search
brings it near O(n+m). That trade — pay some preprocessing to turn repeated
structural comparisons into cheap equality checks — is the transferable idea.

## Start from the obvious

Two things have to happen. First, find a candidate spot in the big tree. Second,
check whether the small tree fits there exactly. The obvious plan glues those
together: at every node of the big tree, ask "does the whole small tree match
starting here?".

```
is_subtree(root, sub):
    for each node in root:
        if same_tree(node, sub): return True
    return False
```

We already know how to write `same_tree` (that's problem 100). So this problem is
really "run problem 100 at every node".

## The insight

The trap is thinking a subtree is just "does `sub`'s root value appear
somewhere". It's stronger: the match must be exact and complete from that node
down. That's why we reuse the strict `is_same_tree` check rather than a looser
one.

Two base cases pin the recursion down:

- If `sub` is empty, it's a subtree of anything — return `True`.
- If `root` is empty but `sub` isn't, there's nowhere left to match — `False`.

Then: match here, or recurse into the left child, or recurse into the right.

```
is_same_tree(root, sub) or is_subtree(root.left, sub) or is_subtree(root.right, sub)
```

## Complexity

- **Time:** `O(n · m)` in the worst case — for each of the `n` nodes in `root` we
  may run an `O(m)` same-tree comparison against `sub`. (A serialize-and-search
  approach can reach `O(n + m)`, but the nested-DFS version is the clearest and
  usually fast enough.)
- **Space:** `O(h)` for the recursion stack.

## Pitfalls

- Matching only the root value instead of the whole subtree — example 2 exists
  precisely to catch this: `[4,1,2]` appears value-wise but a stray `0` under a
  leaf breaks the exact match.
- A partial match: `sub = [1]` (a lone leaf) is **not** a subtree of `[1,2]`,
  because the only node with value 1 there still has a child, so its full subtree
  isn't `[1]`. (It *is* a subtree of `[1,1]`, matched at the childless left leaf.)
- Getting the empty-tree base cases backwards.

## Transfer

This is the "search for a node, then verify a property from there" combo. The
verify step reuses [Same Tree / 100](../0100-same-tree/). The same "run a whole
sub-check at every node" shape appears in
[Path Sum / 112](https://leetcode.com/problems/path-sum/) and string problems
like finding one string as a substructure of another.
