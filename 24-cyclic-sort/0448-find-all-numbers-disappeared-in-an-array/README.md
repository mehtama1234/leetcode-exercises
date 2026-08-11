# 448. Find All Numbers Disappeared in an Array

**Pattern:** Index-as-hash / sign marking (the array is its own lookup table)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/find-all-numbers-disappeared-in-an-array/

## The problem in plain words

You have a list of length `n` where every value is between 1 and `n`. Some values in
`1..n` are present (maybe more than once), and some never show up at all. Return the ones
that never show up — ideally in one pass with no extra memory.

```diagram
   nums = [4, 3, 2, 7, 8, 2, 3, 1]     n = 8, so we expect 1..8

   present: 1, 2, 3, 4, 7, 8      missing: 5, 6
   answer = [5, 6]
```

## Why this matters

This is the mirror of "find the duplicates": same machinery, opposite question. The
underlying operation is presence-tracking over a bounded range — "which of `1..n` did I
see?" — done without a separate table, by letting the array's own slots hold the marks.
Value `v` lives at index `v-1`; visiting `v` flips the sign of the number there;
whatever slot stays positive at the end was never visited, so its index+1 is a value that
disappeared.

That "walk the whole range, mark as you go, then read off the unmarked" shape is how real
systems check for completeness. Detecting gaps in a sequence of message IDs or ledger
entries — to know what to re-request — is exactly this. A bitmap of "which fixed slots
are free" answers the same disappeared-vs-present question. Reconciliation checks — which
expected records didn't arrive — are this pattern with domain names.

What the good solution buys: constant extra memory and a single linear pass — you list
every missing value without a lookup table the size of the input, keeping the memory
footprint flat as `n` grows.

## Start from the obvious

Build the set of what's present, then walk `1..n` and collect anything absent.

```diagram
   present = {1,2,3,4,7,8}
   1? yes  2? yes  3? yes  4? yes  5? NO  6? NO  7? yes  8? yes
   answer = [5, 6]
```

Correct, but the set is extra memory that grows with the input. Since the values are
exactly `1..n`, the array we already hold can play the set's role.

## Find the waste

The set only records one bit per value: "did `v` appear?". We're paying for a full lookup
table to store `n` yes/no answers, when the array already has `n` slots and every value
`v` has a private home at index `v-1`. Hide the "seen" mark at that home slot and the set
disappears.

The place to hide a mark without destroying the value is the **sign**: keep magnitudes
(so `abs` still names each value) and let a negative sign mean "this value's home was
visited."

## The insight

**Mark each present value's home negative; the homes left positive reveal the missing
values.**

Pass 1 — for each entry, jump to its home `abs(x) - 1` and flip that slot negative (only
if it's still positive, so a value seen twice doesn't flip back to positive).

```diagram
   nums = [4, 3, 2, 7, 8, 2, 3, 1]     flip index (value-1) negative

   x=4 -> idx 3: 7>0 flip    [4, 3, 2, -7, 8, 2, 3, 1]
   x=3 -> idx 2: 2>0 flip    [4, 3, -2, -7, 8, 2, 3, 1]
   x=2 -> idx 1: 3>0 flip    [4, -3, -2, -7, 8, 2, 3, 1]
   x=-7-> idx 6: 3>0 flip    [4, -3, -2, -7, 8, 2, -3, 1]
   x=8 -> idx 7: 1>0 flip    [4, -3, -2, -7, 8, 2, -3, -1]
   x=2 -> idx 1: -3<0 skip   (already marked)
   x=-3-> idx 2: -2<0 skip
   x=1 -> idx 0: 4>0 flip    [-4, -3, -2, -7, 8, 2, -3, -1]
```

Pass 2 — any index `i` whose value is still positive was never marked, so the value
`i + 1` never appeared.

```diagram
   final: [-4, -3, -2, -7,  8,  2, -3, -1]
   index:   0   1   2   3   4   5   6   7
                             ^   ^ indices 4 and 5 stayed positive
   missing values = 4+1, 5+1 = 5, 6
```

Using `abs(x)` in pass 1 is essential: an entry may already have been flipped by a prior
mark, but its magnitude still identifies the value whose home to visit.

## Complexity

- **Time:** about `n` steps — two linear passes, a bit of work per element.
- **Extra memory:** constant — marks live in the input array; the output list is the
  required result, not scratch space.

## Pitfalls

- **Reading `nums[i]` instead of `abs(nums[i])`.** After signs flip, the raw value can be
  negative and index the wrong home.
- **Flipping without the `> 0` guard.** A value present twice would flip its home twice,
  turning it positive again and falsely reporting it missing. Guard, or use
  `nums[home] = -abs(nums[home])` to force negative every time.
- **Off-by-one.** Home is `value - 1`; the missing value at index `i` is `i + 1`.
- **Relying on this where the range isn't `1..n`.** The whole trick depends on that
  bound.

## Transfer

This is the "what's absent" face of the index-as-hash coin; its "what's doubled" face is
[Find All Duplicates / 442](../0442-find-all-duplicates-in-an-array/) — identical
marking, different read-out. Siblings that share the array-as-lookup-table idea:
[First Missing Positive / 41](../0041-first-missing-positive/) (finds the *first* gap via
placement) and
[Find the Duplicate Number / 287](../0287-find-the-duplicate-number/) (same range, but
mutation is banned so it needs cycle detection instead).
