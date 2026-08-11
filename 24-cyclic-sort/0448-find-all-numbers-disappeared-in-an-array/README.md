# 448. Find All Numbers Disappeared in an Array

**Pattern:** Index-as-hash / sign marking (the array is its own hash table)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/find-all-numbers-disappeared-in-an-array/

## The problem in plain words

You have a list of length n where every value is between 1 and n. Some values in
1..n are present (maybe more than once), and some never show up at all. Return the
ones that never show up — ideally in one pass with no extra memory.

## Why this matters

This is the mirror of "find the duplicates": same machinery, opposite question.
The underlying operation is presence-tracking over a bounded domain — "which of
1..n did I see?" — done without a separate table, by letting the array's own slots
hold the marks. Value `v` lives at index `v-1`; visiting `v` flips the sign of the
number there; whatever slot stays positive at the end was never visited, so its
index+1 is a value that disappeared.

That "walk the whole domain, mark as you go, then read off the unmarked" shape is
how real systems reconcile completeness. Detecting gaps in a sequence of message
IDs or ledger entries to know what to re-request is exactly this. A bitmap of
"which fixed blocks/slots are free" answers the same disappeared-vs-present
question. Attendance and reconciliation checks — which expected records didn't
arrive — are this pattern with domain names.

What the good solution buys is O(1) extra space and a single linear pass: you list
every missing value without building a set the size of the input, keeping the
memory footprint flat as n grows.

## Start from the obvious

Build the set of what's present, then walk 1..n and collect anything absent:

```
present = set(nums)
return [v for v in range(1, n+1) if v not in present]
```

Correct, but the set costs O(n) extra memory. Since the values are exactly 1..n,
the array we already hold can play the set's role.

## Find the waste

The set only records one bit per value: "did v appear?". We're paying for a full
hash table to store n booleans, when the array already has n slots and every value
`v` has a private home at index `v-1`. Hide the "seen" bit at that home slot and
the set disappears.

The place to hide a bit without destroying the value is the **sign**: keep
magnitudes (so `abs` still names each value) and let a negative sign mean "this
value's home was visited."

## The insight

**Mark each value's home negative; unmarked homes reveal the missing values.**

Pass 1 — for each entry, jump to its home `abs(x) - 1` and flip that slot negative
(only if it's still positive, to avoid double-negating back to positive):

```
for x in nums:
    home = abs(x) - 1
    if nums[home] > 0:
        nums[home] = -nums[home]
```

Pass 2 — any index `i` whose value is still positive was never marked, so the
value `i + 1` never appeared:

```
return [i+1 for i in range(n) if nums[i] > 0]
```

Using `abs(x)` in pass 1 is essential: an entry may already have been flipped by a
prior mark, but its magnitude still identifies the value whose home to visit.

## Complexity

- **Time:** `O(n)` — two linear passes, O(1) work per element.
- **Space:** `O(1)` extra — marks live in the input array; the output list is the
  required result, not scratch space.

## Pitfalls

- **Reading `nums[i]` instead of `abs(nums[i])`.** After signs flip, the raw value
  can be negative and index the wrong home.
- **Flipping without the `> 0` guard.** A value present twice would flip its home
  twice, turning it positive again and falsely reporting it missing. Guard, or use
  `nums[home] = -abs(nums[home])` to force negative idempotently.
- **Off-by-one.** Home is `value - 1`; the missing value at index `i` is `i + 1`.
- **Relying on this where the range isn't 1..n.** The whole trick depends on that
  bound.

## Transfer

This is the "what's absent" face of the index-as-hash coin; its "what's doubled"
face is [Find All Duplicates / 442](../0442-find-all-duplicates-in-an-array/) —
identical marking, different read-out. Siblings that share the array-as-hash idea:
[First Missing Positive / 41](../0041-first-missing-positive/) (finds the *first*
gap via placement) and
[Find the Duplicate Number / 287](../0287-find-the-duplicate-number/) (same domain,
but mutation is banned so it needs cycle detection instead).
