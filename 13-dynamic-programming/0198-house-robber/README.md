# 198. House Robber

**Pattern:** Dynamic programming (1-D, rob-or-skip choice)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/house-robber/

## The problem in plain words

Houses stand in a row, each with some money inside. You want to grab as much as
possible, but there's an alarm rule: **you can't rob two houses that are next to
each other.** Return the largest total you can safely take.

## Start from the obvious

The only real decision at each house is binary: rob it or don't. So think about
the last house, `n-1`:

- If you **rob** it, you take its money but you're forbidden from house `n-2`, so
  the rest of your loot comes from houses `0..n-3`.
- If you **skip** it, your loot is just the best you could do on houses `0..n-2`.

You take whichever is larger. Writing this as a recursion from the front:

```
best(i) = max( nums[i] + best(i+2),   # rob house i, jump past i+1
               best(i+1) )            # skip house i
best(i) = 0   when i is past the end
```

That's a correct, honest recursion. But it branches, and it re-solves the same
suffixes over and over.

## Find the waste

Draw the calls. `best(0)` needs `best(1)` and `best(2)`. `best(1)` also needs
`best(2)` and `best(3)`. So `best(2)` gets computed from two different places, and
this doubling cascades — exponential calls for a problem that only has `n`
distinct subproblems (`best(0)` … `best(n)`). **We keep recomputing the answer for
the same starting house.**

## The insight

Solve each suffix once. Top-down that's memoization: cache `best(i)` the first time
you hit it. Bottom-up, flip direction and sweep left to right carrying just two
numbers:

- `take` — the best total if we're *allowed* to rob the house we're now looking at
  (i.e. we did not rob the previous one),
- `skip` — the best total we've already locked in without robbing the current house.

At each house holding `money`:

```
new_take = skip + money          # rob here: add to whatever didn't include the neighbor
new_skip = max(take, skip)       # don't rob here: carry the best so far
take, skip = new_take, new_skip
```

The answer is `max(take, skip)`. Only the previous two states ever matter, so
there's no table to keep — `O(1)` space.

## Complexity

- **Naive recursion:** exponential time, `O(n)` stack.
- **Memoized:** `O(n)` time (n subproblems solved once), `O(n)` space.
- **Rolling loop:** `O(n)` time, `O(1)` space — the natural endpoint.

## Pitfalls

- Forgetting the empty list (`[]` → `0`) and the single house (`[x]` → `x`).
- Assuming the best plan is "every other house". Values matter: for `[2,1,1,2]`
  the answer robs the two ends (`2 + 2 = 4`), skipping *two* houses in the middle.
- In the update, both new values are computed from the *old* pair — do the
  assignment simultaneously (or with temps) so one doesn't clobber the other.

## Transfer

The "at each item, take-it-and-jump vs skip-it, keep two rolling states" pattern is
the backbone of many linear DPs. Its direct sequels:
[House Robber II / 213](../0213-house-robber-ii/) (houses in a circle — solve two
linear passes), and it rhymes with
[Delete and Earn / 740](https://leetcode.com/problems/delete-and-earn/), which
reduces to this exact recurrence after bucketing values.
