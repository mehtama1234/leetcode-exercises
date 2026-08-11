# 198. House Robber

**Pattern:** Dynamic programming (1-D, rob-or-skip choice)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/house-robber/

## The problem in plain words

Houses stand in a row, each holding some money. You want as much as you can carry,
but the alarm rule is: **you can't rob two houses next to each other.** Return the
largest total you can safely take.

```diagram
   houses:  [ 2 ][ 7 ][ 9 ][ 3 ][ 1 ]
              *         *         *
              rob 0, 2, 4  ->  2 + 9 + 1 = 12
              (never two adjacent; this beats robbing 7 and 3)
```

## Why this matters

Under the heist story is **maximize a total under a "no two adjacent picks"
rule.** The move to learn is a per-item choice — take this one and skip its
neighbor, or skip it — carried forward with two running totals.

Non-adjacent selection is a real shape. Picking the most valuable set of
non-overlapping jobs or time slots reduces to it once sorted. So does spacing out
cell towers or ads so neighbors don't conflict while you maximize coverage, and
choosing a highest-scoring set of items under a "no two in a row" rule.

The fast version collapses an exponential rob-or-skip tree into a single pass —
only `n` distinct suffixes exist — and the two-variable form keeps constant
memory, since the recurrence never reaches back more than one step. The honest
caveat it teaches: "grab every other house" is wrong; the values decide the
pattern.

## Start from the obvious

At each house the only real decision is binary: rob it or don't. Think about the
last house, `n-1`:

- **Rob it:** you take its money, but house `n-2` is now off-limits, so the rest of
  your loot comes from houses `0 .. n-3`.
- **Skip it:** your loot is the best you could do on houses `0 .. n-2`.

Take whichever is larger. As a recursion from the front:

```
best(i) = max( nums[i] + best(i+2),   # rob house i, jump past i+1
               best(i+1) )            # skip house i
best(i) = 0   when i is past the end
```

Correct and honest. But it branches, and it re-solves the same suffixes.

## Find the waste

`best(0)` needs `best(1)` and `best(2)`. But `best(1)` *also* needs `best(2)`. So
`best(2)` gets computed from two different places — and that doubling cascades all
the way down.

```diagram
              best(0)
             /       \
        best(1)       best(2)     <- best(2) reached here...
        /     \
   best(2)   best(3)              <- ...and again here

   exponential calls, but only n distinct starting points exist
```

**The answer for the same starting house gets recomputed over and over.**

## The insight

Solve each suffix once. Sweep left to right carrying just two numbers:

- `take` — best total if we're *allowed* to rob the house we're now looking at
  (meaning we did not rob the previous one),
- `skip` — best total already locked in without robbing the current house.

At each house holding `money`:

```
new_take = skip + money       # rob here: add to whatever didn't include the neighbor
new_skip = max(take, skip)    # don't rob here: carry the best so far
```

Watch it run on `[2, 7, 9, 3, 1]`. Each cell reads only the pair before it:

```diagram
   money:     2      7      9      3      1
             ---    ---    ---    ---    ---
   take:  0 ->2     0+7    2+9    16+3   11+1     take = prev skip + money
             |       ^     ^       ^      ^
   skip:  0-> 0  ->  2  -> 7  ->  11  -> 16       skip = max(prev take, prev skip)

   at house 2 (money 9):
        new take = skip(=7 from before house 1) + 9 = 16
        new skip = max(take=7, skip=7) = 7
                      \___ each cell only needs the previous take/skip
   answer = max(take, skip) at the end = max(11, 16) = ... final = 12
```

The answer is `max(take, skip)` at the end. Only the previous two states ever
matter, so there's no table to keep — constant memory.

## Complexity

- **Naive recursion:** exponential time, `O(n)` stack.
- **Memoized:** about `n` steps (n subproblems solved once), about `n` memory.
- **Rolling loop:** about `n` steps, constant memory — the natural endpoint.

## Pitfalls

- Forgetting the empty list (`[]` → `0`) and the single house (`[x]` → `x`).
- Assuming the best plan is "every other house." Values matter: for `[2,1,1,2]`
  the answer robs the two ends (`2 + 2 = 4`), skipping *two* houses in the middle.
- In the update, both new values come from the *old* pair — assign them together
  (or with temps) so one doesn't clobber the other before it's read.

## Transfer

The "at each item, take-it-and-jump vs skip-it, carry two rolling states" pattern
is the backbone of many linear DPs. Its direct sequel:
[House Robber II / 213](../0213-house-robber-ii/) (houses in a circle — solve two
linear passes). It also rhymes with
[Delete and Earn / 740](https://leetcode.com/problems/delete-and-earn/), which
becomes this exact recurrence after bucketing values.
