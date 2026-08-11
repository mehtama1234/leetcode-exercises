# 102. Binary Tree Level Order Traversal

**Pattern:** Breadth-first search with a queue, one level per round
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/binary-tree-level-order-traversal/

## The problem in plain words

Read the tree row by row, top to bottom. The root is the first row, its children the
second row, their children the third, and so on. Return each row as its own list,
left to right.

```diagram
        3            row 0: [3]
       / \           row 1: [9, 20]
      9  20          row 2: [15, 7]
        /  \
      15    7        answer: [[3], [9,20], [15,7]]
```

## Why this matters

The real problem is *exploring a structure in waves, by distance from a start point*
— finish everything one hop away before touching anything two hops away, while
keeping the waves separate. A queue does the fanning out; the trick is snapshotting
each wave before it grows.

This is the backbone of a lot of work. "Fewest steps" searches over unweighted maps
and puzzles are BFS. Web crawlers and dependency resolvers fan out level by level.
Social features compute "friends, then friends-of-friends" as separate rings. Any UI
that renders a tree depth by depth uses this grouping.

What you buy is visiting each node once while keeping the layer boundaries. The
per-level snapshot is what lets you answer "how far?" and "what's on this ring?"
without re-walking. Memory is bounded by the widest level — the honest cost of going
breadth-first.

## Start from the obvious

To visit "by rows" you reach for a queue: handle the root, then its children, then
their children — first in, first out.

```diagram
   queue: [3]
   pop 3, push 9, 20     -> visited: 3        queue: [9, 20]
   pop 9, push (none)    -> visited: 3 9      queue: [20]
   pop 20, push 15, 7    -> visited: 3 9 20   queue: [15, 7]
   ...
```

But plain BFS gives one flat stream: `3, 9, 20, 15, 7`. The problem wants them
**grouped** by row, and a flat queue never tells you where one row ends.

## The insight

The boundary between rows is knowable if you look at the right instant. At the start
of each round, **every node in the queue belongs to the same row** — because we only
ever added a row's children after finishing that row. So freeze the queue's length
first, then drain exactly that many.

```diagram
   round starts, queue = [9, 20]   -> level_size = 2  (this whole row)

   pop 9  -> row=[9],     push its children
   pop 20 -> row=[9,20],  push 15, 7
   (drained 2, stop this round)     -> emit [9, 20]

   queue now = [15, 7]   <- exactly the next row, waiting
```

Freezing `level_size` *before* pushing children is the whole move — it stops this
row's kids from being counted as part of this row.

## Complexity

- **Time: about n steps** — each node is enqueued and dequeued once.
- **Extra memory: about the widest level** (the most the queue holds at once), plus
  the output list. In the worst case a full bottom row makes that about n/2.

## Pitfalls

- Not freezing `level_size` first — if you loop `while queue` and append children
  inside, all rows merge into one.
- Forgetting the empty tree: it must return `[]`, not `[[]]`.
- `list.pop(0)` is about n work each time; `collections.deque` pops in constant
  time. Fine for teaching clarity, worth knowing at scale.

## Transfer

"Freeze the level size, then drain that many" is the backbone of level-aware BFS:
[Zigzag Level Order / 103](https://leetcode.com/problems/binary-tree-zigzag-level-order-traversal/)
(reverse alternate rows),
[Right Side View / 199](https://leetcode.com/problems/binary-tree-right-side-view/)
(keep the last node of each row), and
[Average of Levels / 637](https://leetcode.com/problems/average-of-levels-in-binary-tree/).
