# 572. Subtree of Another Tree

**Pattern:** Tree recursion — search for a spot, then check an exact match there
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/subtree-of-another-tree/

## The problem in plain words

You have a big tree and a small tree. Does the small tree sit inside the big one as
a **subtree** — is there a node in the big tree such that everything hanging off that
node is identical (shape and values) to the small tree? The match has to go all the
way down to the leaves; you can't stop partway.

```diagram
   big:  3            small:  4
        / \                  / \
       4   5                1   2
      / \
     1   2

   at big's node 4, the whole subtree below is  4
                                                / \
                                               1   2   == small  -> YES
```

## Why this matters

The real job is *finding an exact structural copy of a small thing anywhere inside a
big thing.* It is built from two smaller jobs glued together: **search** (visit each
node of the big tree as a candidate) and **exact match** (structural equality — the
same check as problem 100). "Search × match" shows up constantly, which is why it is
worth seeing with a small picture once.

Compilers and lint tools hunt a syntax tree for a code pattern to flag or rewrite —
find every `x + 0`, spot duplicated subexpressions. Diff and plagiarism tools locate
one document's subtree inside another. HTML/DOM selectors match structural
sub-patterns in a page. Chemistry and bioinformatics search for a substructure inside
a molecule or a phylogenetic tree.

What you are solving for is an honest worst case, and the awareness you can beat it:
serializing both trees or hashing each subtree turns repeated structural comparisons
into cheap equality checks.

## Start from the obvious

Two things must happen: find a candidate spot in the big tree, then check whether the
small tree fits there exactly. Glue them together — at every node of the big tree,
ask "does the whole small tree match starting here?".

```diagram
   walk every node of big:
      at 3: same_tree(subtree@3, small)?  no
      at 4: same_tree(subtree@4, small)?  YES  -> return True
      (never need to check 5, 1, 2)
```

We already know how to write `same_tree` — that is problem 100. So this problem is
really "run problem 100 at every node."

## The insight

The trap is thinking a subtree just means "the small tree's root value appears
somewhere." It is stronger: from the matching node, the shape and values must line up
exactly, all the way down. That is why we reuse the strict `is_same_tree` and not a
looser check.

Two base cases pin the recursion down:

- If `sub` is empty, it fits anywhere — return `True`.
- If `root` is empty but `sub` is not, there is nowhere left to match — `False`.

Then at each node: match here, or recurse into the left child, or recurse into the
right.

```diagram
   sub = [1] (a lone leaf)      big = [1,2]:   1
                                               /
                                              2

   at big's 1: same_tree(subtree@1, sub)?
       subtree@1 is  1        sub is  1
                    /
                   2          -> shapes differ -> NOT the same -> no match
   answer: False   (the only 1 still has a child, so its subtree isn't just [1])
```

## Complexity

- **Time: about n × m in the worst case.** For each of the n nodes in the big tree,
  a same-tree check can walk up to m nodes of the small tree. (Serializing and
  string-searching can reach about n + m, but the nested walk is the clearest and is
  usually fast enough.)
- **Extra memory: about the height of the tree**, for the recursion stack.

## Pitfalls

- Matching only the root value instead of the full subtree. Example 2 exists to
  catch this: `[4,1,2]` appears value-wise, but a stray `0` under a leaf breaks the
  exact match.
- A partial match: `sub = [1]` is not a subtree of `[1,2]`, because the node with
  value 1 there still has a child. (It *is* a subtree of `[1,1]`, matched at the
  childless left leaf.)
- Getting the two empty-tree base cases backwards.

## Transfer

This is the "search for a node, then verify a property from there" combo; the verify
step reuses [Same Tree / 100](../0100-same-tree/). The same "run a full sub-check at
every node" shape appears in
[Path Sum / 112](https://leetcode.com/problems/path-sum/) and in string problems
that look for one string as a substructure of another.
