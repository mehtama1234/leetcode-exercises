# 133. Clone Graph

**Pattern:** Graph traversal + a "seen" map (copy each node exactly once)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/clone-graph/

## The problem in plain words

You are handed one node of a connected, undirected graph. Build a **completely
separate copy** of the whole thing: same values, same connections, but every node
is a brand-new object. Editing the copy must never touch the original.

```diagram
   original:                 copy you must build:

      (1)---(2)                (1')---(2')
       |     |                  |      |
      (4)---(3)                (4')---(3')

   same shape, same links, but every (x') is a NEW object
```

## Why this matters

Strip the story away and the job is: **copy a structure made of linked objects
that has sharing and loops in it.** The graph above has a loop (1→2→3→4→1), and
undirected edges mean node 2 points back at node 1 while node 1 points at node 2.

The one reusable idea is: **walk the structure while remembering, node by node,
which ones you have already rebuilt.** A map from `original -> its copy` does two
jobs at once. It stops you from looping forever, and it is your wiring table so
every edge lands on the *one* shared copy instead of a fresh duplicate.

This exact move runs whenever real systems copy or move object graphs.
`deepcopy` and structured-clone do it. Serializers (JSON, protobuf) walk an object
graph and must handle shared references and back-pointers without spinning.
Garbage collectors trace live objects the same way, marking each once.

## Start from the obvious

"Copy the graph" sounds like "walk it and make a new node for each node I see." So
you reach for a walk that recurses into every neighbor:

```diagram
   copy(node):
       new = Node(node.val)
       for nb in node.neighbors:
           new.neighbors.append( copy(nb) )   <- trouble
       return new
```

This breaks in two ways. Because there is a **loop**, `copy` walks back into a node
it is already inside, and never stops. And even with no loop, two nodes that both
point at the same neighbor each build their own copy of it — so the result has
duplicate nodes and the wrong shape.

## The insight

Both bugs have the same fix: **remember which originals you have already copied.**
Keep a map `original node -> its copy`.

1. When you enter a node, check the map first. If its copy already exists, hand
   that back right away — don't rebuild, don't recurse.
2. Otherwise make the copy and **put it in the map before** you recurse into
   neighbors.

That "record before recursing" order is the whole game. The second time you arrive
at any node — and you will, since loops and undirected edges guarantee it — its
copy is already sitting in the map, so the walk bottoms out instead of spinning.

```diagram
   start at 1, map = {}

   at 1: not in map -> make 1', map = {1:1'}, then visit its neighbors
     at 2: not in map -> make 2', map = {1:1', 2:2'}, visit its neighbors
       at 1: IN MAP -> return 1'   (loop closed, no infinite spin)
       at 3: not in map -> make 3', ... and so on
     back at 1: neighbor 4 similar

   every node made once; every edge points at the shared copy
```

Checking the map *before* making a copy is what turns a loop from a trap into a
one-line "oh, already did that." The map is your visited-set and your wiring table
at the same time.

## Find the waste

Without the map you re-copy shared neighbors again and again and never stop on a
loop. The map turns "have I built this node's copy yet?" into a one-step lookup, so
each node is made exactly once and each edge is followed exactly once.

## Complexity

- **Time: about V + E steps** (nodes plus edges). Every node is copied once, and
  every edge is walked once to wire up a neighbor.
- **Extra memory: about V.** The map holds one entry per node, plus the recursion
  stack, which is at most V deep.

## Pitfalls

- **Forgetting the map** → the walk spins forever on any loop, or makes duplicate
  nodes.
- **Adding to the map too late** (after recursing) → the loop re-enters before the
  copy is registered, and you still spin. Register *first*.
- **`None` input.** An empty graph must return `None`, not crash.
- **Shallow copy.** Copying the neighbor *list* but reusing the same Node objects
  isn't a deep copy — the "copy" would share nodes with the original.

## Transfer

The "walk + remember by identity" move copies any linked structure with sharing or
loops: deep-copying a
[linked list with random pointers / 138](https://leetcode.com/problems/copy-list-with-random-pointer/),
serializing a graph, or any walk where you must not revisit a node — see
[Number of Islands / 200](../0200-number-of-islands/) for the visited-marker idea
and [Course Schedule / 207](../0207-course-schedule/) for loop-aware traversal.
