# 55. Jump Game

**Pattern:** Greedy (track how far you can reach)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/jump-game/

## The problem in plain words

You stand at index 0. The number at each index is the **most** steps you may jump
forward from there — you may also jump fewer. Can you reach the last index? Return
true or false.

```diagram
   index:   0    1    2    3    4
   nums:  [ 2 ,  3 ,  1 ,  1 ,  4 ]
            \___/                          from 0 you may go 1 or 2 steps
   0 -> 1 -> 4      reaches the end  ->  true
```

## Why this matters

The real question is **reachability**: given a set of local moves, can you get from
a start to a goal? And can you decide it by tracking a single number — the farthest
point reached so far — instead of listing out routes? The core operation is holding
a *reachable frontier* as you scan.

That pattern shows up wherever movement or dependency is constrained. Networking
asks "is this host reachable?" and pushes a frontier out hop by hop. Build systems
ask whether a target is reachable through its dependency edges. Game AI tests
whether a goal tile is reachable under a move budget. Garbage collectors mark which
objects are still reachable from live roots.

What you buy is one linear pass and constant memory. Because reachability here has
no holes (reach index `i`, and you reach everything before it too), you skip the
exploding search over jump sequences and carry a single frontier.

## Start from the obvious

The literal reading is a search: from where you stand you may jump 1, 2, … up to
`nums[i]` steps. Try each and recurse.

```
def reach(i):
    if i >= last: return True
    for step in 1 .. nums[i]:
        if reach(i + step): return True
    return False
```

Correct, but it explores a branching tree of jump sequences and revisits the same
indices again and again. Even with a memo table (remember each index's answer) it
is about n × n work — a lot for a plain yes/no question. That is a sign you are
computing more than you need.

## Find the waste

The recursion agonizes over *which* jumps to take. But the question is not "what is
the path?" — it is "**is the last index reachable at all?**" For that, the route
does not matter. Only one thing does: how far can you possibly get?

Here is the property that collapses the search. Reachability has no holes: if you
can land on index `i`, you can land on every index between the start and `i` too. A
jump that reaches `i` also lets you stop short of it — you are allowed to jump
*fewer* steps. So the reachable set is always a solid stretch `0 .. reach`, and one
number, `reach`, describes it fully.

```diagram
   nums:  [ 2 ,  3 ,  1 ,  1 ,  4 ]
   index:   0    1    2    3    4

   reachable so far:  0====reach          (solid, no gaps)
                      every index up to `reach` is landable
```

## The insight

Sweep left to right, keeping `reach` = the farthest index reachable so far.

```
reach = 0
for i, step in enumerate(nums):
    if i > reach:          return False   # can't even stand on i
    reach = max(reach, i + step)
    if reach >= last:      return True
return True
```

A trace of a passing case and a failing one:

```diagram
   PASS   nums = [2, 3, 1, 1, 4]        FAIL   nums = [3, 2, 1, 0, 4]
   i=0 step2  reach = max(0, 2) = 2     i=0 step3  reach = max(0, 3) = 3
   i=1 step3  reach = max(2, 4) = 4     i=1 step2  reach = max(3, 3) = 3
   i=2        reach >= last(4)  TRUE    i=2 step1  reach = max(3, 3) = 3
                                        i=3 step0  reach = max(3, 3) = 3
                                        i=4        i(4) > reach(3)  FALSE
                                                   ^ stalled at 3, gap before 4
```

At each index `i`: if `i > reach`, nothing before `i` jumps far enough to land on it
— there is a gap, so the goal is unreachable. Otherwise `i` is reachable, so push
the frontier out to `i + nums[i]`. The moment `reach` covers the last index, done.

**Why is the greedy choice safe?** "Extend the frontier as far as possible" never
throws away a spot you could have used. Since the reachable set has no holes, its
single boundary `reach` *is* the complete state — there is no hidden reachable index
sitting past `reach` that some other choice of jumps would have unlocked. Maximizing
`reach` keeps every option open. Making a smaller jump on purpose could only shrink
the frontier and strand you before a gap you would otherwise clear.

## Complexity

- **Time: about n steps.** One pass, constant work per index.
- **Extra memory: a fixed amount.** A single integer `reach`.

## Pitfalls

- **The `0` trap.** A `0` is not fatal by itself (`[2, 0, 0]` is fine — one jump
  clears it). It is only fatal when `reach` catches up to it and cannot get past, as
  in `[3, 2, 1, 0, 4]`. Test `i > reach`, not `nums[i] == 0`.
- **Off-by-one on the goal.** The target is the **last index**, `len(nums) - 1`, not
  `len(nums)`.
- **Overbuilding.** People reach for full search or table-based methods here; the
  frontier is about n steps and simpler. Do not reconstruct the actual jumps — the
  question never asked for them.

## Transfer

The reusable idea is **collapsing a path search into a single "how far can I get?"
number, valid whenever the reachable set has no holes.** Siblings:
[Jump Game II / 45](https://leetcode.com/problems/jump-game-ii/) (same frontier, but
count the *minimum* jumps),
[Gas Station / 134](https://leetcode.com/problems/gas-station/) (a running tank a
single sweep decides). Whenever a problem asks only *whether* you can reach a goal,
ask "what is the farthest I can reach?" before listing routes.
