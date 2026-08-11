# 315. Count of Smaller Numbers After Self

**Pattern:** Binary Indexed Tree over ranks (or count-during-merge-sort) — inversions
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/count-of-smaller-numbers-after-self/

## The problem in plain words

For every element in the array, look only at the elements to its **right** and
count how many of them are strictly smaller than it. Return one such count per
position. Example: in `[5, 2, 6, 1]` the answer is `[2, 1, 1, 0]` — the `5` has two
smaller numbers after it (`2` and `1`), the `2` has one (`1`), the `6` has one
(`1`), and the last element has none.

## Why this matters

This is the **inversion count**, reported per element — "how out of order is each
item relative to what comes after it?" Inversions are the standard formal measure
of *disorder* in a sequence, and counting them efficiently is a recurring need.

Concrete places it shows up: **rank-correlation statistics** — Kendall's tau, used
to measure how well a ranking model agrees with ground truth, is built directly on
inversion counts. **"How far from sorted" diagnostics** — near-sorted data lets you
pick a cheaper algorithm; the inversion count quantifies exactly that. **Sorting-
network and comparison-cost analysis** counts the swaps a sort must make.
**Sequence-similarity / edit-distance-flavored tasks** measure how much two
orderings disagree.

The engineering lesson is sharper than the application list, though. The brute
force is `O(n²)` and dies on large inputs. Two different `O(n log n)` structures
fix it — a **Fenwick tree used as a running counter**, and **merge sort that counts
while it merges**. What the good solution buys is the classic `n²`→`n log n`
collapse: at `n = 100,000`, that's ~10 billion operations down to ~1.7 million.

## Start from the obvious

The definition is a nested loop:

```
for i in range(n):
    for j in range(i+1, n):
        if nums[j] < nums[i]:
            result[i] += 1
```

Honest and obviously correct. But for each `i` it re-scans the entire suffix, and
those suffixes overlap enormously — `O(n²)` total. That repeated re-scanning of the
same tail is the waste.

## Find the waste

Reframe the question. Sweep the array from **right to left**. By the time you reach
position `i`, the set of elements you've *already visited* is exactly the set of
elements to the right of `i`. So the per-element question collapses to:

> Of the values I've seen so far, how many are **strictly smaller** than `nums[i]`?

That's not a search — it's a **count over a growing multiset**: insert values as you
go, and each step ask "how many currently-inserted values are `< x`?" If you can
insert and count-less-than in `O(log n)`, the whole thing is `O(n log n)`.

## The insight — a BIT as a running "count of smaller" oracle

A **Binary Indexed Tree (Fenwick)** is a frequency table that supports a *prefix
sum* in `O(log n)`. Put value-frequencies in it: `add(rank)` records that a value
appeared; `prefix(rank)` returns how many recorded values have rank `≤ that`.

The values can be huge or negative, so first **coordinate-compress**: sort the
distinct values and map each to a small rank `1..m`. Now:

```
for i from right to left:
    r = rank[nums[i]]
    result[i] = bit.prefix(r - 1)   # inserted values strictly smaller than nums[i]
    bit.add(r)                       # record nums[i] as now "seen to the right"
```

The BIT's speed comes from storing sums over power-of-two-sized blocks, indexed by
binary: `prefix` peels off blocks via `i -= i & -i`, `add` climbs covering blocks
via `i += i & -i`. Each touches one node per bit of the index — `O(log n)`. Query
*before* insert so an element never counts itself.

The **merge-sort** approach reaches the same bound differently: sort indices by
value, and during each merge, when you pull a left-half element out, add the number
of right-half elements already taken — those are elements originally to its right
yet smaller. Both are in the solution file.

## Complexity

- **Time:** `O(n log n)`. BIT: `n` inserts + `n` queries, each `O(log n)`; compression
  is one `O(n log n)` sort. Merge sort: the recurrence `T(n) = 2T(n/2) + O(n)`.
- **Space:** `O(n)` — the BIT array and the rank map (or the merge buffers).

## Pitfalls

- **Insert-then-query order.** Query the count *before* inserting the current value,
  or an element counts itself as smaller-than-itself (it isn't).
- **Strict vs. non-strict.** "Strictly smaller" means `prefix(rank - 1)`, not
  `prefix(rank)`. Off by one here silently miscounts every duplicate.
- **Skipping coordinate compression.** Raw values may be up to ±10⁴ here but the
  pattern generalizes to arbitrary ints; without compression the BIT would need a
  slot per possible value. Compress to distinct ranks `1..m`.
- **Merge sort must be stable and sort indices, not values.** You need each original
  index to accumulate its own count; sorting the raw values loses that identity.
- **`n = 0`.** Return `[]` cleanly — empty sorted set, empty BIT, no loop iterations.

## Transfer

The reusable trick is a **BIT (or merge sort) as a "how many earlier/later items are
less than this one" counter** — the general inversion-counting toolkit. Sweep in one
direction, keep a running frequency structure, and turn a per-element `O(n)` scan
into an `O(log n)` prefix query. Siblings: [Range Sum Query - Mutable /
307](../0307-range-sum-query-mutable/) is the same BIT machinery for range sums;
[Reverse Pairs / 493] and [Count of Range Sum / 327] are inversion-counting cousins
solved by the very same merge-sort-with-a-counter or BIT-over-ranks technique.
