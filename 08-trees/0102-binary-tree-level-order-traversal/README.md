# 102. Binary Tree Level Order Traversal

**Pattern:** Breadth-first search (BFS) with a queue
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/binary-tree-level-order-traversal/

## The problem in plain words

Read the tree row by row, top to bottom. The root is the first row; its children
are the second row; their children the third; and so on. Return each row as its
own list, left to right.

## Why this matters

The real problem is **exploring a structure in order of distance from a start
point, in distinct waves** — processing everything one hop away before anything
two hops away, while keeping the layers separate. The fundamental operation is
breadth-first expansion with a queue, snapshotting each frontier before it grows.

This is the backbone of a lot of real work. Shortest-path and "fewest steps"
searches (unweighted maps, puzzle solvers, network hop counts) are BFS. Web
crawlers and dependency resolvers fan out level by level. Garbage collectors
sweep reachable objects in waves; social features compute "friends, then
friends-of-friends" as distinct rings. Any UI that renders a tree depth-by-depth
uses this grouping.

What you're solving for is **visiting each node exactly once, O(n) time, while
preserving layer boundaries** — the per-level snapshot is what lets you answer
"how far?" and "what's on this ring?" without re-walking the tree. Memory is
bounded by the widest level, the honest cost of going breadth-first.

## Start from the obvious

To visit a tree "by rows", you naturally want a queue: process the root, then its
children, then their children — first in, first out. That's plain BFS:

```
queue = [root]
while queue:
    node = queue.pop(0)
    visit(node)
    queue.push(node.left, node.right)
```

But plain BFS gives you one flat stream of nodes. The problem wants them
**grouped** by row, and a flat queue doesn't tell you where one row ends and the
next begins.

## The insight

The boundary between levels is knowable if you look at the right moment. At the
start of each round, **every node currently in the queue belongs to the same
level** — because we only ever added a level's children after finishing that
level. So snapshot the queue's length first:

```
level_size = len(queue)   # exactly the nodes on this row
```

Then pop exactly `level_size` nodes, gather their values into one sublist, and
push their children. Those children are now the entire next row, waiting for the
next iteration. Freezing `level_size` *before* enqueuing children is the whole
trick — it stops this row's kids from being counted as part of this row.

## Complexity

- **Time:** `O(n)` — each node is enqueued and dequeued exactly once.
- **Space:** `O(w)` where `w` is the widest level (the max the queue holds), plus
  `O(n)` for the output. In the worst case (a full bottom row) `w ≈ n/2`.

## Pitfalls

- Not snapshotting `level_size` first — if you loop `while queue` and append
  children inside, you'll merge all rows into one.
- Forgetting the empty-tree case; it must return `[]`, not `[[]]`.
- Using a plain `list.pop(0)` in a hot path is `O(n)`; `collections.deque` gives
  `O(1)` pops. Fine for teaching clarity here, worth knowing at scale.

## Transfer

The "freeze the level size, then drain that many" pattern is the backbone of
level-aware BFS:
[Zigzag Level Order / 103](https://leetcode.com/problems/binary-tree-zigzag-level-order-traversal/)
(reverse alternate rows),
[Right Side View / 199](https://leetcode.com/problems/binary-tree-right-side-view/)
(keep the last node of each row), and
[Average of Levels / 637](https://leetcode.com/problems/average-of-levels-in-binary-tree/).
