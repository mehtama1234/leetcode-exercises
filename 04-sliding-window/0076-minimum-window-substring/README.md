# 76. Minimum Window Substring

**Pattern:** Sliding window (variable size, "grow to satisfy, shrink to minimize")
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/minimum-window-substring/

## The problem in plain words

You have a big string `s` and a small string `t`. Find the *shortest* piece of
`s` (a contiguous chunk) that contains everything in `t` — and duplicates count.
If `t` is `"AABC"`, your window must contain at least two `A`s, one `B`, one `C`.
If no chunk works, return `""`.

## Why this matters

The deeper problem is finding the **shortest span of a stream that satisfies a coverage requirement** — "contains at least this much of everything I need" — with the counts mattering. The fundamental operation is *expand until valid, then contract while still valid*, tracking closeness-to-satisfied as a single integer so you never recount a window from scratch.

This "smallest window that covers a requirement" pattern is genuinely useful:

- **Log and monitoring queries** — the shortest time span containing at least one of every event type you care about (e.g., a full request→response→ack sequence).
- **Search-result snippet generation** — the tightest passage of a document that contains all the query terms, which is how highlighted snippets are chosen.
- **Bioinformatics and signal search** — the minimal segment containing a required set of markers.

What we're solving for is **turning an `O(n^2)`-or-worse recount into `O(n)`**: the `formed`/`required` counter makes "is this window valid?" an O(1) check updated incrementally as characters enter and leave, so both edges only move forward and each character is touched a constant number of times.

## Start from the obvious

Try every substring of `s` and test whether it covers `t`.

```
best = ""
for each start i:
    for each end j > i:
        if s[i..j] contains all of t (with counts):
            keep it if it's the shortest so far
            break   # first cover from i is the shortest starting at i
return best
```

That's `O(n^2)` substrings, and each coverage check re-counts characters — roughly
`O(n^2 * (n + m))`. It's correct and it pins down exactly what "covers" means. Now
find the waste.

## Find the waste

Two expensive things happen:

1. **Coverage is recomputed from scratch** for every substring, even though
   neighboring windows differ by one character.
2. Once a window covers `t`, making it *longer* can never help — so all that extra
   scanning to the right is pointless. What we actually want, once covered, is to
   pull the **left** edge in and see how small we can get while staying covered.

That's the two-move rhythm of a variable sliding window: **expand until valid,
then contract while valid.**

## The insight

Keep target counts `need` (from `t`) and live counts `window` (for the current
chunk). The trick that makes coverage O(1) to check: a counter `formed` = how many
*distinct* required characters have currently hit their full required count. When
`formed` equals the number of distinct characters in `t`, the window covers `t`.

```
expand right, adding s[right] to window
    if that character just reached its needed count: formed += 1
while formed == required:              # window is valid — try to shrink
    record it if it's the smallest so far
    remove s[left] from window
    if that drops a character below its need: formed -= 1
    left += 1
```

- **Expanding** finds coverage.
- **Shrinking** (the inner `while`) squeezes each valid window to its minimum, and
  stops the moment removing one more character would break coverage.

`formed` turns "is the window valid?" from a full recount into a single integer
comparison, updated as characters enter and leave. Both `left` and `right` only
move forward.

## Complexity

- **Time:** `O(n + m)` — building `need` is `O(m)`; then each character of `s` is
  added by `right` once and removed by `left` at most once.
- **Space:** `O(m)` — the `need` and `window` maps hold at most the distinct
  characters of `t` (window may briefly hold more, bounded by the alphabet).

## Pitfalls

- **Counting duplicates wrong.** `t = "AA"` needs *two* A's; a set-based "have I
  seen A?" check silently accepts one. Track counts, and only bump `formed` when a
  character reaches *exactly* its needed count (using `==`, not `>=`, so it fires
  once).
- **Shrinking too far or not enough.** Decrement `formed` only when a removed
  character drops *below* its requirement — an over-supplied character leaving
  keeps the window valid.
- Forgetting to record the best window *before* you shrink past validity — capture
  it at the top of the `while`.
- Edge cases: empty `s` or `t`, or `t` longer than what `s` can supply → return
  `""`. Guard `best_len == infinity` at the end.
- Returning the length instead of the actual substring — save `best_start` too.

## Transfer

This is the canonical "grow to satisfy a constraint, then shrink to optimize"
window, and the `formed`/`required` counter trick — tracking *how close to valid*
you are as an O(1) number — reappears widely:
[Longest Substring Without Repeating Characters / 3](../0003-longest-substring-without-repeating-characters/),
[Longest Repeating Character Replacement / 424](../0424-longest-repeating-character-replacement/),
"smallest subarray with sum ≥ target", and "permutation in string". Whenever you
need the *shortest* window meeting a coverage condition, reach for expand-then-
contract with a satisfaction counter.
