# 392. Is Subsequence

**Pattern:** Two pointers (greedy scan)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/is-subsequence/

## The problem in plain words

`s` is a subsequence of `t` if you can cross out some letters of `t` and what's
left, read in order, spells `s`. Crossing out never lets you rearrange — order is
fixed. So: can you find every letter of `s` inside `t`, in the same order?

## Why this matters

The fundamental operation is *matching one ordered sequence against another in a
single forward pass, because order is fixed and there's nothing to gain from
looking back.* A greedy two-pointer walk suffices — no backtracking, no DP.

This in-order matching is real work. Diff tools and version control compare two
file versions by finding common subsequences of lines. Streaming pattern and
event-sequence detection — "did these steps happen in this order?" in log
analysis, funnel analytics, or intrusion detection — is exactly this scan. Merge
steps in merge sort and in merging sorted database indexes use the same
two-pointer advance.

What you're solving for is a single O(|t|) pass over an input you consume once,
with O(1) memory, instead of the branching recursion the problem seems to invite.
And the greedy insight scales: when you must test many `s` strings against one
fixed `t`, you preprocess `t` once so each query is cheap — the pattern behind
serving many queries against a static corpus.

## Start from the obvious

You might reach for recursion or DP: at each character of `t`, either use it to
match the next letter of `s` or skip it, and see if any path consumes all of `s`.
That explores a branching tree and is far more machinery than the structure of
the problem needs.

The key observation that collapses it: because deletion preserves order, you
**never need to reconsider a character of `t` once you pass it**. There's no
backtracking to gain from — which means a single forward walk is enough.

## The insight

Keep one pointer `i` into `s`, marking the next letter you still need to find.
Sweep through `t` left to right. Every time `t`'s current character is exactly the
letter `s[i]` you're waiting for, advance `i`. Ignore everything else.

```
i = 0
for ch in t:
    if i < len(s) and ch == s[i]:
        i += 1
return i == len(s)
```

If `i` walks off the end of `s`, you matched all of `s` in order — True. If `t`
runs out first, it couldn't supply them — False.

**Why greedy is correct:** when the letter you need appears, taking the *earliest*
occurrence in `t` is never worse than waiting for a later one. Grabbing it early
leaves the longest possible remaining tail of `t` for the rest of `s`. So there's
no case where "skip this match, hope for a better one later" helps.

## Complexity

- **Time:** `O(|t|)` — one pass over `t`; `s` is consumed along the way.
- **Space:** `O(1)` — just the two indices.

## Pitfalls

- The empty `s` is a subsequence of *anything* (including empty `t`) — return
  True. The `i == len(s)` check handles this because `i` starts already at the
  end.
- Guard `i < len(s)` before reading `s[i]`, or you index out of bounds once `s`
  is fully matched.
- Don't test only that every letter of `s` *appears* in `t` — order matters.
  `"axc"` fails against `"ahbgdc"` even though a, x?, c all seem present.

## Transfer

The pattern is **"one greedy forward pass because order is preserved and there's
nothing to gain from looking back."** It's the same two-pointer merge motion used
in [Merge Sorted Array](../../03-two-pointers/) and in the follow-up to this very
problem: when you must check *many* different `s` strings against one fixed `t`,
you preprocess `t` (e.g. a map from letter → sorted list of positions and binary
search) so each query is fast — a nice next step once this scan is second nature.
