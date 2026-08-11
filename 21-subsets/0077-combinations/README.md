# 77. Combinations

**Pattern:** Backtracking with a forward-only index and depth pruning
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/combinations/

## The problem in plain words

Given `n` and `k`, list every way to choose `k` numbers from `1..n`, where the
order of the chosen numbers doesn't matter. For `n=4, k=2`: `[1,2]`, `[1,3]`,
`[1,4]`, `[2,3]`, `[2,4]`, `[3,4]` — six of them. `[1,2]` and `[2,1]` are the
*same* combination, so only one appears.

```diagram
   n=4, k=2   pick 2 from {1,2,3,4}, order-free

   [1,2] [1,3] [1,4] [2,3] [2,4] [3,4]     C(4,2) = 6
```

## Why this matters

This is **choosing without order** — the "n choose k" of counting made concrete.
Subsets listed selections of *any* size; here the size is fixed, and that one
constraint both shrinks the answer (`C(n,k)` instead of `2^n`) and opens the door
to cutting branches early.

Fixed-size selection is the honest shape of real problems. Picking a committee or
a starting lineup of exactly `k` from a pool, choosing `k` features to A/B test
together, sampling `k`-item combinations for cross-validation folds, generating
all `k`-of-`n` sensor placements — each asks "which groups of exactly `k`, order
irrelevant?"

The good solution buys two things: a **canonical order** (always ascending) so
each combination is generated exactly once with no dedupe pass, and an **early
cut** so branches too short to ever reach size `k` are dropped before you waste
recursion on them.

## Start from the obvious

A combination is a size-`k` subset. So the honest first idea reuses the subset
tree but stops at depth `k`, and — to avoid `[1,2]`/`[2,1]` duplicates — only
ever picks numbers larger than the last one chosen:

```diagram
   forward-only tree, n=4, k=2   (only ascending picks)

                  start=1
        /        |        |       \
     1(->2..)  2(->3..)  3(->4)   4  <- 4 alone can't reach k=2
     / | \      / \       |
   2  3  4     3   4      4
   |  |  |     |   |      |
 [1,2][1,3][1,4][2,3][2,4][3,4]        6 leaves at depth k=2
```

Correct. The forward-only `start` is what enforces "order doesn't matter": by
always ascending, each set of `k` values has exactly one increasing arrangement,
and that's the one we build.

## Find the waste

The version above still walks into branches that can't finish. Take `n=4, k=3`
and say you've chosen `[3]`. The only larger number is `4` — one number for two
empty slots. There's no way to reach size 3, yet the loop still recurses on `4`,
discovers the dead end, and backs out. Multiply that across the tree and it's a
lot of pointless descent.

```diagram
   n=4, k=3, already chose [3], need 2 more from {4}

   [3] -> take 4 -> [3,4]  need 1 more from {}   X dead end
                    ^ only 1 number left but 2 slots to fill
   we should never have entered this branch
```

## The insight

Count before you recurse. If you still need `need = k - len(path)` numbers, the
*largest* start value worth trying is bounded: you must fit `need` values into
`start..n`, so `start` can be at most `n - need + 1`. Cap the loop there.

```diagram
   need = k - len(path)   last usable start = n - need + 1

   n=4, k=3, path=[3]: need=2, last_ok = 4-2+1 = 3
     loop start..3  -> start is already 4 > 3  -> loop is EMPTY
     the dead branch is PRUNED before it's ever entered
```

Now every branch you step into is guaranteed to have enough numbers left to
finish a combination — no dead-end descents. The choose / recurse / un-choose
template is untouched; we only tightened the loop's upper bound.

## Complexity

- **Time: about `k * C(n,k)`** — there are `C(n,k)` combinations and copying each
  into the result costs about `k`. The cut removes wasted internal descent but not
  the output size, which is the true floor.
- **Extra memory: about `k`** — recursion is at most `k` deep and `path` holds
  `k` items. The result is `k * C(n,k)`, the answer itself.

## Pitfalls

- **Recursing from `start` instead of `i+1`** — you'd revisit numbers and produce
  order-permuted or repeated combinations.
- **Off-by-one in the cut bound.** `n - need + 1` is inclusive; get it wrong and
  you either miss valid combinations or lose the cut's benefit.
- Forgetting the copy at the leaf, or the `pop()` on the way back — the usual
  backtracking traps.

## Transfer

Combinations is Subsets with a depth cap plus a "can this branch still finish?"
cut. The same forward-only index appears in
[Combination Sum / 39](../../09-backtracking/0039-combination-sum/) (cut by a
running total instead of a count) and in every "choose exactly k, order-free"
enumeration. The cut idea — *stop when the remaining choices can't satisfy the
remaining requirement* — reaches far beyond this problem.
