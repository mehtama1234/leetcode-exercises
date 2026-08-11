# 78. Subsets

**Pattern:** Backtracking (decision tree over include/exclude)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/subsets/

## The problem in plain words

You get a list of distinct numbers. Give back every subset — every way to pick
some of them, from picking nothing (the empty set) all the way up to picking all
of them. For `[1,2,3]` there are 8. Order doesn't matter, inside a subset or
between subsets.

```diagram
   nums = [1, 2, 3]

   pick nothing        -> []
   pick one            -> [1]  [2]  [3]
   pick two            -> [1,2]  [1,3]  [2,3]
   pick all            -> [1,2,3]
                          8 subsets total
```

## Why this matters

Look at what each element really is: a switch. For every number you make one
yes/no call — take it or leave it. A subset is one setting of all the switches.
So producing every subset is producing every way to flip `n` on/off switches,
and that is why the count is exactly `2^n` — two choices, `n` times over.

That "walk every combination of independent yes/no choices" is the honest core
of real work. Feature-flag and A/B systems reason about which flags are on
together. A build system deciding which optional parts to include, a query
planner weighing which indexes to use, a test tool generating every combination
of settings — all walk the same tree. Any "try every possible selection"
search, like knapsack or a configuration solver, sits on this shape.

What the backtracking version buys you is a way to visit all `2^n` outcomes
while holding only one partial pick in memory at a time, and it's the reusable
template — choose, recurse, un-choose — that every other problem in this chapter
bends rather than rewrites.

## Start from the obvious

A subset is one yes/no choice per element. So the honest first move is: walk the
elements in order, and at each one split into two paths — "leave it out" and
"take it." Draw that splitting and you get a binary decision tree, `n` levels
deep.

```diagram
   include/exclude tree for [1, 2, 3]     (L = leave out, T = take)

                          start
                   L /              \ T
              (no 1)                  (1)
             L /   \ T              L /   \ T
        (--)      (2)          (1)        (1,2)
       L / \T    L / \T       L / \T      L / \T
     [] [3] [2][2,3]  [1][1,3][1,2][1,2,3]
      ^  ^   ^   ^      ^    ^    ^     ^
      the 8 leaves = the 8 subsets
```

Every leaf at the bottom is a finished subset. There are `n` levels and each
node splits in two, so `2^n` leaves — one per subset. This is already the right
shape. Subsets is the rare problem where the plain idea and the intended answer
are the same tree; the job here is to make the template clear before the harder
variants stretch it.

## The insight

The three lines after the split are the backtracking template you will reuse all
chapter long:

1. **Choose** — `path.append(nums[i])`.
2. **Explore** — recurse deeper with that choice in place.
3. **Un-choose** — `path.pop()`, restoring `path` so the *sibling* branch (and
   everything above it) sees a clean slate.

The un-choose is the load-bearing step. `path` is one shared list, changed in
place for speed. Skip the pop and a choice made in one branch leaks into the
next. And because `path` keeps changing, at a leaf you must store a **copy**
(`path[:]`), never the live list.

```diagram
   path as one shared list, walking take-1 then take-2 then back up:

   choose 1   path=[1]          <- Choose
     choose 2 path=[1,2]        <- Choose (deeper)
       leaf   record [1,2]
     pop      path=[1]          <- Un-choose: sibling sees clean [1]
   pop        path=[]           <- Un-choose: back to the top
```

No pruning happens here and none is possible — every leaf is a valid answer, so
there is no dead branch to cut. That's what makes this the clean baseline: the
later problems in the chapter are this same tree with a branch-cutting rule
added.

## Complexity

- **Time: about `n * 2^n`.** There are `2^n` subsets, and copying each finished
  one into the result costs up to `n`. You cannot beat `2^n` — the output itself
  is that big.
- **Extra memory: about `n`.** The recursion goes `n` deep and `path` holds at
  most `n` items. The returned list is `n * 2^n`, but that's the answer you were
  asked for, not overhead.

## Pitfalls

- **Storing the live `path`** instead of a copy — every entry in `result` then
  points at the same list, which is empty after all the pops.
- **Forgetting the `pop()`** — choices from one branch contaminate the next.
- Thinking you need a special rule to "add the empty set" — you don't; the branch
  that leaves out every element lands on a leaf with an empty path for free.

## Transfer

The include/exclude tree with choose–recurse–un-choose is the spine of this whole
chapter. With duplicates you sort and skip repeats
([Subsets II / 90](../0090-subsets-ii/)); with a fixed size you cut branches too
short to finish ([Combinations / 77](../0077-combinations/)); with a target you
cut branches by a running sum
([Combination Sum / 39](../../09-backtracking/0039-combination-sum/)). Learn this
template once and the rest are edits to it.
