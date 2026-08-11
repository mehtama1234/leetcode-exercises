# 131. Palindrome Partitioning

**Pattern:** Backtracking (choose a cut point, prune to valid prefixes)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/palindrome-partitioning/

## The problem in plain words

Cut a string into consecutive pieces so that *every* piece reads the same forward
and backward (a palindrome), and return all the different ways to do it. For
`"aab"` there are two: `["a","a","b"]` and `["aa","b"]`. Every character must land
in exactly one piece.

## Why this matters

The primitive here is **segmenting a sequence subject to a validity rule on each
segment**. A string of `n` characters has `n-1` gaps between characters, and a
partition is a choice of which gaps to cut — `2^(n-1)` raw ways. The twist that
makes it interesting: not every cut is legal, so you're searching a *constrained*
partition space, and the art is refusing illegal branches early.

Segment-under-a-rule is the honest core of real parsing. Word-breaking a string
into dictionary words, tokenizing input where each token must match a pattern,
splitting a log or DNA sequence into meaningful runs, chunking a stream so each
chunk satisfies a size/format constraint — all choose cut points where each
resulting piece must pass a test.

What the good solution buys is pruning at the moment of choice: you never recurse
past a prefix that already fails the palindrome test, so entire subtrees of doomed
partitions are skipped. Without that, you'd generate all `2^(n-1)` partitions and
filter — doing full work to build answers you immediately discard.

## Start from the obvious

Generate every possible partition, then keep the ones where all pieces are
palindromes:

```
for every way to cut s into pieces:
    if all pieces are palindromes: keep it
```

Honest and correct, but wasteful: if the very first piece isn't a palindrome, this
still builds out every completion of that bad start before rejecting them. The
rejection should happen the instant the first piece is known to be bad.

## The insight

Fold the test *into* the choice. Walk left to right; at position `start`, try each
possible end for the next piece — but only actually take a piece
`s[start..end]` **if it is a palindrome**. That single `if` is the prune:

```
backtrack(start):
    if start == n: record a copy of path; return   # cut everything, valid partition
    for end in start..n-1:
        if s[start..end] is a palindrome:           # <-- prune
            path.push(s[start..end])                # choose
            backtrack(end+1)                        # explore the suffix
            path.pop()                              # un-choose
```

Reaching `start == n` means every character has been placed into a palindromic
piece — a complete valid partition, so record a **copy** of `path`. The palindrome
check itself is a cheap two-pointer walk from both ends. Because a bad prefix is
never chosen, we never explore any partition that builds on it.

## Complexity

- **Time:** `O(n * 2^n)` in the worst case (e.g. `"aaaa..."`, where every prefix is
  a palindrome so nothing prunes): up to `2^(n-1)` partitions, each costing `O(n)`
  to check and copy. On typical strings the palindrome prune cuts this sharply.
- **Space:** `O(n)` extra — recursion depth and `path` are each `O(n)`. The result
  is the required output. (You can precompute an `is_palindrome[i][j]` DP table to
  make each check `O(1)`; here the two-pointer check is kept for clarity.)

## Pitfalls

- **Off-by-one on the substring.** `s[start:end+1]` includes `end`; the next call
  must start at `end+1`, not `end`, or pieces overlap or repeat.
- **Recording the live `path`** instead of `path[:]` — all stored partitions alias
  and end up empty after backtracking.
- Re-checking palindromes from scratch on huge inputs — fine for the constraints,
  but the DP table is the standard speedup worth knowing.

## Transfer

"Advance a cursor, take a prefix only if it passes a rule, recurse on the rest" is
the sequence-partition template. It's exactly the shape of Word Break II
(prefix must be a dictionary word) and Restore IP Addresses (each segment must be a
valid octet). Whenever you split a sequence and each piece must satisfy a
predicate, reach for this cut-and-prune recursion.
