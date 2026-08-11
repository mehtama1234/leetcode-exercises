# 46. Permutations

**Pattern:** Backtracking (order matters — track what's still available)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/permutations/

## The problem in plain words

Given distinct numbers, return every possible ordering of *all* of them. For
`[1,2,3]` that's the 6 arrangements `[1,2,3]`, `[1,3,2]`, `[2,1,3]`, and so on.
Every number appears in every permutation; what changes is the order.

## Why this matters

The primitive here is **arranging** rather than **selecting**. Subsets asked
"which items?"; permutations ask "in what order?". Those are different explosions:
`n` items have `2^n` subsets but `n!` orderings, and `n!` grows far faster. Knowing
which one your problem is keeps you from accidentally exploring the wrong,
much larger space.

Ordering search is the honest core of real tasks. A scheduler deciding the order
to run jobs, a router evaluating tours through delivery stops (the brute-force
heart of the Traveling Salesman Problem), a compiler trying orderings of
independent optimization passes, a test tool exercising every sequence of events
to shake out order-dependent bugs — all enumerate permutations. Ranking and
tie-breaking logic is "which arrangement is best" over this same space.

What the backtracking template buys is generating all `n!` orderings with only
`O(n)` working memory and no duplicated arrangements, plus a clean place to prune
(you can reject a partial order the instant it violates a constraint, before
committing to the tail).

## Start from the obvious

An ordering is "pick a first element, then a second from what's left, then a
third..." So the honest recursion is: try each unused number in this slot, recurse
to fill the rest, then undo.

```
backtrack():
    if path has all n numbers: record a copy; return
    for each i not yet used:
        used[i] = true; path.push(nums[i])
        backtrack()
        path.pop(); used[i] = false
```

That already is the intended solution — like subsets, the natural recursion is the
right one. The new ingredient is the `used[]` bookkeeping.

## The insight

The difference from subsets is a single idea: **an element, once placed, is off
the table for the rest of this branch.** A subset chooses each element at most once
by *walking forward* through indices; a permutation must be free to place index 5
before index 2, so we can't rely on position — we need an explicit record of
what's still available.

That record is `used[]` (a boolean per index). The template is otherwise
identical:

1. **Choose** — mark `used[i]`, push `nums[i]`.
2. **Explore** — recurse to fill the next slot.
3. **Un-choose** — pop and clear `used[i]`, so the sibling branch can use `i` too.

A leaf is reached when `path` has all `n` numbers — that's a full ordering, so
record a **copy**. The tree has `n` choices at the top, `n-1` at the next level,
down to 1, giving `n!` leaves.

## Complexity

- **Time:** `O(n * n!)` — there are `n!` permutations and copying each into the
  result costs `O(n)`. This is optimal: the output alone is that large.
- **Space:** `O(n)` extra — recursion depth `n`, plus `path` and `used` of size
  `n`. The result list is `O(n * n!)`, which is the required answer.

## Pitfalls

- **Forgetting to clear `used[i]` on the way back up** — later branches then think
  a freed number is still taken, and you lose whole permutations.
- **Recording the live `path`** instead of `path[:]` — all entries alias one list.
- Confusing this with subsets and iterating from a `start` index — that would
  produce combinations (order-insensitive), not orderings.

## Transfer

The "for each unused item" loop with a `used[]` mask is the ordering template.
Add sort-and-skip-equal-siblings to handle repeats
([Permutations II / 47](../0047-permutations-ii/)); swap the "all n" leaf test
for a fixed depth and you're back to [Combinations / 77](../0077-combinations/).
Any "try every sequence / arrangement" problem reduces to this loop.
