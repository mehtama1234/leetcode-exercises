# 76. Minimum Window Substring

**Pattern:** Sliding window (variable size — grow to satisfy, shrink to minimize)
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/minimum-window-substring/

## The problem in plain words

You have a big string `s` and a small string `t`. Find the *shortest* piece of `s`
(a contiguous chunk) that contains everything in `t` — and duplicates count. If `t`
is `"AABC"`, your chunk must hold at least two `A`s, one `B`, one `C`. If no chunk
works, return `""`.

```diagram
   s = "A D O B E C O D E B A N C"      t = "A B C"

   many chunks cover t; we want the SHORTEST one.

   [A D O B E C]        covers, length 6
              [C O D E B A N C]  covers, length 8
                       [B A N C] covers, length 4   <- shortest
```

## Why this matters

The deeper problem is: **the shortest span of a stream that meets a coverage
requirement** — "contains at least this much of everything I need," with the counts
mattering. The reusable move is *expand until valid, then contract while still
valid*, tracking how close you are to satisfied as a single number so you never
recount a window from scratch.

This "smallest window that covers a requirement" shape is useful. The shortest time
span containing at least one of every event type — a full request, response, ack —
is this. The tightest passage of a document that contains all the query terms is
how a highlighted search snippet gets chosen. The minimal segment containing a
required set of markers shows up in signal and sequence search.

What the good version buys you is turning a re-count-everything approach into one
forward pass. A `formed`/`required` counter makes "is this window valid?" a
one-step check, updated as characters enter and leave, so both edges only move
forward.

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

That's about `n × n` substrings, and each coverage check re-counts characters. It's
correct and it pins down exactly what "covers" means. Now find the waste.

## Find the waste

Two expensive things happen:

1. **Coverage is recomputed from scratch** for every substring, even though
   neighboring windows differ by one character.
2. Once a window covers `t`, making it *longer* can never help — so all that extra
   scanning to the right is pointless. Once covered, what you actually want is to
   pull the **left** edge in and see how small you can get while staying covered.

That's the two-move rhythm of a variable sliding window: **expand until valid, then
contract while valid.**

## The insight

Keep target counts `need` (from `t`) and live counts `window` (for the current
chunk). The trick that makes coverage a one-step check: a counter `formed` = how
many *distinct* required characters have currently hit their full required count.
When `formed` equals the number of distinct characters in `t`, the window covers
`t`.

```diagram
   s = "A D O B E C ...      B A N C"     t = "A B C"   need={A:1,B:1,C:1}

   EXPAND right until formed == 3 (all requirements met):

   [A D O B E C]         window has A,B,C -> formed=3, VALID, len 6
    L         R          record best = 6

   now SHRINK left while still valid:
    [D O B E C]          dropped A -> A missing, formed=2, STOP
     L       R           (best stays 6)

   keep expanding R, later reach the tail:

              [B A N C]  window has A,B,C -> formed=3, VALID, len 4
               L     R   record best = 4  (smaller!)

   shrinking drops B -> formed=2, STOP.  answer = "BANC"
```

- **Expanding** finds coverage.
- **Shrinking** (the inner loop) squeezes each valid window to its smallest and
  stops the moment removing one more character would break coverage.

`formed` turns "is the window valid?" from a full recount into a single comparison,
updated as characters enter and leave. Both `left` and `right` only move forward.

## Complexity

- **Time: about n + m steps.** Building `need` is about `m`; then each character of
  `s` is added by `right` once and removed by `left` at most once.
- **Extra memory: about m.** The `need` and `window` maps hold at most the distinct
  characters of `t`.

## Pitfalls

- **Counting duplicates wrong.** `t = "AA"` needs *two* A's; a set-based "have I
  seen A?" check silently accepts one. Track counts, and only bump `formed` when a
  character reaches *exactly* its needed count (use `==`, not `>=`, so it fires
  once).
- **Shrinking too far.** Drop `formed` only when a removed character falls *below*
  its requirement — an over-supplied character leaving keeps the window valid.
- Forgetting to record the best window *before* you shrink past validity — capture
  it at the top of the shrink loop.
- Empty `s` or `t`, or `t` longer than what `s` can supply → return `""`. Guard the
  "no window ever found" case at the end.
- Returning the length instead of the actual substring — save the best start too.

## Transfer

This is the canonical "grow to satisfy a constraint, then shrink to optimize"
window, and the `formed`/`required` counter — tracking *how close to valid* you are
as a single number — reappears widely:
[Longest Substring Without Repeating Characters / 3](../0003-longest-substring-without-repeating-characters/),
[Longest Repeating Character Replacement / 424](../0424-longest-repeating-character-replacement/),
"smallest subarray with sum at least target," and "permutation in string." Whenever
you need the *shortest* window meeting a coverage condition, reach for
expand-then-contract with a satisfaction counter.
