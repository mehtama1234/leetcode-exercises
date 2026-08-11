# 392. Is Subsequence

**Pattern:** Two pointers (one greedy forward walk, no looking back)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/is-subsequence/

## The problem in plain words

`s` is a subsequence of `t` if you can cross out some letters of `t` and what's
left, read in order, spells `s`. Crossing out never lets you reorder — the order
is fixed. So: can you find every letter of `s` inside `t`, in the same order?

```diagram
      s = "abc"
      t = "ahbgdc"
           a  b   c        <- keep these, cross out h, g, d
           |  |   |
           a  b   c  = s   ->  answer: true
```

## Why this matters

Because you can't reorder, matching runs one direction only. Line `s` up against
`t` and sweep forward: whenever `t`'s current letter is the one `s` is waiting
for, take it and move on. There's nothing to gain from going back, so a single
pass is enough — no branching, no bookkeeping of choices.

This in-order matching is real work. Diff tools and version control compare two
file versions by finding the letters, or lines, they share in order. "Did these
steps happen in this order?" — in log analysis, funnel analytics, or intrusion
detection — is exactly this scan. The merge step in merge sort, and merging two
sorted database indexes, use the same forward advance of two pointers.

What you're solving for is one straight pass over `t` with almost no memory,
instead of the branching recursion the problem seems to invite. And it scales:
when you have to test many different `s` strings against one fixed `t`, you
prepare `t` once so each check is cheap.

## Start from the obvious

You might reach for recursion: at each letter of `t`, either use it to match the
next letter of `s`, or skip it, and see if any path uses up all of `s`. That
explores a branching tree of choices — far more machinery than this needs.

Here's the observation that collapses it: because crossing out preserves order,
you **never need to reconsider a letter of `t` once you pass it.** There's no
better choice hiding behind you — so one forward walk is enough.

## The insight

Keep one pointer `i` into `s`, marking the next letter you still need. Sweep
through `t` left to right. Each time `t`'s current letter is exactly `s[i]`,
advance `i`. Ignore everything else.

```diagram
   s = "abc"   t = "ahbgdc"     i marks the next letter of s we need

   t: a  h  b  g  d  c
      ^                 t=a, s[0]=a  match  -> i=1
         ^              t=h, s[1]=b  no
            ^           t=b, s[1]=b  match  -> i=2
               ^        t=g, s[2]=c  no
                  ^     t=d, s[2]=c  no
                     ^  t=c, s[2]=c  match  -> i=3
                        i reached end of s  ->  true
```

If `i` walks off the end of `s`, every letter was matched in order — true. If `t`
runs out first, it couldn't supply them — false.

**Why grabbing the earliest match is safe:** when the letter you need shows up,
taking it now is never worse than waiting for a later copy. Taking it early leaves
the longest possible remaining tail of `t` for the rest of `s`. So "skip this
match, hope for a better one" can never help.

```diagram
   s = "aa"   t = "a b a a"
   need first a: take the first one  ->  leaves "b a a" (has two a's, fine)
   if you skipped it                 ->  leaves "a a"   (only just enough)
   taking early never leaves you shorter.
```

## Complexity

- **Time: about the length of `t`.** One pass over `t`; `s` is consumed along the
  way.
- **Extra memory: a fixed small amount.** Just the two indices.

## Pitfalls

- An empty `s` is a subsequence of *anything*, including empty `t` — return true.
  The `i == len(s)` check handles it because `i` starts already at the end.
- Guard `i < len(s)` before reading `s[i]`, or you read past the end once `s` is
  fully matched.
- Don't test only that every letter of `s` *appears* in `t` — order matters.
  `"axc"` fails against `"ahbgdc"` even though a, x?, c all seem present.

## Transfer

The pattern is **one greedy forward pass, because order is fixed and there's
nothing to gain from looking back.** It's the same two-pointer merge motion in
[Merge Sorted Array](../../03-two-pointers/). And the follow-up scales it: when
you must check *many* different `s` strings against one fixed `t`, you prepare `t`
once (a map from each letter to a sorted list of its positions, then binary
search) so every check is fast — a natural next step once this scan feels
automatic.
