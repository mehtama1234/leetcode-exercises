# 3. Longest Substring Without Repeating Characters

**Pattern:** Sliding window (variable size) + last-seen index
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/longest-substring-without-repeating-characters/

## The problem in plain words

Given a string, find the longest run of characters-in-a-row that has no character
repeated. "Substring" means contiguous — `pwke` inside `pwwkew` doesn't count
because those letters aren't adjacent; `wke` does.

## Why this matters

The real question is **the longest contiguous run over a stream that keeps a "no duplicates" invariant** — and, crucially, when the invariant breaks, jumping the window's start straight past the offending earlier copy instead of crawling. The fundamental operation is maintaining a live window with a "last position I saw this" lookup so you never rescan.

That shape is common in stream processing and text work:

- **Deduplication over a sliding time window** — accepting events only if the same key hasn't appeared recently; the last-seen index is the dedup memory.
- **Session and rate windows** — tracking the longest activity stretch with no repeated action, or resetting a window when a conflict appears.
- **Tokenizers, autocomplete, and log scanners** — finding the longest clean span in a single left-to-right pass over data you can't rewind.

What we're solving for is **a single pass at O(1) amortized work per character**: brute force restarts and re-walks characters (`O(n^2)`), while remembering *where* the conflict was lets the left edge leap ahead once, giving `O(n)` time — essential when the input is a long stream you only get to read once.

## Start from the obvious

For each starting position, extend to the right, collecting characters into a set.
The instant you'd add a character that's already there, this window has a repeat —
stop and record how long you got.

```
best = 0
for each start i:
    seen = set()
    for j from i onward:
        if s[j] in seen: break
        seen.add(s[j])
        best = max(best, j - i + 1)
return best
```

That's `O(n^2)` in the worst case. It's correct, and it makes the goal precise.
Now find what it repeats.

## Find the waste

When a start `i` fails at position `j` (a repeat), the brute force throws away
everything and restarts at `i+1` with an empty set — re-walking characters it just
looked at. But we already know a lot: the window `s[i..j-1]` was clean, and the
*only* thing that broke it was the character at `j` colliding with an earlier copy
inside the window.

So we don't need to restart at `i+1` and inch forward. We can jump the left edge
**directly to just past that earlier copy** — everything up to there is what made
the window dirty, and everything after it is still clean.

## The insight

Keep a window `s[left..right]` that is always repeat-free, plus a dict of each
character's **most recent index**. Walk `right` across the string:

- If the current character was last seen at some index `prev` that lies *inside*
  the window (`prev >= left`), move `left = prev + 1` — one jump makes the window
  clean again.
- Record this character's new index and update the best length.

```
last_seen = {}     # char -> latest index
left = 0
best = 0
for right, ch in s:
    prev = last_seen.get(ch)
    if prev is not None and prev >= left:
        left = prev + 1
    last_seen[ch] = right
    best = max(best, right - left + 1)
return best
```

`left` only ever moves forward, and `right` moves forward once, so together they
sweep the string a single time.

## Complexity

- **Time:** `O(n)` — each index is visited by `right` once; `left` never rewinds.
- **Space:** `O(min(n, a))` where `a` is the alphabet size — the dict holds at
  most one entry per distinct character.

## Pitfalls

- **Letting `left` move backward.** On `"abba"`, when the second `a` arrives its
  last-seen index is `0`, but `left` has already advanced past it. The
  `prev >= left` guard is what stops `left` from jumping *back* and corrupting the
  window.
- On `"dvdf"`, `left` must jump to just past the first `d` (to index 1), not to
  the start — the jump-to-`prev+1` handles this; a naive "reset to 0" would not.
- Confusing substring (contiguous) with subsequence — only adjacent characters
  count.
- Empty string returns `0`; a single character (even a space) returns `1`.

## Transfer

This is the variable-size sliding window sharpened with a "jump" instead of a
one-step shrink: remembering *where* the conflict was lets `left` skip ahead in
one move. The same idea powers
[Longest Repeating Character Replacement / 424](../0424-longest-repeating-character-replacement/)
and [Minimum Window Substring / 76](../0076-minimum-window-substring/). Whenever a
window becomes invalid at a known position, ask whether you can jump the left edge
straight to the fix rather than crawling.
