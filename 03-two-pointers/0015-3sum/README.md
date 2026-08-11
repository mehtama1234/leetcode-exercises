# 15. 3Sum

**Pattern:** Sort + two pointers (fix one, converge the rest)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/3sum/

## The problem in plain words

Find every group of three numbers in the array that add up to zero. Return the
triplets themselves (their values, not positions), and don't list the same triplet
twice even when the array has repeats.

```diagram
   nums = [-1, 0, 1, 2, -1, -4]
   groups of three that sum to 0:
     -1 + 0 + 1 = 0   -> [-1, 0, 1]
     -1 + -1 + 2 = 0  -> [-1, -1, 2]
   (the two -1s look the same but sit at different spots — count the group once)
```

## Why this matters

The real problem is *finding combinations that hit a numeric target without
checking every combination* — and doing it while quietly dropping duplicate
answers. The one reusable move: turn a three-way search into a two-way search plus
a single sweep, and use sorted order both to guide the sweep and to make dedup fall
out for free (equal values land next to each other).

That "match up entries that sum to a target" pattern shows up wherever quantities
move. Accounting reconciliation looks for sets of transactions that net to a
balance. Analytics groups records whose measures combine to hit a threshold.
Geometry finds triples of points meeting a distance condition after sorting.

What you're solving for is dodging the blowup: brute force is about n × n × n
steps, and sorting once turns it into about n × n with no extra hash set — sorted
adjacency handles the duplicates that would otherwise corrupt the output.

## Start from the obvious

"Three numbers that sum to zero" turns straight into three nested loops.

```diagram
   for i:
     for j after i:
       for k after j:
         if nums[i] + nums[j] + nums[k] == 0: record it
```

Correct, but about n × n × n steps, and it has a second problem: duplicates.
`[0,0,0,0]` reports `[0,0,0]` many times, so you'd need a set to dedupe. Fine first
draft — and staring at the inner two loops shows the fix.

## Find the waste

Rewrite the inner two loops as a question: *given a fixed first number `nums[i]`,
find two numbers in the rest that sum to `-nums[i]`.* That is exactly **Two Sum**.
And on a *sorted* array, Two Sum doesn't need a nested loop — two converging
pointers solve it in one sweep (see
[Two Sum II / 167](../0167-two-sum-ii-input-array-is-sorted/)). The waste is the
full inner loop where a single sweep would do.

## The insight

**Sort first.** Then for each anchor `i`, put `left = i+1` and `right = n-1` and let
the sum steer the pointers.

```diagram
   sorted: [-4, -1, -1, 0, 1, 2]      anchor i=1 (nums[i] = -1), need pair summing to +1
            i    L              R
                 -1 + 2 = 1  (with anchor: -1 + -1 + 2 = 0)  -> record [-1,-1,2]
                 step both inward:
            i        L      R
                 0 + 1 = 1  (with anchor: -1 + 0 + 1 = 0)    -> record [-1,0,1]
                 step both inward: L meets R -> done with this anchor

   steering rule (with anchor fixed):
     triple sum < 0 -> need bigger -> L++
     triple sum > 0 -> need smaller -> R--
     triple sum == 0 -> record, then L++ and R--
```

Sorting pays off twice. It powers the sweep, **and** it makes deduping cheap — equal
values sit next to each other:

```diagram
   dedup by skipping repeats:
     anchor:  skip nums[i] if it equals nums[i-1]   (keep first, drop later copies)
     after a hit: skip repeated L values, skip repeated R values
     early stop: once nums[i] > 0, every later number is positive -> no zero triple
```

## Complexity

- **Time: about n × n steps.** Sorting is about n·log n; then each of n anchors
  sweeps the tail in about n. The n × n term dominates.
- **Extra memory: constant** beyond the output (ignoring the sort's scratch space).
  No hash set — sorted adjacency handles duplicates.

## Pitfalls

- **Duplicate triplets** are the whole difficulty. Skip repeats in three places: the
  anchor `i`, and the `left`/`right` values after a match.
- Skip the anchor with `i > 0 and nums[i] == nums[i-1]` — compare to the *previous*,
  so you keep the first copy and drop later ones.
- Forgetting to move **both** pointers after a hit — leave one and you just re-find
  the same triplet.
- Not sorting first: every step of the method depends on sorted order.

## Transfer

This is the template for the whole "k-Sum" family: fix outer values and
two-pointer the innermost pair. It extends straight to
[4Sum / 18](https://leetcode.com/problems/4sum/) (two fixed loops, then two
pointers) and *3Sum Closest*. The reusable move — **sort, then reduce a k-sum to a
(k-1)-sum with two converging pointers** — builds directly on
[Two Sum II / 167](../0167-two-sum-ii-input-array-is-sorted/).
