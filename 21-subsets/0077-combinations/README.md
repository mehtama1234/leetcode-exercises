# 77. Combinations

**Pattern:** Backtracking with a forward-only index and depth pruning
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/combinations/

## The problem in plain words

Given `n` and `k`, list every way to choose `k` numbers from `1..n`, where order
of the chosen numbers doesn't matter. For `n=4, k=2`: `[1,2]`, `[1,3]`, `[1,4]`,
`[2,3]`, `[2,4]`, `[3,4]` — six of them. `[1,2]` and `[2,1]` are the *same*
combination, so only one appears.

## Why this matters

This is **choosing without order** — the "n choose k" of counting made concrete.
Subsets enumerated selections of *any* size; here the size is fixed, and that one
constraint both shrinks the answer (`C(n,k)` instead of `2^n`) and opens the door
to pruning.

Fixed-size selection is the honest shape of real problems. Picking a committee or
a starting lineup of exactly `k` from a pool, choosing `k` features to A/B test
together, sampling `k`-item combinations for cross-validation folds, generating
all `k`-of-`n` sensor placements to evaluate — each asks "which groups of exactly
`k`, order irrelevant?"

What the good solution buys is twofold: a **canonical order** (always ascending)
so each combination is generated exactly once with no dedupe pass, and **early
pruning** so branches too short to ever reach size `k` are abandoned before you
waste recursion on them. On tight `k` relative to `n`, that pruning removes a large
fraction of the tree.

## Start from the obvious

A combination is a size-`k` subset. So the honest first idea reuses the subset
template but stops at depth `k`, and — to avoid `[1,2]`/`[2,1]` duplicates — only
ever picks numbers larger than the last one chosen:

```
backtrack(start):
    if path has k numbers: record a copy; return
    for i from start to n:
        path.push(i)
        backtrack(i+1)      # strictly larger next
        path.pop()
```

Correct. The forward-only `start` is what enforces "order doesn't matter": by
always ascending, each set of `k` values has exactly one increasing arrangement,
which is the one we build.

## Find the waste

The version above still walks into branches that can't finish. Suppose `n=4,
k=3` and you've chosen `[3]`. The only larger numbers are `4` — one number for two
remaining slots. There's no way to reach size 3, yet the loop still recurses on
`4`, discovers the dead end, and backtracks. Multiply that across the tree and
it's a lot of pointless descent.

## The insight

Count before you recurse. If you still need `need = k - len(path)` numbers, the
*smallest* start value that leaves enough room is bounded: you must be able to pick
`need` values from `start..n`, so `start` can be at most `n - need + 1`. Cap the
loop there:

```
need = k - len(path)
for i from start to (n - need + 1):
    choose i; backtrack(i+1); un-choose
```

Now every branch you enter is guaranteed to have enough numbers left to complete a
combination — no dead-end descents. The choose / recurse / un-choose template is
untouched; we only tightened the loop's upper bound.

## Complexity

- **Time:** `O(k * C(n,k))` — there are `C(n,k)` combinations and copying each into
  the result costs `O(k)`. The pruning removes wasted internal descent but not the
  output size, which is the true lower bound.
- **Space:** `O(k)` extra — recursion is at most `k` deep and `path` holds `k`
  items. The result is `O(k * C(n,k))`, the required answer.

## Pitfalls

- **Recursing from `start` instead of `i+1`** — you'd revisit numbers and produce
  order-permuted or repeated combinations.
- **Off-by-one in the prune bound.** `n - need + 1` is inclusive; get it wrong and
  you either miss valid combinations or lose the pruning benefit.
- Forgetting the copy at the leaf, or the `pop()` on the way back — the usual
  backtracking traps.

## Transfer

Combinations is Subsets with a depth cap plus a completion-feasibility prune. The
same forward-only index appears in
[Combination Sum / 39](../../09-backtracking/0039-combination-sum/) (prune by a
running total instead of a count) and in every "choose exactly k, order-free"
enumeration. The prune idea — *stop when the remaining choices can't satisfy the
remaining requirement* — generalizes far beyond this problem.
