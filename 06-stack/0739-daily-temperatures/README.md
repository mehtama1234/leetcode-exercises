# 739. Daily Temperatures

**Pattern:** Monotonic stack (next-greater-element)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/daily-temperatures/

## The problem in plain words

You have a list of daily temperatures. For each day, answer: how many days do you
wait until it gets warmer than today? If it never gets warmer, the answer is `0`.
So `[73, 74, 75, 71, 69, 72, 76, 73]` gives `[1, 1, 4, 2, 1, 1, 0, 0]`.

## Start from the obvious

For each day, just walk forward until you hit a hotter day and count the steps.

```
for each i:
    for j from i+1 onward:
        if temps[j] > temps[i]:
            answer[i] = j - i; break
```

Correct, and worth writing first. But watch what happens on a long stretch of
cooling weather: day 0 scans the whole tail, then day 1 scans almost the same
tail, and so on. Every early day re-walks the same future days. That repetition is
`O(n^2)`, and it's the thing to kill.

## Find the waste

Flip the question around. Instead of each day searching forward for its warmer
day, ask: **when a warm day arrives, which earlier days was it waiting to answer?**

A hot day today "answers" every earlier day that is still waiting *and* cooler than
today. And notice the days that are still waiting must form a **decreasing** run of
temperatures — if an earlier waiting day were cooler than a later waiting day, the
later day would already have answered it. So the set of unresolved days, read from
oldest to newest, is temperatures going *down*.

"Keep the still-waiting days, newest on top, temperatures decreasing" is a
**monotonic stack**.

## The insight

Keep a stack of the *indices* of days that haven't found a warmer day yet. Walk the
list once. For each new day `i` with temperature `t`:

1. While the day on top of the stack is **cooler** than `t`, it just found its
   warmer day — today. Pop it and set its answer to `i - poppedIndex`.
2. Push `i`; now it waits for *its* warmer day.

```
for i, t in temps:
    while stack and temps[stack[-1]] < t:
        prev = stack.pop()
        answer[prev] = i - prev
    stack.append(i)
```

Every index is pushed once and popped at most once, so even with the inner `while`
the total work is linear.

## Complexity

- **Time:** `O(n)` — each index enters and leaves the stack exactly once; the inner
  loop's total pops across the whole run is at most `n`.
- **Space:** `O(n)` — a strictly decreasing input (`[90, 80, 70]`) keeps every day
  on the stack at once. The `answer` array is `O(n)` too.

## Pitfalls

- **Strict vs. non-strict:** "warmer" means strictly greater. Use `<` in the while
  (pop only when top is *cooler*), so equal temperatures like `[50, 50, 50]` do not
  count and stay `0`.
- **Store indices, not temperatures:** the answer is a day *gap* `i - prev`, so the
  stack must hold indices to compute it.
- **Leftovers stay 0:** days still on the stack at the end never warmed up — leave
  their pre-filled `0`. Don't try to "finish" them.
- Don't reset or re-scan; the point is a single pass.

## Transfer

This is the **next-greater-element** template, and the monotonic stack behind it
recurs widely:
[Next Greater Element I / 496](../../06-stack/0496-next-greater-element-i/),
[Largest Rectangle in Histogram / 84](../0084-largest-rectangle-in-histogram/),
[Trapping Rain Water / 42](../../03-two-pointers/0042-trapping-rain-water/),
[Car Fleet / 853](../0853-car-fleet/). Whenever you need, for each item, the next
item that beats it, keep a stack that stays sorted and pop as each new item
resolves the ones it dominates.
