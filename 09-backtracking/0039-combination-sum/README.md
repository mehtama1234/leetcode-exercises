# 39. Combination Sum

**Pattern:** Backtracking (make a choice, undo it, try the next)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/combination-sum/

## The problem in plain words

You have a handful of distinct positive numbers and a target. Find every group of
numbers that adds up exactly to the target. You can reuse the same number as many
times as you like. `[2,2,3]` and `[3,2,2]` are the *same* group — count it once,
not once per ordering.

```diagram
   candidates = [2, 3, 6, 7]   target = 7
   groups that sum to 7:
     2 + 2 + 3 = 7   -> [2, 2, 3]
     7           = 7 -> [7]
   ([3,2,2] is the same multiset as [2,2,3] — don't list it again)
```

## Why this matters

Underneath the puzzle: *list every way to combine parts (reuse allowed) that hits
an exact total, counting each combination once no matter the order.* The one
reusable move is a search that builds a choice, undoes it, and moves on — never
walking into the same combination twice.

This is how real systems solve "make change" problems. Vending machines pick coin
and bill combinations that sum to an amount. Cutting-stock tools choose piece
lengths that add up without waste. Billing systems assemble line items that hit an
exact budget. Any "which items sum to N, reuse allowed" question is this shape.

What you're solving for is dodging an explosion of wasted work: the `start`-index
trick keeps the search from re-exploring the same group in every order, and the
sorted early stop cuts hopeless branches. The space is exponential, so that pruning
is what keeps it doable at all.

## Start from the obvious

At each step you're asking: "what number do I add next?" The obvious move is to try
every candidate at every step.

```diagram
   build(remaining, path):
     if remaining == 0: record(path); return
     if remaining < 0:  return
     for c in candidates:        # pick ANY candidate
       build(remaining - c, path + [c])
```

This finds every sum — but it also finds `[2,3]` and `[3,2]` as different answers,
because it's free to pick numbers in any order. It generates a mountain of
duplicates.

## Find the waste

The duplicates come from one thing: allowing every order of the same group. If we
force a single fixed order, each group is produced exactly once and all that
duplicate work vanishes.

The order rule is easy: **never pick a candidate that comes before the one you just
picked.** Pass a `start` index into the recursion and only loop from `start` onward.
Because reuse is allowed, after picking candidate `i` the next call still starts at
`i` (we may take it again) — `start = i`, not `i + 1`.

```diagram
   free order (bad):        forced order via start (good):
     2 -> 3   [2,3]           2 -> can still pick 2 or later
     3 -> 2   [3,2]  dup!     3 -> can pick 3 or later, NEVER back to 2
   the "never go back before start" rule makes [3,2] impossible to build
```

## The insight

Sort the candidates first and carry `remaining = target − sum(path)`. When
`remaining` hits 0, record a copy of the path. Otherwise loop `i` from `start`
upward; if `candidates[i] > remaining`, **stop** the loop — the list is sorted, so
every later candidate is even bigger. Otherwise pick it, recurse with `start = i`,
then pop it back off.

```diagram
   candidates sorted: [2, 3, 6, 7]   target = 7      (rem = remaining)
   backtrack(start=0, rem=7)
   |
   +- pick 2 -> backtrack(0, 5)
   |          +- pick 2 -> backtrack(0, 3)
   |          |          +- pick 2 -> backtrack(0, 1)
   |          |          |          +- 2>1 stop (dead end)
   |          |          +- pick 3 -> backtrack(1, 0)  rem==0 -> RECORD [2,2,3]
   |          |          +- 6>3 stop
   |          +- pick 3 -> backtrack(1, 2)
   |          |          +- 3>2 stop (dead end)
   |          +- 6>5 stop
   +- pick 3 -> backtrack(1, 4)
   |          +- pick 3 -> backtrack(1, 1)
   |          |          +- 3>1 stop
   |          +- 6>4 stop
   +- pick 6 -> backtrack(2, 1)  +- 6>1 stop
   +- pick 7 -> backtrack(3, 0)  rem==0 -> RECORD [7]

   the pop after each recurse is the BACKTRACK: it restores path so the
   next choice at this level starts clean
```

The `start` rule kills duplicate orderings; the sorted stop cuts dead branches
early.

## Complexity

- **Time: hard to bound tightly, exponential in the worst case.** The search tree
  is up to `target / smallest candidate` deep and up to `len(candidates)` wide, so
  it explores roughly that many branches. That's inherent — the number of valid
  combinations can itself be exponential.
- **Extra memory: proportional to the tree depth** (`target / smallest candidate`)
  for the recursion and the current path, plus the output list holding every
  combination found.

## Pitfalls

- Recursing with `start = i + 1` instead of `i` — that forbids reuse and turns this
  into a subset problem (see Combination Sum II).
- Recording `path` directly instead of a **copy** — you'd store a reference to a
  list that later steps empty out; every recorded answer ends up identical.
- Forgetting to sort, then trying to stop on the size check — without sorting a
  small candidate can sit after a big one, so an early stop would miss answers.

## Transfer

The "pass a `start` index so combinations stay non-decreasing" trick is the core of
every *pick-a-subset* backtracking problem: [Subsets / 78](../../21-subsets/0078-subsets/),
[Combinations / 77](../../21-subsets/0077-combinations/), and *Combination Sum II /
40* (each number used once, skip duplicates). Whenever you enumerate groups and
order-within-a-group doesn't matter, enforce an order with a `start` cursor.
