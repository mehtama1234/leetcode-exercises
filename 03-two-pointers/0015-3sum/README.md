# 15. 3Sum

**Pattern:** Sort + two pointers (fix one, converge the rest)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/3sum/

## The problem in plain words

Find every group of three numbers in the array that add up to zero. Return the
triplets themselves (their values, not indices), and don't list the same triplet
twice even if the array has repeated numbers.

## Why this matters

The real problem is **finding combinations that satisfy a numeric relationship without checking every combination** — and doing it while suppressing duplicate answers. The core operation is reducing a k-way search to a (k-1)-way search plus a single linear sweep, using sorted order to both guide the sweep and make dedup fall out for free (equal values sit adjacent).

This "match up entries that sum or balance to a target" pattern is everywhere money and quantities move:

- **Finance/accounting reconciliation** — finding sets of transactions that net to a given balance, or offsetting entries that cancel.
- **Analytics and reporting** — grouping records whose measures combine to hit a threshold, deduplicating equivalent groups.
- **Computational geometry / collision** — triples of points meeting a coplanar or distance condition after sorting by coordinate.

What we're solving for is **avoiding the combinatorial blowup**: brute force is `O(n^3)`, and sorting once turns it into `O(n^2)` with `O(1)` extra space — no hash set, because sorted adjacency handles the duplicates that would otherwise corrupt the output.

## Start from the obvious

"Three numbers that sum to zero" turns straight into three nested loops:

```
for i:
  for j after i:
    for k after j:
      if nums[i] + nums[j] + nums[k] == 0: record it
```

Correct, but `O(n^3)`, and it has a second problem: duplicates. `[0,0,0,0]` would
report `[0,0,0]` many times, so you need to dedupe (sort each triplet, drop it in
a set). It's a fine first draft — and staring at it shows the fix.

## Find the waste

Rewrite the inner two loops as a question: *given a fixed first number `nums[i]`,
find two numbers in the rest that sum to `-nums[i]`.* That is literally **Two Sum**.

And we already know sorted Two Sum doesn't need a nested loop — two converging
pointers solve it in one linear pass (see [Two Sum II / 167](../0167-two-sum-ii-input-array-is-sorted/)).
So the waste in the brute force is re-scanning the tail with a full inner loop
when a sorted array lets a single sweep do it.

## The insight

**Sort the array first.** Then for each index `i`:

- Set `left = i+1`, `right = n-1`.
- Look at `nums[i] + nums[left] + nums[right]`. Too small? move `left` right for a
  bigger number. Too big? move `right` left for a smaller one. Exactly zero?
  record the triplet and step both inward.

Sorting pays off twice. It powers the two-pointer sweep, **and** it makes deduping
trivial — equal values are adjacent, so:

- skip `nums[i]` if it equals the previous anchor,
- after recording a hit, skip past any repeated `left` and `right` values.

One more freebie: once `nums[i] > 0`, every remaining number is positive, so no
triplet can sum to zero — stop early.

```
nums.sort()
for i in range(n):
    if nums[i] > 0: break
    if i > 0 and nums[i] == nums[i-1]: continue
    left, right = i+1, n-1
    while left < right:
        s = nums[i] + nums[left] + nums[right]
        if s < 0: left += 1
        elif s > 0: right -= 1
        else:
            record [nums[i], nums[left], nums[right]]
            left += 1; right -= 1
            skip duplicate lefts and rights
```

## Complexity

- **Time:** `O(n^2)` — sorting is `O(n log n)`, then for each of `n` anchors the
  two pointers sweep the tail in `O(n)`. The `n^2` term dominates.
- **Space:** `O(1)` beyond the output (ignoring sort's temporary space). No hash
  set for deduping — sorted adjacency handles it.

## Pitfalls

- **Duplicate triplets** are the whole difficulty. You must skip repeats in three
  places: the anchor `i`, and the `left`/`right` values after a successful match.
- Skipping the anchor with `i > 0 and nums[i] == nums[i-1]` — compare to the
  *previous*, not the next, so you keep the first occurrence and drop later copies.
- Forgetting to move **both** pointers after recording a hit — leaving one put
  will just re-find the same or an invalid triplet.
- Not sorting first: every step of the method depends on sorted order.

## Transfer

This is the template for the whole "k-Sum" family: fix outer values and
two-pointer the innermost pair. It extends directly to
[4Sum / 18](https://leetcode.com/problems/4sum/) (two fixed loops, then two
pointers) and *3Sum Closest*. The reusable move — **sort, then reduce a k-sum to a
(k-1)-sum with two converging pointers** — builds straight on
[Two Sum II / 167](../0167-two-sum-ii-input-array-is-sorted/).
