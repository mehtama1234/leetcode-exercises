# 213. House Robber II

**Pattern:** Dynamic programming (reduce a circular constraint to two linear runs)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/house-robber-ii/

## The problem in plain words

Exactly [House Robber / 198](../0198-house-robber/) — houses in a row, each with
money, no robbing two neighbors — with one twist: the houses form a **circle**.
Now the first house and the last house are neighbors too, so you can't rob both of
them. Return the most money you can safely take.

```diagram
             [0]---[1]
            /         \
          [4]         [2]
            \         /
             [3]-----.

   0 and 4 are now neighbors (the ends touch).
   robbing both is illegal, even though in a straight row it was fine.
```

## Why this matters

The real lesson is a general move: **when a constraint ties the two ends of a
sequence together, don't try to weave it into the recurrence — fix one boundary
decision, solve the rest as an ordinary line, once per choice, then combine.** You
split on the wrap-around to turn a circular problem into linear ones you already
know how to solve.

That "break the wrap-around by fixing an endpoint" move shows up in round-robin
shift schedules and ring buffers where the first and last slots touch, in placing
items around a ring under a no-adjacent rule, and in circular-array DPs like the
maximum circular subarray sum.

The clean version buys correctness at no extra cost: two linear passes and
constant state, instead of a fiddly recurrence that has to remember whether the
first house was robbed so it can forbid the last.

## Start from the obvious

Your instinct is to reuse the linear solution. But the wrap-around breaks it: the
straight-line DP is perfectly happy to rob both house `0` and house `n-1`, and in a
circle that's illegal. You could bolt the "ends touch" rule directly into the
recurrence — tracking whether you robbed the first house so you can forbid the
last — but that's fiddly and easy to get wrong.

## The insight

Step back and look at what the circle actually adds: **one extra constraint**,
"not both end houses." Instead of encoding that inside the DP, use it to *split*
the problem in two.

Any legal circular plan must fall into one of these buckets, since it can never
hold both ends:

- **It doesn't rob the last house** → houses `0 .. n-2` behave like a plain
  straight row.
- **It doesn't rob the first house** → houses `1 .. n-1` behave like a plain
  straight row.

```diagram
   nums = [ 2 ][ 3 ][ 2 ]     (a circle; ends 0 and 2 touch)

   bucket A: drop the LAST house -> run robber on [ 2 ][ 3 ]      = 3
             ^^^^^^^^^^^^^^^^^^^^                  0    1

   bucket B: drop the FIRST house -> run robber on      [ 3 ][ 2 ] = 3
             ^^^^^^^^^^^^^^^^^^^^^                        1    2

   answer = max(A, B) = max(3, 3) = 3     (can't take both 2s)
```

Every legal circular plan lives in at least one bucket (a plan that skips both
ends lands in both — fine, we take a max, not a sum). So:

```
answer = max( rob_line(nums[0 .. n-2]),
              rob_line(nums[1 .. n-1]) )
```

We reuse the already-solved linear robber twice and keep the better run. The
circular difficulty dissolves into two ordinary problems.

`rob_line` is the same two-rolling-variable House Robber:

```diagram
   run rob_line on [ 1 ][ 3 ][ 1 ][ 3 ][ 100 ]  (bucket B of a bigger example)

   money:     1      3      1      3     100
   take:  0 ->1     0+3    3+1    4+3   6+100
   skip:  0-> 0  -> 1  ->  3  ->  4  ->  103
              \____ take = prev skip + money;  skip = max(prev take, prev skip)

   answer for this line = max(take, skip) = 103   (rob the 3 and the 100)
```

## Complexity

- **Time:** about `n` steps — two linear sweeps, each about `n`.
- **Space:** constant for the DP itself. (Slicing `nums[:-1]` / `nums[1:]` copies,
  which costs `O(n)` memory; iterate over index ranges instead if you want strictly
  constant memory.)

## Pitfalls

- **The `n == 1` case.** With one house there is no "other end," and both slices
  `nums[:-1]` and `nums[1:]` come out empty, giving `0`. Handle a single house
  directly and return `nums[0]`.
- Dropping *just* the first or *just* the last house isn't enough on its own — you
  need **both** runs and the max; each alone misses plans the other allows.
- Don't assume the two buckets are disjoint. They aren't (a plan robbing neither
  end sits in both), but `max` handles the overlap correctly.

## Transfer

"Break a circular / wrap-around constraint by fixing one boundary choice and
solving the linear cases" is a reusable move — reach for it whenever a problem is a
known linear DP made circular. The underlying line solver is
[House Robber / 198](../0198-house-robber/); the same reduce-to-cases instinct
shows up in circular-array problems like
[Maximum Sum Circular Subarray / 918](https://leetcode.com/problems/maximum-sum-circular-subarray/).
