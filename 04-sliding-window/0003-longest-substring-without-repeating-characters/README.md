# 3. Longest Substring Without Repeating Characters

**Pattern:** Sliding window (variable size) with a last-seen index (jump, don't crawl)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/longest-substring-without-repeating-characters/

## The problem in plain words

Given a string, find the longest run of characters-in-a-row with no character
repeated. "Substring" means contiguous — inside `pwwkew`, the letters `pwke` don't
count because they aren't next to each other, but `wke` does.

```diagram
   index:   0   1   2   3   4   5
   s:     [ p , w , w , k , e , w ]

   longest clean run:      [ w  k  e ]      length 3
                            (indices 2..4, all distinct)
```

## Why this matters

The real question is: **what's the longest stretch that keeps a "no duplicates"
rule true, and when the rule breaks, how far do I have to move the start to fix
it?** The reusable move is to keep a live window plus a "last place I saw this
character" note, so when a repeat shows up you jump the start past the old copy
instead of crawling forward one step at a time.

That shape is common in text and stream work. Removing duplicate events within a
recent window uses the last-seen note as its memory. Finding the longest activity
stretch with no repeated action, or resetting a window when a conflict appears, is
the same idea. Tokenizers, autocomplete, and log scanners all want the longest
clean span in one left-to-right pass over data you can't rewind.

What the good version buys you is a single pass where the start edge only moves
forward. The slow version restarts and re-walks characters it already checked;
remembering *where* the conflict was lets the start leap ahead once.

## Start from the obvious

For each starting position, extend right, collecting characters into a set. The
instant you'd add a character that's already there, this window has a repeat — stop
and record how long you got.

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

That's about `n × n` steps in the worst case. It's correct, and it pins the goal
down. Now find what it repeats.

## Find the waste

When a start `i` fails at position `j` because of a repeat, the slow version throws
everything away, restarts at `i+1` with an empty set, and re-walks characters it
just looked at. But you already know a lot: the window before `j` was clean, and
the *only* thing that broke it was the character at `j` colliding with an earlier
copy inside the window.

```diagram
   s:  [ a , b , c , b , d ]
        i               j
        start           the second b collides with the b at index 1
        clean: a b c    ^ earlier copy sits here (index 1)

   slow version: restart at i+1 = index 1, rebuild from scratch
   but everything after that earlier b is still clean -- no need to recheck it
```

So there's no reason to restart at `i+1` and inch forward. You can jump the start
**straight to just past that earlier copy** — everything up to there is what made
the window dirty, and everything after it is still clean.

## The insight

Keep a window `s[left..right]` that is always repeat-free, plus a note of each
character's most recent index. Walk `right` across the string. If the current
character was last seen at some index inside the window, move `left` to just past
it — one jump makes the window clean again.

```diagram
   s:  [ a , b , c , b , d ]      last_seen = {}      left = 0

   r=0  a   not seen         window [a]        best 1   {a:0}
        [a]

   r=1  b   not seen         window [a b]      best 2   {a:0, b:1}
        [a b]

   r=2  c   not seen         window [a b c]    best 3   {a:0,b:1,c:2}
        [a b c]

   r=3  b   last seen at 1, inside window -> left jumps to 2
             [c b]           window [c b]      best 3   {...,b:3}
              ^left

   r=4  d   not seen         window [c b d]    best 3   {...,d:4}
             [c b d]
```

`left` only ever moves forward, and `right` moves forward once, so together they
sweep the string a single time.

## Complexity

- **Time: about n steps.** Each index is visited by `right` once; `left` never
  rewinds.
- **Extra memory: about the alphabet size.** The note holds at most one entry per
  distinct character.

## Pitfalls

- **Letting `left` move backward.** On `"abba"`, when the second `a` arrives its
  last-seen index is `0`, but `left` has already moved past it. Only jump `left`
  when the earlier copy sits *inside* the current window (its index is `>= left`),
  or `left` will leap back and corrupt the window.
- On `"dvdf"`, `left` must jump to just past the first `d` (to index 1), not back
  to the start — jumping to "old index + 1" handles this; a naive "reset to 0"
  would not.
- Confusing substring (contiguous) with subsequence — only adjacent characters
  count.
- Empty string returns `0`; a single character (even a space) returns `1`.

## Transfer

This is the variable-size sliding window sharpened with a jump instead of a
one-step shrink: remembering *where* the conflict was lets `left` skip ahead in one
move. The same idea powers
[Longest Repeating Character Replacement / 424](../0424-longest-repeating-character-replacement/)
and [Minimum Window Substring / 76](../0076-minimum-window-substring/). Whenever a
window becomes invalid at a known spot, ask whether you can jump the start straight
to the fix rather than crawling.
