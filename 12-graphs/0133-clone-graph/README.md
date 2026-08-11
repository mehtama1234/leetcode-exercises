# 133. Clone Graph

**Pattern:** Graph traversal (DFS/BFS) + a "seen" map for deep copy
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/clone-graph/

## The problem in plain words

You're handed one node of a connected, undirected graph. Build a **completely
separate copy** of the whole graph: same values, same connections, but every node
is a brand-new object. Editing the copy must never touch the original.

## Why this matters

Underneath, this is **deep-copying a pointer-linked structure that has sharing and cycles** — the fundamental operation is "traverse a graph while remembering, by identity, which nodes you've already rebuilt." The `original -> clone` map is doing two jobs at once: cycle guard and wiring table.

That exact move is everywhere real systems copy or move object graphs. Language runtimes and libraries implement it as `deepcopy` / structured clone / snapshotting. Serializers (JSON, protobuf, ORM detach) walk an object graph and must handle shared references and back-pointers without looping. Garbage collectors and heap-copying collectors trace live objects the same way, marking each once. Version-control and undo systems snapshot linked state.

What you're really solving for is **termination and correctness on a structure you can't safely re-walk**: without the seen-map you either loop forever on a cycle or silently duplicate shared nodes and corrupt the shape. The map buys `O(1)` "have I built this yet?" so the whole copy is one linear pass instead of an exponential re-explosion.

## Start from the obvious

"Copy the graph" sounds like "walk the graph and make a new node for each node I
see." So you reach for DFS:

```
def dfs(node):
    copy = Node(node.val)
    for nb in node.neighbors:
        copy.neighbors.append(dfs(nb))   # <-- trouble
    return copy
```

This is broken in two ways. Because the graph has **cycles**, `dfs` recurses back
into a node it's already inside and loops forever. And even without cycles, two
different nodes that both point at the same neighbor would each build their own
copy of it — so the clone has duplicate nodes and the wrong shape.

## The insight

Both bugs have the same fix: **remember which originals you've already cloned.**
Keep a map `original node -> its clone`.

1. When you enter a node, first check the map. If its clone already exists, return
   that clone immediately — don't rebuild, don't recurse.
2. Otherwise create the clone and **put it in the map before** recursing into
   neighbors.

That "record before recursing" ordering is the whole game. It means the second
time you arrive at any node (which will happen — undirected edges and cycles
guarantee it) the clone is already there, so the recursion bottoms out. The map
is simultaneously your visited-set (stops infinite loops) and your wiring table
(so every edge points at the *one* shared clone, not a fresh duplicate).

## Find the waste

Without the map you re-clone shared neighbors over and over and never terminate on
a cycle. The map turns "have I built this node's copy yet?" into an `O(1)` lookup,
so each node is created exactly once and each edge is followed exactly once.

## Complexity

- **Time:** `O(V + E)` — every node is cloned once (V) and every edge is walked
  once to wire up a neighbor (E, counted twice for undirected but still linear).
- **Space:** `O(V)` — the map holds one entry per node, plus the recursion stack
  which is at most `O(V)` deep.

## Pitfalls

- **Forgetting the map** → infinite recursion on any cycle, or duplicate nodes.
- **Adding to the map too late** (after recursing) → the cycle re-enters before
  the clone is registered, and you still loop forever. Register *first*.
- **`None` input.** An empty graph must return `None`, not crash.
- **Shallow copy.** Copying the neighbor *list* but reusing the same Node objects
  isn't a deep copy — the "clone" would share nodes with the original.

## Transfer

The "traverse + memoize by identity" move copies any linked structure with sharing
or cycles: deep-copying a
[linked list with random pointers / 138](https://leetcode.com/problems/copy-list-with-random-pointer/),
serializing/deserializing a graph, or any DFS where you must not revisit a node —
see [Number of Islands / 200](../0200-number-of-islands/) for the visited-marker
idea and [Course Schedule / 207](../0207-course-schedule/) for cycle-aware DFS.
