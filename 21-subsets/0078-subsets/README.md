# 78. Subsets

**Pattern:** Backtracking (decision tree over include/exclude)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/subsets/

## The problem in plain words

Given a list of distinct numbers, produce every subset — every way to pick some
of them, from picking none (the empty set) to picking all of them. For `[1,2,3]`
there are 8 such subsets. Order of the subsets, and order inside each subset,
doesn't matter.

## Why this matters

Under this puzzle is one primitive operation: *enumerate every combination of
independent yes/no choices.* Each element is a switch that is on or off, and a
subset is one setting of all the switches. Producing the power set is producing
every configuration of `n` boolean flags — which is why there are exactly `2^n`
of them.

That enumeration is the honest core of real work. Feature-flag and A/B systems
reason about the space of on/off combinations. A build system exploring which
optional components to include, a query planner deciding which indexes to use, a
test harness generating every combination of settings — all walk the same tree.
Any "try every possible selection" search (knapsack, configuration solvers) has
this shape at its base.

What the backtracking solution buys is a way to visit all `2^n` outcomes using
only `O(n)` working memory instead of building them all up in a giant list at
once, and — crucially — it's the reusable template (choose, recurse, un-choose)
that every sibling problem in this chapter reshapes rather than reinvents.

## Start from the obvious

A subset is one yes/no choice per element. So the honest first thought is: walk
the elements, and at each one branch into "leave it out" and "take it".

```
backtrack(i):
    if i == n: record a copy of path; return
    backtrack(i+1)              # leave nums[i] out
    path.push(nums[i])         # take nums[i]
    backtrack(i+1)
    path.pop()
```

That already *is* the optimal structure — subsets is the one problem where the
brute force and the intended solution are the same shape. The whole point here is
to make the template explicit before the harder variants bend it.

## The insight

The three lines after the branch are the backtracking template you will reuse all
chapter long:

1. **Choose** — `path.append(nums[i])`.
2. **Explore** — recurse deeper with that choice in place.
3. **Un-choose** — `path.pop()`, restoring `path` so the *sibling* branch (and
   everything above) sees a clean slate.

The un-choose is the load-bearing step. `path` is one shared list mutated in
place for speed; without the pop, a choice from one branch would leak into the
next. And because `path` keeps changing, you must record a **copy** (`path[:]`)
at a leaf, never the live list.

The decision tree has depth `n` and branches 2 ways, so it has `2^n` leaves — one
per subset. No pruning is possible or needed: every leaf is a valid answer.

## Complexity

- **Time:** `O(n * 2^n)` — there are `2^n` subsets, and copying each one into the
  result costs up to `O(n)`. You cannot beat `2^n`; the output itself is that big.
- **Space:** `O(n)` extra beyond the output — the recursion is `n` deep and
  `path` holds at most `n` items. The returned list is `O(n * 2^n)`, but that's
  the required answer, not overhead.

## Pitfalls

- **Appending the live `path`** instead of a copy — every entry in `result` then
  ends up as the same (empty, after all pops) list.
- **Forgetting the `pop()`** — choices from one branch contaminate the next.
- Thinking you need a separate rule to "add the empty set" — you don't; the
  branch that leaves out every element reaches a leaf with an empty path for free.

## Transfer

The include/exclude tree with choose–recurse–un-choose is the spine of this whole
chapter. With duplicates you sort and skip repeats
([Subsets II / 90](../0090-subsets-ii/)); with a fixed size you prune by depth
([Combinations / 77](../0077-combinations/)); with a target you prune by a
running sum ([Combination Sum / 39](../../09-backtracking/0039-combination-sum/)).
Learn this template once and the rest are edits to it.
