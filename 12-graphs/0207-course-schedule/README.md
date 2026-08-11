# 207. Course Schedule

**Pattern:** Topological sort / spotting a loop in a directed graph
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/course-schedule/

## The problem in plain words

You have `numCourses` courses. A pair `[a, b]` means "before you can take course
`a`, you must finish course `b`." Can you finish every course, or do the
prerequisites tangle up so badly that some courses can never be taken?

```diagram
   [1,0] means: finish 0, then 1 is allowed

        finish 0
           |
           v
          (1)          -> take 0, then 1.  possible.

   but if 0 needs 1 AND 1 needs 0:

        (0) --> (1)
         ^       |
         |_______|          neither can go first.  impossible.
```

## Why this matters

Draw an arrow from each prerequisite to the course it unlocks and you have a
directed graph. The real question becomes one word: **is there a loop?** If courses
chain back on themselves — 0 needs 1, 1 needs 2, 2 needs 0 — none of them can ever
be the first one, and you are stuck. No loop means you can finish everything.

The reusable idea is **topological sort**: put dependent tasks in an order where
everything comes after the things it needs, and flag when no such order exists.
Build tools (Make, Bazel, npm) sort targets so each is built after what it depends
on, and error out on a dependency loop. Spreadsheets recompute cells in dependency
order and shout "circular reference" the same way. Schedulers run pipeline stages
in order; package managers order installs and refuse cyclic requirements.

What you are solving for is a valid order **plus** a cheap, honest "is this even
possible?" verdict — in a single pass.

## Start from the obvious

Model it as the directed graph above: an arrow `b -> a` for "finish `b`, then `a`
opens up." The question is now "does this graph have a loop?"

One instinct is to walk the graph marking nodes as in-progress, and shout "loop!"
if the walk re-enters a node still marked in-progress. That works. But there is a
second approach that mirrors how you would actually schedule the courses by hand,
so let's build that one.

## The insight — peel off whatever is ready

For each course, count its **in-degree**: how many prerequisites it is still
waiting on. Courses with in-degree `0` have nothing blocking them — take those now.
Then repeat:

1. Take a ready course (in-degree 0) and mark it finished.
2. For every course that depended on it, drop that course's in-degree by 1 — one of
   its prerequisites is now done.
3. If a course's in-degree hits `0`, it just became ready — add it to the queue.

Keep going until nothing is ready.

```diagram
   courses 0..3,  edges: 0->1, 0->2, 1->3, 2->3   (diamond)

   in-degree:  0:0   1:1   2:1   3:2
   ready queue: [0]                       finished = 0

   take 0  -> drop 1 and 2   in-deg 1:0, 2:0    ready: [1,2]   finished=1
   take 1  -> drop 3         in-deg 3:1         ready: [2]     finished=2
   take 2  -> drop 3         in-deg 3:0         ready: [3]     finished=3
   take 3                                       ready: []      finished=4

   finished 4 == numCourses 4   ->  YES, order exists
```

Now watch a loop stall the same machine:

```diagram
   edges: 0->1, 1->2, 2->0    (a 3-cycle)

   in-degree:  0:1   1:1   2:1
   ready queue: []                    <- nothing starts at 0

   the queue is empty on step one.  finished = 0, not 3.  ->  NO
```

The finished-count **is** the loop detector. If you finished all `numCourses`, an
order exists. If courses remain but nothing is ready, those leftovers are exactly a
loop — each still waiting on another that never got finished.

## Find the waste

Re-scanning "which courses are ready now?" every round would cost about V × V steps
(each round rescans all courses). The in-degree counters plus a ready-queue let
each course become ready exactly once and each edge be handled exactly once, which
collapses the work to grow in step with courses + prerequisites.

## Complexity

- **Time: about V + E steps** (courses plus prerequisite pairs). Building the graph
  and in-degrees is linear, then each course leaves the queue once and each edge is
  handled once.
- **Extra memory: about V + E** for the graph, the in-degree array, and the queue.

## Pitfalls

- **Edge direction.** Store `prereq -> course`. Flip it and the whole dependency
  logic inverts.
- **Courses with no prerequisites.** They start at in-degree 0 and must seed the
  queue, or nothing ever begins.
- **The self-loop `[a, a]`.** A course that requires itself never reaches in-degree
  0 — an instant loop. The counting handles it on its own.
- **Reading the result wrong.** The answer is "did we finish *all* of them?", i.e.
  `finished == numCourses`, not "did the queue empty."

## Transfer

This peel-off machine gives both a yes/no loop test and the actual order.
[Course Schedule II / 210](https://leetcode.com/problems/course-schedule-ii/) asks
for the order (just record the take-off sequence),
[Alien Dictionary / 269](../0269-alien-dictionary/) sorts letters this way, and
[Minimum Height Trees / 310](https://leetcode.com/problems/minimum-height-trees/)
peels leaves layer by layer the same way.
