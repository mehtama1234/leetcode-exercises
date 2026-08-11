# 98. Validate Binary Search Tree

**Pattern:** Tree recursion (DFS) with an inherited range
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/validate-binary-search-tree/

## The problem in plain words

Check whether a tree obeys the binary-search-tree rule: at every node, *all* the
values in its left subtree are smaller, and *all* the values in its right subtree
are larger. Not just the immediate children — the entire subtree on each side.

## Start from the obvious

The tempting first check is local: for each node, make sure `left.val < node.val
< right.val`.

```
valid(node):
    return node.left.val < node.val < node.right.val
       and valid(node.left) and valid(node.right)
```

This looks right and passes small cases — which is exactly why it's dangerous.

## Find the waste (actually: find the bug)

The local check is too weak. Consider:

```
      5
     / \
    4   6
       / \
      3   7
```

Every parent/child pair looks fine (`4<5`, `3<6`, `7>6`). But `3` sits in the
**right** subtree of `5`, so it must be greater than `5` — and it isn't. A value
must beat *every ancestor whose subtree it fell into*, not just its parent. The
local check throws away that ancestor context.

## The insight

Carry the context down as a **range**. Each node inherits an open interval
`(low, high)` of values it is allowed to hold. Start the root with
`(-∞, +∞)`. Then:

- Descending **left**, values must be smaller than the current node, so tighten
  the upper bound: the child's range becomes `(low, node.val)`.
- Descending **right**, values must be larger, so raise the lower bound:
  `(node.val, high)`.

A node is valid exactly when `low < node.val < high` and both children are valid
under their tightened ranges. The strict `<` (not `<=`) enforces "no duplicates",
which LeetCode requires.

```
valid(node, low, high):
    if node is None: return True
    if not (low < node.val < high): return False
    return valid(node.left, low, node.val) and valid(node.right, node.val, high)
```

## Complexity

- **Time:** `O(n)` — each node checked once against `O(1)` bounds.
- **Space:** `O(h)` for the recursion stack.

## Pitfalls

- The classic bug above: checking only parent/child instead of the full ancestor
  range.
- Using `<=` and accidentally allowing equal values (LeetCode forbids duplicates
  in a valid BST).
- Node values at the integer extremes: seeding with `float("-inf")/float("inf")`
  sidesteps any overflow or boundary confusion.

## Transfer

The "pass an accumulated constraint down the recursion" idea also drives an
**in-order traversal** check (a BST's in-order sequence is strictly increasing —
an equally clean alternative), and range-bounded tree problems like
[Trim a BST / 669](https://leetcode.com/problems/trim-a-binary-search-tree/) and
[Range Sum of BST / 938](https://leetcode.com/problems/range-sum-of-bst/).
