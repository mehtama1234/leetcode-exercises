# 213. House Robber II

**Pattern:** Dynamic programming (reduce a circular constraint to two linear runs)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/house-robber-ii/

## The problem in plain words

Exactly [House Robber / 198](../0198-house-robber/) — houses in a row, each with
money, no robbing two neighbors — with one twist: the houses form a **circle**.
That means the first house and the last house are neighbors too, so you can't rob
both of them. Return the most money you can safely take.

## Start from the obvious

Your instinct is to reuse the linear solution. But the wrap-around breaks it: the
linear DP is perfectly happy to rob both house `0` and house `n-1`, and in a
circle that's illegal. You could try to bolt the "ends touch" rule directly into
the recurrence, tracking whether you robbed the first house so you can forbid the
last — doable, but fiddly and easy to get wrong.

## Find the waste — and the cleaner framing

Step back and look at what the circle actually adds: **a single extra
constraint**, "not both end houses". Instead of encoding that inside the DP, use
it to *split* the problem.

Any valid circular plan falls into one of two buckets, because it can never
contain both ends:

- **It doesn't rob the last house.** Then houses `0 .. n-2` behave like a plain
  straight row — the wrap-around neighbor of house 0 (the last house) is out of
  play.
- **It doesn't rob the first house.** Then houses `1 .. n-1` behave like a plain
  straight row.

Every legal circular plan lives in at least one bucket (a plan that skips both
ends is counted in both, which is fine — we're taking a max, not a sum). So:

```
answer = max( rob_line(nums[0 .. n-2]),
              rob_line(nums[1 .. n-1]) )
```

We reuse the already-solved linear robber twice and pick the better run. The
circular difficulty dissolves into two ordinary problems.

## The insight

**When a constraint couples the two ends of a sequence, fix one end's decision and
solve the rest as a normal line — once per choice, then combine.** Here the
decision is "which end do I leave untouched", giving two linear passes.

`rob_line` is the same two-rolling-variable House Robber:

```
take, skip = 0, 0
for money in row:
    take, skip = skip + money, max(take, skip)
return max(take, skip)
```

## Complexity

- **Time:** `O(n)` — two linear sweeps, each `O(n)`.
- **Space:** `O(1)` for the DP itself. (Slicing `nums[:-1]` / `nums[1:]` copies,
  which is `O(n)` memory; iterate over index ranges instead if you want strict
  `O(1)`.)

## Pitfalls

- **The `n == 1` case.** With one house there is no "other end", and both slices
  `nums[:-1]` and `nums[1:]` are empty, giving `0`. Handle single-house directly and
  return `nums[0]`.
- Trying to drop *just the first* or *just the last* house isn't enough on its own —
  you need **both** runs and the max; each alone misses plans that the other allows.
- Don't double-count: it's tempting to think the two buckets must be disjoint. They
  aren't (a plan robbing neither end is in both), but `max` handles that correctly.

## Transfer

"Break a circular / wrap-around constraint by fixing one boundary choice and
solving linear cases" is a reusable move. You'll see it whenever a problem is a
known linear DP made circular. The underlying line solver is
[House Robber / 198](../0198-house-robber/); the same reduce-to-cases instinct
shows up in circular-array problems like
[Maximum Sum Circular Subarray / 918](https://leetcode.com/problems/maximum-sum-circular-subarray/).
