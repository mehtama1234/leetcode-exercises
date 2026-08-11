# 424. Longest Repeating Character Replacement

**Pattern:** Sliding window (variable size, "keep the window valid")
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/longest-repeating-character-replacement/

## The problem in plain words

You have a string and a budget `k`. You may rewrite up to `k` characters, each to
any letter you like. Afterwards, what's the longest stretch of the *same* letter
you can end up with?

The key reframe: pick a stretch and decide to make it all one letter. The
smartest choice is to keep whichever letter already appears most in that stretch,
and rewrite the rest. So a stretch is achievable exactly when **the number of
letters that aren't the most common one is at most `k`.**

## Start from the obvious

Check every substring. For `s[i..j]`, count the letters, find the most common
one, and ask: are the leftovers `<= k`?

```
best = 0
for each start i:
    for each end j >= i:
        count letters in s[i..j]
        need = (length of s[i..j]) - (max letter count)
        if need <= k: best = max(best, length)
return best
```

That's `O(n^2)` substrings, each costing up to `O(n)` (or `O(26)`) to count. It's
correct — and it re-counts overlapping substrings constantly. That's the waste.

## Find the waste

Two facts about the "need" number, `length - max_freq`:

- As you **grow** a substring by one character, you only add to one letter's
  count — you never have to recount everything.
- If a substring is *unfixable* (`need > k`), making it even longer never helps,
  and every substring *inside* a fixable one is also fixable.

So there's no reason to restart the count for every pair. Slide a single window
across the string, adjusting counts incrementally.

## The insight

Grow the window on the right. Keep letter counts and `max_freq` (the highest
single-letter count seen in the window). The window is valid while:

```
window_length - max_freq <= k
```

When adding a character breaks that, the window is one-too-big, so nudge `left`
forward by exactly one — that keeps it the largest valid size — and continue.
Record the best length reached.

```
counts = {}, left = 0, max_freq = 0, best = 0
for right, ch in s:
    counts[ch] += 1
    max_freq = max(max_freq, counts[ch])
    if (right - left + 1) - max_freq > k:   # can't fix this window
        counts[s[left]] -= 1
        left += 1
    best = max(best, right - left + 1)
return best
```

**Why we don't recompute `max_freq` when shrinking:** the answer can only improve
when some letter's count sets a *new* record. A `max_freq` that's momentarily
"too high" only makes the window look more fixable than it is, but it can never
produce a window longer than one we already legitimately achieved. So the best
value stays correct, and we save the recount.

## Complexity

- **Time:** `O(n)` — `right` and `left` each advance across the string once.
- **Space:** `O(1)` — the count map holds at most 26 uppercase letters.

## Pitfalls

- Trying to keep `max_freq` perfectly accurate on shrink (recomputing it) — it's
  unnecessary and turns the loop into `O(26n)` for no benefit.
- Moving `left` in a `while` loop that shrinks more than one step — this window
  only needs to drop *one* character per over-budget step, so an `if` is right.
- Forgetting the empty string returns `0`.
- Thinking you must actually decide *which* letter to keep — you never fix a
  letter; you just track the max frequency and let the arithmetic decide.

## Transfer

This is the "longest window that stays valid" template: grow greedily, shrink
just enough to restore a validity condition, track the best length. The same
skeleton solves
[Longest Substring Without Repeating Characters / 3](../0003-longest-substring-without-repeating-characters/),
[Max Consecutive Ones III / 1004], and "longest subarray with at most k of
something". The only thing that changes per problem is the validity test.
