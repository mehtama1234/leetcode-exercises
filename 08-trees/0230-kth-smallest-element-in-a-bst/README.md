# 230. Kth Smallest Element in a BST

**Pattern:** In-order traversal of a BST (iterative, early-stop)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/kth-smallest-element-in-a-bst/

## The problem in plain words

You have a binary search tree and a number `k`. Return the `k`-th smallest value
in it (counting from 1, so `k=1` is the minimum).

## Why this matters

The deeper problem is **exploiting order that's already stored** to answer a rank
query without re-sorting, and to **stop as soon as you have the answer**. An
in-order walk of a BST yields values in sorted order lazily, so the fundamental
operation is "stream the sorted sequence and halt at the k-th element."

This is exactly what ordered indexes do in real systems. A database B-tree index
answers `ORDER BY ... LIMIT k` or `OFFSET/LIMIT` pagination by walking the index
in key order and stopping early — it never sorts the table. "Top-k" and
percentile/median queries over a sorted structure, leaderboard rank lookups, and
range scans all lean on the same "structure already encodes order, just walk it"
idea.

What you're solving for is **avoiding the wasteful O(n log n) sort and the full
traversal**: the good solution is O(h + k) — it touches only the nodes it must
and quits. And if the tree gets many such queries or frequent updates, augmenting
nodes with subtree counts turns each lookup into O(h), the classic
space-for-repeated-speed trade.

## Start from the obvious

The blunt approach: collect every value, sort it, take index `k-1`.

```
vals = all values in the tree
vals.sort()
return vals[k-1]
```

That's `O(n log n)` and completely ignores that the tree is *already a search
tree* — its structure encodes order for free.

## Find the waste

Two wasteful things happen above. First, we sort values that the BST already
keeps ordered. Second, we process the entire tree even though we only need the
first `k` values in order.

The fix for the first: an **in-order traversal** of a BST emits values in sorted
order automatically. Why? At any node, everything in the left subtree is smaller,
so if you fully visit the left subtree *before* the node, then the node, then the
right subtree, you produce values from smallest to largest. No sorting needed.

## The insight

Do an in-order walk and simply count. The `k`-th value you emit is the answer.
And because we control the walk with an explicit stack, we can **stop the moment
the count hits `k`** — no need to touch the rest of the tree.

```
stack = []
node = root
while stack or node:
    while node:            # dive left, remembering the path
        stack.push(node); node = node.left
    node = stack.pop()     # smallest not-yet-visited node
    k -= 1
    if k == 0: return node.val
    node = node.right      # now the right subtree
```

The inner `while` pushes the whole left spine; popping then yields the smallest
remaining value; after emitting it we pivot into its right subtree, which holds
the next-larger values.

## Complexity

- **Time:** `O(h + k)` — we descend the left spine (`O(h)`) and then emit `k`
  values, each involving amortized `O(1)` stack work. Far better than
  `O(n log n)` when `k` is small.
- **Space:** `O(h)` for the stack (the current root-to-node path).

## Pitfalls

- Off-by-one: `k` is 1-indexed. Decrement first, then test `k == 0`.
- Forgetting to pivot to `node.right` after emitting, which would loop forever or
  skip values.
- Recursing over the whole tree and collecting all values defeats the early-stop
  benefit; the iterative stack lets you bail early cleanly.
- If the tree is modified often and you need many `k`-th queries, augment nodes
  with subtree counts for `O(h)` per query — a common follow-up.

## Transfer

"In-order traversal turns a BST into a sorted stream" is a workhorse:
[Validate BST / 98](../0098-validate-binary-search-tree/) (the stream must be
increasing),
[Minimum Absolute Difference in BST / 530](https://leetcode.com/problems/minimum-absolute-difference-in-bst/),
and converting a BST to a sorted list. The iterative stack pattern here is the
general "controllable DFS" you reach for whenever recursion can't stop early.
