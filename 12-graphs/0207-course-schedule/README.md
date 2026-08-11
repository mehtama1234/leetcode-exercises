# 207. Course Schedule

**Pattern:** Topological sort / cycle detection on a directed graph
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/course-schedule/

## The problem in plain words

You have `numCourses` courses. A pair `[a, b]` means "before you can take course
`a`, you must finish course `b`." Can you finish all the courses, or do the
prerequisites tangle up so badly that some courses can never be taken?

## Start from the obvious

Model it as a directed graph: draw an arrow `b -> a` for "finish `b`, then `a`
becomes takeable." Now the question is simple to state: **is there a cycle?** If
courses form a loop — `0` needs `1`, `1` needs `2`, `2` needs `0` — none of them
can ever be the "first" one, so you're stuck. No cycle ⇒ you can finish
everything.

A first instinct is DFS with three colors (unvisited / in-progress / done) and
report a cycle if DFS re-enters an in-progress node. That works. But there's an
approach that mirrors how you'd actually schedule the courses.

## The insight — Kahn's algorithm (peel off what's ready)

For each course, count its **in-degree**: how many prerequisites it's still
waiting on. Courses with in-degree `0` have nothing blocking them — take them now.

Repeat:

1. Take any ready course (in-degree 0) and "finish" it.
2. For every course that depended on it, decrement that course's in-degree by 1 —
   one of its prerequisites is now satisfied.
3. If a course's in-degree hits `0`, it just became ready — queue it.

Keep going until nothing is ready.

- If you finished **all** `numCourses`, a valid order exists → return `True`.
- If courses remain but nothing is ready, those leftovers are exactly a **cycle**:
  each is still waiting on another that never got finished → return `False`.

The finished-count *is* the cycle detector — no separate check needed.

## Find the waste

Naively re-scanning "which courses are ready now?" every round would be `O(V^2)`.
The in-degree counters + a ready-queue let each course become ready exactly once
and each edge be relaxed exactly once, collapsing it to linear.

## Complexity

- **Time:** `O(V + E)` — build the graph and in-degrees in `O(V + E)`, then each
  node is dequeued once and each edge relaxed once.
- **Space:** `O(V + E)` for the adjacency list, in-degree array, and queue.

## Pitfalls

- **Edge direction.** Store `prereq -> course`. Flipping it inverts the whole
  dependency logic.
- **Courses with no prerequisites.** They start at in-degree 0 and must seed the
  queue, or nothing ever begins.
- **The self-loop `[a, a]`.** A course that requires itself is an instant cycle —
  it never reaches in-degree 0. (Kahn handles it automatically.)
- **Reading the result wrong.** The answer is "did we finish *all* of them?", i.e.
  `finished == numCourses`, not "did the queue empty."

## Transfer

Kahn's algorithm gives you both a yes/no cycle test and the actual order.
[Course Schedule II / 210](https://leetcode.com/problems/course-schedule-ii/) asks
for the order (just record the dequeue sequence),
[Alien Dictionary / 269](../0269-alien-dictionary/) topo-sorts letters, and
[Minimum Height Trees / 310](https://leetcode.com/problems/minimum-height-trees/)
peels leaves the same layer-by-layer way.
