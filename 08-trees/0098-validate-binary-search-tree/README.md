# 98. Validate Binary Search Tree

**Pattern:** Tree recursion carrying an allowed (low, high) range down each branch
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/validate-binary-search-tree/

## The problem in plain words

Check whether a tree obeys the binary-search-tree rule: at every node, *all* the
values in its left subtree are smaller, and *all* the values in its right subtree are
larger. Not just the immediate children — the entire subtree on each side.

```diagram
      5            valid?  left of 5 is {1,4} all < 5     ok
     / \                  right of 5 is {6} all > 5       ok
    1   6                 -> YES

      5            valid?  3 sits in the RIGHT subtree of 5,
     / \                  so it must be > 5.  It is 3.       FAIL
    1   6                 -> NO  (even though 3 < 6 looks fine locally)
       / \
      3   7
```

## Why this matters

The real task is *confirming a global order from local checks*: every value has to
respect the range squeezed on it by ancestors far above, not just its parent. You
carry a shrinking `(low, high)` window down each branch and check membership at each
node.

This is what real systems do. Database engines validate B-tree index pages this way —
a corrupted index is caught by confirming each key sits inside the range its
position implies. Compilers and type checkers carry an inherited context (which names
are in scope, which types are allowed) down the syntax tree and reject a node that
breaks it. Schema validators do the same for nested documents.

What you buy is one pass with memory only as deep as the tree, and no sorting or
extra structures — the tree already encodes the order, so you confirm it holds
rather than rebuild it. The subtle win is catching the *non-local* violation the
naive neighbor check misses.

## Start from the obvious

The tempting check is local: for each node, make sure `left.val < node.val <
right.val`.

```diagram
   valid(node):
       node.left.val < node.val < node.right.val
       AND valid(left) AND valid(right)
```

This looks right and passes small cases — which is exactly what makes it dangerous.

## Find the waste (actually: find the bug)

The local check is too weak. Look again at the failing tree:

```diagram
      5
     / \
    1   6
       / \
      3   7

   parent/child pairs all look fine: 1<5, 3<6, 7>6
   but 3 fell into the RIGHT subtree of 5, so it must beat 5 too -- it doesn't.
```

A value must beat *every ancestor whose subtree it fell into*, not just its parent.
The local check throws that ancestor context away.

## The insight

Carry the context down as a **range** — the open interval a node is allowed to hold.
Start the root at `(-inf, +inf)`. Then:

- Going **left**, values must be smaller than this node, so tighten the top:
  the child's range becomes `(low, node.val)`.
- Going **right**, values must be larger, so raise the bottom: `(node.val, high)`.

A node is valid exactly when `low < node.val < high` and both children are valid
under their tightened ranges. The strict `<` (not `<=`) forbids duplicates, which
LeetCode requires.

```diagram
   check(5, -inf, +inf):  -inf < 5 < +inf   ok
     check(1, -inf, 5):    -inf < 1 < 5      ok
     check(6, 5, +inf):       5 < 6 < +inf   ok
       check(3, 5, 6):        5 < 3 ? NO  -> FAIL
                              ^ the range from ancestor 5 catches it
```

## Complexity

- **Time: about n steps** — each node checked once against a constant-size range.
- **Extra memory: about the height of the tree**, for the recursion stack.

## Pitfalls

- The classic bug above: checking only parent/child instead of the full inherited
  range.
- Using `<=` and letting equal values through (a valid BST here forbids duplicates).
- Node values at the integer extremes: seeding with `float("-inf")/float("inf")`
  sidesteps any boundary confusion.

## Transfer

"Pass an accumulated constraint down the recursion" also gives a clean alternative:
an **in-order traversal** of a BST must come out strictly increasing (that walk shows
up in [Kth Smallest / 230](../0230-kth-smallest-element-in-a-bst/)). The same
range-bounding idea drives
[Trim a BST / 669](https://leetcode.com/problems/trim-a-binary-search-tree/) and
[Range Sum of BST / 938](https://leetcode.com/problems/range-sum-of-bst/).
