# 269. Alien Dictionary

**Pattern:** Build a graph from constraints + topological sort
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/alien-dictionary/

## The problem in plain words

Some alien language uses the same letters as us but in a **different alphabetical
order**. You're handed a list of their words that are already sorted by *their*
rules. Figure out an order of the letters that's consistent with that sorting. If
no order can explain the list, return `""`.

## Why this matters

Underneath the aliens, this is **recovering one global order from many local pairwise comparisons** — and detecting when those comparisons contradict each other. The fundamental operation is: turn each "X before Y" fact into a directed edge, then topologically sort.

This shows up wherever a total order has to be reconstructed from partial evidence. Version and dependency resolvers infer a consistent install order from many "A must come before B" constraints and report a conflict when they form a cycle. Ranking systems (sports standings, tournament seeding, preference aggregation / "rank choice" merges) build a global order from head-to-head results. Build systems derive compile order from per-file `#include`/import edges. Even schema migration tools order migrations from their stated dependencies.

What you're solving for is **a consistent order plus a clean "impossible" signal**, in time linear in the input. The subtle payoff is honesty: a cycle means the constraints genuinely contradict (`x<z` and `z<x`), and the prefix rule (`"abc"` before `"ab"`) catches evidence that no order could ever explain.

## Start from the obvious

You can't look at a single word and learn much. The information is *between*
adjacent words: since the list is sorted, word `i` comes before word `i+1`, and a
dictionary sort compares them letter by letter until the first difference. That
first differing letter is the whole story.

```
"wrt", "wrf"   -> first differ at position 2: 't' before 'f'
"wrf", "er"    -> first differ at position 0: 'w' before 'e'
"er",  "ett"   -> first differ at position 1: 'r' before 't'
```

Each adjacent pair yields **one** fact: "letter X comes before letter Y." Letters
matching before the difference tell you nothing; letters after it are irrelevant
to this pair.

## The insight

Those "X before Y" facts are directed edges in a graph over the letters. A valid
alien alphabet is precisely a **topological sort** of that graph — an ordering
where every edge points forward. So:

1. **Seed** the graph with every letter that appears (even letters with no
   constraints must appear in the answer).
2. For each adjacent word pair, find the first differing letter and add edge
   `a -> b`.
3. **Topologically sort** (Kahn's algorithm: repeatedly emit a letter with no
   remaining "must come after" constraints).

If the sort can't place every letter, there's a **cycle** — the constraints
contradict each other (e.g. `x < z` and `z < x`) — so return `""`.

## Find the trap (the prefix rule)

There's one non-obvious inconsistency the letter-comparison misses. If an earlier
word is a **prefix** of a later word, that's fine (`"ab"` before `"abc"`). But the
reverse — a longer word before its own prefix, like `"abc"` before `"ab"` — is
**impossible** in any sort order, because a prefix always sorts first. When two
adjacent words match all the way up to the shorter one's length and the earlier is
longer, return `""` immediately. Forgetting this is the classic wrong answer here.

## Complexity

- **Time:** `O(C)` where `C` is the total number of characters across all words —
  each character is examined a constant number of times to build edges, and the
  topo sort is linear in letters + edges (both bounded by the alphabet and pairs).
- **Space:** `O(1)` in the alphabet size (at most 26 letters and 26² edges), i.e.
  `O(U + E)` in the number of distinct letters and derived edges.

## Pitfalls

- **The prefix inconsistency** above — the most-missed case.
- **Only the first difference matters.** After the first differing position,
  `break`; later letters carry no ordering info for that pair.
- **Seed all letters.** A letter appearing in no constraint still belongs in the
  output; initialize the graph from *every* character first.
- **Cycle = invalid.** If the topo sort emits fewer than all letters, return `""`.
- **Duplicate edges.** Adding the same `a -> b` twice would inflate the in-degree
  and break the sort — guard with a set before incrementing.

## Transfer

"Turn ordering constraints into edges, then topo-sort" is the reusable engine,
shared with [Course Schedule / 207](../0207-course-schedule/) and
[Course Schedule II / 210](https://leetcode.com/problems/course-schedule-ii/)
(finish order),
[Sequence Reconstruction / 444](https://leetcode.com/problems/sequence-reconstruction/),
and any "recover a global order from local comparisons" task.
