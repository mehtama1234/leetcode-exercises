# 39. Combination Sum

**Pattern:** Backtracking (build a choice, undo it, try the next)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/combination-sum/

## The problem in plain words

You have a handful of distinct positive numbers and a target. Find every group
of numbers that adds up exactly to the target. You can use the same number as
many times as you like. `[2,2,3]` and `[3,2,2]` count as the *same* group, so we
want each group once, not once per ordering.

## Why this matters

Underneath the puzzle is a classic problem: enumerate every way to combine parts (with repetition) that hits an exact total, while counting each combination once regardless of order. The fundamental operation is a systematic search that builds a choice, undoes it, and moves on — never revisiting the same combination twice.

This is exactly how real systems solve "make change" style problems. Cash registers and vending machines pick coin/bill combinations that sum to an amount. Cutting-stock and bin-packing tools choose piece lengths that add up to a target without waste. Resource allocators and billing systems assemble line items or credits that hit an exact budget. Any "which items sum to N, reuse allowed" question — from crafting recipes to nutrition planners hitting a calorie target — is this shape.

What you're solving for is avoiding an explosion of wasted work: the `start`-index trick keeps the search from re-exploring the same group in every possible order, and the sorted `break` prunes hopeless branches early. Since the space is exponential, that pruning is what keeps it tractable at all.

## Start from the obvious

At each step you're really just asking: "what number do I add next?" The obvious
move is to try every candidate at every step:

```
def build(remaining, path):
    if remaining == 0: record(path); return
    if remaining < 0:  return
    for c in candidates:          # pick ANY candidate
        build(remaining - c, path + [c])
```

This finds all the sums — but it also finds `[2,3]` and `[3,2]` as different
answers, because it's free to pick numbers in any order. It generates a mountain
of duplicates.

## Find the waste

The duplicates come from one thing: allowing every order of the same multiset.
If we could force a single canonical order, each group would be produced exactly
once and all that duplicate work disappears.

The canonical order is easy: **never pick a candidate that comes before the one
you just picked.** Pass a `start` index into the recursion and only loop from
`start` onward. Because reuse is allowed, when we pick candidate `i` the next
call still starts at `i` (we may take it again) — it's `start = i`, not `i + 1`.

## The insight

Sort the candidates first and carry `remaining = target − sum(path)`:

1. `remaining == 0` → record a copy of the current path.
2. Loop `i` from `start` upward. If `candidates[i] > remaining`, **break** —
   the list is sorted, so every later candidate is even bigger and hopeless.
3. Otherwise choose it, recurse with `start = i` and `remaining − candidates[i]`,
   then pop it back off. That pop is the backtrack: it restores the path so the
   next `i` starts from a clean slate.

The `start` rule kills duplicate orderings; the sorted `break` prunes dead
branches early.

## Complexity

- **Time:** Hard to bound tightly. The search tree has depth up to
  `target / min(candidates)` and branches up to `len(candidates)` wide, so it's
  exponential in the worst case — roughly `O(k^(target/min))` explored nodes.
  That's inherent: the number of valid combinations can itself be exponential.
- **Space:** `O(target / min(candidates))` for the recursion depth and the
  current `path`, plus the output list which holds all found combinations.

## Pitfalls

- Recursing with `start = i + 1` instead of `i` — that forbids reuse and turns
  this into a subset problem (see Combination Sum II).
- Appending `path` instead of `path.copy()` — you'd store a reference to a list
  that later mutations empty out; every recorded answer ends up identical.
- Forgetting to sort, then trying to `break` on the size check — without sorting
  a small candidate can appear after a big one, so `break` would miss answers
  (you'd have to `continue` instead, losing the pruning).

## Transfer

The "pass a `start` index so combinations are non-decreasing" trick is the core
of every *pick-a-subset* backtracking problem:
[Combination Sum II / 40](../0040-combination-sum-ii/) (each number used once,
skip duplicates), [Subsets / 78](../0078-subsets/),
[Combinations / 77](../0077-combinations/). Whenever you must enumerate groups
and order-within-a-group doesn't matter, enforce an order with a `start` cursor.
