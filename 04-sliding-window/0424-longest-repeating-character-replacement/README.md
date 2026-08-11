# 424. Longest Repeating Character Replacement

**Pattern:** Sliding window (variable size — grow greedily, shrink to stay valid)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/longest-repeating-character-replacement/

## The problem in plain words

You have a string and a budget `k`. You may rewrite up to `k` characters, each to
any letter you like. Afterwards, what's the longest stretch of the *same* letter
you can end up with?

Here's the reframe that unlocks it. Pick a stretch and decide to make it all one
letter. The smart choice is to keep whichever letter already appears most in that
stretch and rewrite the rest. So a stretch works exactly when **the number of
letters that aren't the most common one is at most `k`.**

```diagram
   s = "A A B A B B A"     k = 1

   look at the stretch  [ A B B A ]
     most common letter here: B, appears 2 times
     the rest: A, A -> that's 2 changes needed
     2 > k(1)  -> this stretch is NOT achievable

   look at the stretch  [ B B A ]
     most common: B (2), rest: A (1) -> 1 change
     1 <= k(1)  -> achievable, length 3
```

## Why this matters

The real problem is: **the longest window you can make all-one-letter with a
limited budget of fixes** — at most `k` characters differ from the dominant one.
The reusable move is to grow a window greedily and shrink it just enough to restore
the rule, while tracking the dominant count as you go so the check stays one step.

This "longest run within an error budget" shape is practical. The longest stretch
of a signal or manufacturing run with at most `k` samples out of spec is this. The
longest genomic segment matching a reference with up to `k` mismatches is
approximate matching, same idea. The longest span you can tolerate with at most `k`
dropped packets before quality breaks is the same window.

What the good version buys you is one pass at constant space instead of re-checking
every substring. The window shrinks at most one step per over-budget move, and the
dominant-count updates as characters enter.

## Start from the obvious

Check every substring. For a stretch, count the letters, find the most common one,
and ask: are the leftovers `<= k`?

```
best = 0
for each start i:
    for each end j >= i:
        count letters in s[i..j]
        need = (length of s[i..j]) - (max letter count)
        if need <= k: best = max(best, length)
return best
```

That's about `n × n` substrings, each costing up to `n` (or 26) to count. It's
correct — and it re-counts overlapping substrings constantly. That's the waste.

## Find the waste

Two facts about the "changes needed" number, `length - max_count`:

- As you **grow** a stretch by one character, you only bump one letter's count.
  You never have to recount everything.
- If a stretch is *unfixable* (`need > k`), making it even longer never helps, and
  every stretch *inside* a fixable one is also fixable.

So there's no reason to restart the count for every pair. Slide one window across
the string, adjusting counts as you go.

## The insight

Grow the window on the right. Keep letter counts and `max_freq` — the highest
single-letter count seen in the window. The window is valid while:

```
window_length - max_freq <= k
```

When adding a character breaks that, the window is one-too-big, so nudge `left`
forward by exactly one — that keeps it the largest valid size — and carry on.
Record the best length reached.

```diagram
   s = "A A B A B B A"   k = 1     window = [left..right]

   r=0  A   [A]            len 1, maxf 1, need 0   ok    best 1
   r=1  A   [A A]          len 2, maxf 2, need 0   ok    best 2
   r=2  B   [A A B]        len 3, maxf 2, need 1   ok    best 3
   r=3  A   [A A B A]      len 4, maxf 3, need 1   ok    best 4
   r=4  B   [A A B A B]    len 5, maxf 3, need 2 > k -> shrink
            [A B A B]      left moves 0 -> 1       len 4  best 4
   r=5  B   [A B A B B]    len 5, maxf 3, need 2 > k -> shrink
            [B A B B]      left moves 1 -> 2       len 4  best 4
   r=6  A   [B A B B A]    len 5, maxf 3, need 2 > k -> shrink
            [A B B A]      left moves 2 -> 3       len 4  best 4

   answer: 4
```

**Why we don't recompute `max_freq` when shrinking:** the answer can only improve
when some letter's count sets a *new* record. A `max_freq` that's momentarily too
high only makes the window look more fixable than it is — it can never produce a
window longer than one you already legitimately reached. So the best value stays
correct, and you save the recount.

## Complexity

- **Time: about n steps.** `right` and `left` each cross the string once.
- **Extra memory: constant.** The count map holds at most 26 uppercase letters.

## Pitfalls

- Trying to keep `max_freq` perfectly accurate on shrink (recomputing it). It's
  unnecessary and turns the loop into `26 × n` work for no gain.
- Shrinking more than one step per over-budget move — this window only needs to
  drop *one* character each time, so a single `if` is right, not a `while`.
- Forgetting the empty string returns `0`.
- Thinking you must actually decide *which* letter to keep. You never fix a letter;
  you track the max count and let the arithmetic decide.

## Transfer

This is the "longest window that stays valid" template: grow greedily, shrink just
enough to restore the rule, keep the best length. The same skeleton solves
[Longest Substring Without Repeating Characters / 3](../0003-longest-substring-without-repeating-characters/),
Max Consecutive Ones III, and "longest subarray with at most k of something." The
only thing that changes per problem is the validity test.
