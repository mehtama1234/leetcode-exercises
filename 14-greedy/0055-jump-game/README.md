# 55. Jump Game

**Pattern:** Greedy (track the reachable frontier)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/jump-game/

## The problem in plain words

You stand at index 0 of an array. The number at each index says the **most** steps
you may jump forward from there (you can also jump fewer). Can you get to the last
index? Return true or false.

## Start from the obvious

The literal reading is a search: from where you stand, you may jump 1, 2, … up to
`nums[i]` steps; try each and recurse.

```
def reach(i):
    if i >= last: return True
    for step in 1 .. nums[i]:
        if reach(i + step): return True
    return False
```

Correct, but it explores an exponential tree of jump sequences and revisits the
same indices over and over. Memoizing gets it to `O(n^2)`. That's a lot of work
for a plain yes/no question — a sign we're computing more than we need.

## Find the waste

The recursion agonizes over *which* jumps to take. But the question isn't "what's
the path?" — it's just "**is the last index reachable at all?**" For that, the
exact route is irrelevant. All that matters is: how far can we possibly get?

Here's the property that collapses the search. Reachability is **downward
closed**: if you can land on index `i`, you can also land on every index between
the start and `i`. Why? A jump that lets you reach `i` from some earlier index
also lets you stop anywhere short of `i` (you're allowed to jump *fewer* steps).
So the set of reachable indices is always a solid prefix `0 .. reach` with no
holes — and one number, `reach`, describes it completely.

## The insight

Sweep left to right, keeping `reach` = the farthest index reachable so far.

```
reach = 0
for i, step in enumerate(nums):
    if i > reach:           # can't even stand on i
        return False
    reach = max(reach, i + step)
    if reach >= last:
        return True
return True
```

At each index `i`:

1. If `i > reach`, nothing before `i` could jump far enough to land on it — there's
   a gap, so the last index is unreachable. Return false.
2. Otherwise `i` is reachable, so from `i` we can push the frontier out to
   `i + nums[i]`. Keep the larger frontier.
3. The moment `reach` covers the last index, we're done.

**Why is the greedy choice safe?** Because "extend the frontier as far as
possible" never discards a position we could otherwise have used. Since the
reachable set is a hole-free prefix, its single boundary `reach` *is* the complete
state — there is no hidden reachable index sitting beyond `reach` that a different
choice of jumps would have unlocked. Maximizing `reach` at each step therefore
keeps every option open. If instead we made a "smaller" jump on purpose, we could
only shrink the frontier and possibly strand ourselves before a gap we'd otherwise
have cleared — so being greedy about distance is strictly the right move.

## Complexity

- **Time:** `O(n)` — one pass, constant work per index.
- **Space:** `O(1)` — a single integer `reach`.

## Pitfalls

- **The `0` trap.** A `0` isn't fatal by itself (`[2, 0, 0]` is fine — one jump
  clears it). It's only fatal when `reach` catches up to that index and can't get
  past it, as in `[3, 2, 1, 0, 4]`: the frontier stalls at index 3, then index 4
  fails the `i > reach` check. Test `i > reach`, not `nums[i] == 0`.
- **Off-by-one on the target.** The goal is the **last index**, `len(nums) - 1`,
  not `len(nums)`.
- **Overbuilding.** People reach for DP/BFS here; the greedy frontier is `O(n)`,
  `O(1)`, and simpler. Don't reconstruct the actual jumps — the question never
  asked for them.

## Transfer

The reusable idea is **collapsing a path search into a single "how far can I get?"
scalar, valid whenever the reachable set has no holes.** Siblings:
[Jump Game II / 45](https://leetcode.com/problems/jump-game-ii/) (same frontier
idea, but count the *minimum* jumps — advance a level boundary each time you
exhaust the current one),
[Gas Station / 134](https://leetcode.com/problems/gas-station/) (a running tank
where a single sweep decides feasibility). Whenever a problem asks only *whether*
you can reach a goal, ask "what's the farthest I can reach?" before enumerating
routes.
