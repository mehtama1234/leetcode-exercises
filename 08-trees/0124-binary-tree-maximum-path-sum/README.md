# 124. Binary Tree Maximum Path Sum

**Pattern:** Tree DFS with a "return one thing, track another" twist
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/binary-tree-maximum-path-sum/

## The problem in plain words

A path is any connected chain of nodes following parent-child links. It can start
and end anywhere, and it doesn't have to touch the root. Add up the values along
a path — what's the biggest total you can get? Values can be negative, which is
what makes this tricky.

## Start from the obvious

You might try: for every node, compute the best path that passes through it, and
take the max over all nodes. That's the right *goal*. The hard part is that a path
through a node can bend — it can come **up** the left arm, pass through the node,
and go back **down** the right arm, like an upside-down V. So "best path through
this node" isn't a single downward line.

## The insight: two different quantities

Each node is involved in two distinct measurements, and confusing them is the
classic mistake:

1. **The best path that peaks at this node.** It may use both children:
   `node.val + best_left_arm + best_right_arm`. This is a legitimate answer
   candidate — a full bent path.
2. **The best path this node can extend to its parent.** A parent that links
   through this node can only continue in a straight line, so this node may
   contribute itself plus **at most one** arm:
   `node.val + max(left_arm, right_arm)`. You can't hand both arms upward,
   because the parent would then create a branch, not a path.

So the DFS **returns** quantity 2 (the upward-extendable value) while **updating a
global best** with quantity 1 (the peak). And any arm with a negative total is
worthless — we'd rather take nothing than subtract — so clamp each arm at 0.

```
gain(node):
    if node is None: return 0
    left  = max(gain(node.left), 0)     # ignore negative arms
    right = max(gain(node.right), 0)
    best = max(best, node.val + left + right)   # path peaking here
    return node.val + max(left, right)          # straight line upward
```

## Complexity

- **Time:** `O(n)` — one visit per node, constant work each.
- **Space:** `O(h)` recursion stack.

## Pitfalls

- Returning `node.val + left + right` up to the parent — that hands up a bent
  path the parent can't legally use. Return only one arm upward.
- Initializing the global best to 0 — wrong when every value is negative
  (`[-3]` should give `-3`, not 0). Start at `-inf`.
- Forgetting to clamp arms at 0, so a strongly negative subtree drags a good path
  down instead of being skipped.

## Transfer

The "recurse returning a *restricted* value while a side channel tracks the true
answer" pattern is reusable:
[Diameter of Binary Tree / 543](https://leetcode.com/problems/diameter-of-binary-tree/)
(return depth upward, track the longest bent path globally) is the same shape with
lengths instead of sums, and
[Longest Univalue Path / 687](https://leetcode.com/problems/longest-univalue-path/)
follows it too.
