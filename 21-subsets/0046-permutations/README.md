# 46. Permutations

**Pattern:** Backtracking (order matters — track what's still available)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/permutations/

## The problem in plain words

Given distinct numbers, return every ordering of *all* of them. For `[1,2,3]`
that's the 6 arrangements `[1,2,3]`, `[1,3,2]`, `[2,1,3]`, and so on. Every
number appears in every answer; what changes is the order they sit in.

```diagram
   nums = [1, 2, 3]

   [1,2,3]  [1,3,2]  [2,1,3]  [2,3,1]  [3,1,2]  [3,2,1]
   3 choices for the first slot x 2 for the second x 1 for the last = 6
```

## Why this matters

The move here is **arranging** rather than **selecting**. Subsets asked "which
items?"; permutations ask "in what order?". Those are different explosions: `n`
items have `2^n` subsets but `n!` orderings, and `n!` grows far faster. Knowing
which one your problem is keeps you from wandering into the much larger space by
mistake.

Ordering search is the honest core of real tasks. A scheduler deciding the order
to run jobs, a router weighing tours through delivery stops (the brute-force
heart of the Traveling Salesman Problem), a compiler trying orders of independent
optimization passes, a test tool exercising every sequence of events to shake out
order-dependent bugs — all enumerate permutations.

What the template buys is generating all `n!` orderings while holding one partial
order in memory, with no duplicate arrangements, plus a clean place to cut a
branch (you can reject a partial order the instant it breaks a rule, before
filling the rest).

## Start from the obvious

An ordering is "pick a first number, then a second from what's left, then a
third..." So the honest recursion is: try each unused number in this slot,
recurse to fill the rest, then undo.

```diagram
   choice tree for [1,2,3]  (each branch = "which unused number goes next")

                      _  _  _
          1 /          2 |          \ 3
        1 _ _         2 _ _          3 _ _
       2 / \ 3       1 / \ 3        1 / \ 2
     1 2 _ 1 3 _   2 1 _ 2 3 _    3 1 _ 3 2 _
       |     |       |     |        |     |
    [1,2,3][1,3,2][2,1,3][2,3,1] [3,1,2][3,2,1]

   fan-out shrinks 3 -> 2 -> 1 down the levels, giving 3! = 6 leaves
```

That already is the intended solution — like subsets, the natural recursion is
the right one. The new ingredient is a way to remember which numbers are still
free.

## The insight

The one difference from subsets: **an element, once placed, is off the table for
the rest of this branch.** Subsets picked each element at most once by *walking
forward* through indices. A permutation must be free to place index 5 before
index 2, so position can't carry that information — you need an explicit record
of what's still available.

That record is `used[]`, one boolean per index. The template is otherwise the
same:

1. **Choose** — mark `used[i]`, push `nums[i]`.
2. **Explore** — recurse to fill the next slot.
3. **Un-choose** — pop and clear `used[i]`, so the sibling branch can use `i` too.

```diagram
   used[] walking the branch that builds [2,1,3], then unwinding:

   pick 2   path=[2]     used=[_,T,_]     <- Choose
     pick 1 path=[2,1]   used=[T,T,_]     <- Choose
       pick 3 path=[2,1,3] used=[T,T,T]   -> leaf: record [2,1,3]
       pop   path=[2,1]   used=[T,T,_]    <- Un-choose (clear 3)
     pop     path=[2]     used=[_,T,_]    <- Un-choose (clear 1)
   pop       path=[]      used=[_,_,_]    <- Un-choose (clear 2)
```

A leaf is reached when `path` holds all `n` numbers — a full ordering, so record
a **copy**. There's no pruning in the plain version: every complete path is a
valid permutation. (Permutations II adds the first real cut.)

## Complexity

- **Time: about `n * n!`.** There are `n!` permutations and copying each into the
  result costs about `n`. This is the best possible: the output alone is that big.
- **Extra memory: about `n`** — recursion depth `n`, plus `path` and `used`, each
  of size `n`. The result list is `n * n!`, the answer itself.

## Pitfalls

- **Forgetting to clear `used[i]` on the way back up** — later branches then think
  a freed number is still taken, and you lose whole permutations.
- **Storing the live `path`** instead of `path[:]` — every entry points at one
  shared list.
- Confusing this with subsets and looping from a `start` index — that produces
  combinations (order-blind), not orderings.

## Transfer

The "for each unused item" loop with a `used[]` mask is the ordering template.
Add sort-and-skip-equal-siblings to handle repeats
([Permutations II / 47](../0047-permutations-ii/)); swap the "all n" leaf test
for a fixed depth and you're back to [Combinations / 77](../0077-combinations/).
Any "try every sequence / arrangement" problem reduces to this loop.
