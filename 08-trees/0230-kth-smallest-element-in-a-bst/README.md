# 230. Kth Smallest Element in a BST

**Pattern:** In-order walk of a BST, stopping the moment you reach the k-th value
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/kth-smallest-element-in-a-bst/

## The problem in plain words

You have a binary search tree and a number `k`. Return the `k`-th smallest value in
it, counting from 1 — so `k=1` is the minimum.

```diagram
        3
       / \        sorted values: 1, 2, 3, 4
      1   4       k=1 -> 1   k=2 -> 2   k=3 -> 3
       \
        2
```

## Why this matters

The real idea is *use order that is already stored, don't re-sort it*, and *stop the
moment you have the answer*. Walking a BST in-order hands you the values in sorted
order one at a time, so the job becomes: stream the sorted sequence and halt at the
k-th item.

This is what ordered indexes do. A database B-tree answers `ORDER BY ... LIMIT k` or
paged `OFFSET/LIMIT` by walking the index in key order and stopping early — it never
sorts the table. Top-k queries, percentile and median lookups over a sorted
structure, and leaderboard ranks all lean on "the structure already encodes order,
just walk it."

What you buy is skipping both the wasteful full sort and the full traversal: the walk
costs about the tree height plus k, touching only the nodes it must and then quitting.

## Start from the obvious

The blunt approach: collect every value, sort, take index `k-1`.

```diagram
   vals = every value in the tree
   vals.sort()
   return vals[k-1]
```

That is about `n log n` work, and it ignores that the tree is *already a search tree*
— its shape encodes the order for free.

## Find the waste

Two wasteful things happen. First, we sort values the BST already keeps ordered.
Second, we process the whole tree even though we only need the first `k` in order.

The fix for the first: an **in-order** walk of a BST emits values smallest to
largest on its own. Why? At any node, everything in the left subtree is smaller, so
if you fully visit the left subtree *before* the node, then the node, then the right
subtree, the values come out sorted. No sorting step needed.

```diagram
        3
       / \      in-order = (left of 3) then 3 then (right of 3)
      1   4              = 1, 2         then 3 then 4
       \
        2               emits:  1, 2, 3, 4   (already sorted)
```

## The insight

Do the in-order walk and count. The `k`-th value you emit is the answer. Drive the
walk with an explicit stack so you can **stop the instant the count hits `k`** and
leave the rest of the tree untouched.

```diagram
   stack drives it (dive left, remembering the path):

   push 3, push 1        stack: [3, 1]
   pop 1  -> emit 1  (k: 2->1), then go to 1.right = 2
   push 2                stack: [3, 2]
   pop 2  -> emit 2  (k: 1->0)  == 0  ->  answer is 2, stop
   (node 3 and 4 never visited)
```

The inner dive pushes the whole left spine; popping yields the smallest not-yet-seen
value; after emitting it we pivot into that node's right subtree, which holds the
next-larger values.

## Complexity

- **Time: about the tree height plus k.** We descend the left spine (about the
  height) and then emit `k` values, each with constant stack work. Much better than
  `n log n` when `k` is small.
- **Extra memory: about the height of the tree**, for the stack (the current
  root-to-node path).

## Pitfalls

- Off-by-one: `k` is 1-indexed. Decrement first, then test `k == 0`.
- Forgetting to pivot to `node.right` after emitting — you loop forever or skip
  values.
- Recursing over the whole tree and collecting everything defeats the early stop; the
  explicit stack lets you bail cleanly.
- If the tree changes often and you need many k-th queries, store subtree counts in
  each node to get each lookup down to about the height — a common follow-up.

## Transfer

"In-order turns a BST into a sorted stream" is a workhorse:
[Validate BST / 98](../0098-validate-binary-search-tree/) (the stream must be
increasing),
[Minimum Absolute Difference in BST / 530](https://leetcode.com/problems/minimum-absolute-difference-in-bst/),
and converting a BST to a sorted list. The explicit-stack pattern here is the general
"controllable DFS" you reach for whenever plain recursion can't stop early.
