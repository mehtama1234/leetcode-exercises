# 496. Next Greater Element I

**Pattern:** Monotonic stack (decreasing)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/next-greater-element-i/

## The problem in plain words

You have a big list `nums2` of distinct numbers and a small list `nums1` whose
values all appear in it. For each value in `nums1`, look at where it sits inside
`nums2` and find the **first number to its right that is bigger**. If nothing to
the right is bigger, the answer is `-1`.

## Why this matters

The core operation is *"next greater element"*: for every position, who is the
next thing downstream that beats it? Answering that for one element is trivial;
answering it for *all* of them in one pass — without re-scanning — is the skill.

Concrete places this shows up: financial series, where "the next day the price
exceeds today's" bounds a run or a drawdown; scheduling and monitoring, where you
want the next event that crosses a threshold after each event; and compilers /
expression evaluation, where a stack tracks operators still waiting for a bigger
one to their right. The dual (next *smaller*) underlies span and histogram
problems.

What the good solution buys is time and reuse. Brute force re-walks `nums2` for
every query — O(n·m). The monotonic stack precomputes the answer for **every**
element of `nums2` in one O(m) pass, then serves each `nums1` query in O(1) from a
map. You pay once for a structure that answers everyone.

## Start from the obvious

Do exactly what the problem says: find the value in `nums2`, then scan rightward
until you hit something bigger.

```
for x in nums1:
    j = index of x in nums2
    scan k from j+1: first nums2[k] > x  ->  answer, else -1
```

Honest and correct. But each query independently re-scans `nums2`, so it's
`O(n * m)`, and adjacent queries redo nearly identical scans.

## Find the waste

"Next greater element" is a fixed property of each position in `nums2` — it does
not depend on which queries we ask. Yet the brute force rediscovers it per query.
Compute it **once for every element of `nums2`**, store it in a map, then each
`nums1` lookup is O(1).

## The insight

Sweep `nums2` left to right holding a stack of values that are still **waiting**
for their next greater element — a stack whose values strictly decrease from
bottom to top. When the current value `x` is larger than the top, `x` is exactly
the next greater element the top was waiting for: pop it and record the pair.

```
for x in nums2:
    while stack and stack[-1] < x:
        next_greater[stack.pop()] = x   # x resolves this waiting value
    stack.append(x)
# leftovers on the stack have no greater element -> -1
answer = [next_greater.get(x, -1) for x in nums1]
```

Why monotonic gives O(n): a value stays on the stack only while nothing bigger
has appeared. The first bigger value resolves it and pops it — for good. Each
value is pushed once and popped at most once, so the whole sweep is linear, and
every pop "resolves" one element's next-greater answer permanently.

## Complexity

- **Time:** `O(n + m)` — one pass over `nums2` builds the map, one pass over
  `nums1` reads it. (Brute force is `O(n * m)`.)
- **Space:** `O(m)` for the map and the stack.

## Pitfalls

- Using `<=` vs `<`: values are distinct here so it doesn't bite, but with
  duplicates the strictness decides whether equal values resolve each other.
- Forgetting the `-1` default for values never popped (no greater element right).
- `nums2.index(x)` in the brute force is itself O(m) — part of why it's slow.
- Assuming `nums1` is contiguous inside `nums2`; it's only a *subset* of values,
  which is exactly why precompute-then-lookup is the clean structure.

## Transfer

This is the plain **next-greater-element** template. Its close relatives keep the
same stack, different framing:
[Next Greater Element II / 503](https://leetcode.com/problems/next-greater-element-ii/)
(circular array), [Daily Temperatures / 739](https://leetcode.com/problems/daily-temperatures/)
(distance to next warmer day), and
[Online Stock Span / 901](../0901-online-stock-span/) (nearest greater to the
*left*, streamed). The histogram and rainwater problems are the "nearest smaller"
mirror. Whenever you need "next bigger/smaller for everyone," reach for a
monotonic stack.
