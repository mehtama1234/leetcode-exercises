# 131. Palindrome Partitioning

**Pattern:** Backtracking (choose a cut point, prune to valid prefixes)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/palindrome-partitioning/

## The problem in plain words

Cut a string into consecutive pieces so that *every* piece reads the same forward
and backward (a palindrome), and return all the ways to do it. For `"aab"` there
are two: `["a","a","b"]` and `["aa","b"]`. Every character lands in exactly one
piece.

```diagram
   s = "a a b"    the gaps between characters:  a | a | b
                                                  ^   ^  choose which gaps to cut

   cut both gaps   -> ["a","a","b"]
   cut only gap 2  -> ["aa","b"]      ("aa" is a palindrome, ok)
   cut only gap 1  -> ["a","ab"]      X "ab" is not a palindrome
```

## Why this matters

The move here is **segmenting a sequence under a rule on each segment**. A string
of `n` characters has `n-1` gaps between characters, and a partition is a choice
of which gaps to cut — `2^(n-1)` raw ways. The twist: not every cut is legal, so
you're searching a *constrained* partition space, and the art is refusing illegal
branches early.

Segment-under-a-rule is the honest core of real parsing. Breaking a string into
dictionary words, tokenizing input where each token must match a pattern,
splitting a log or DNA sequence into meaningful runs, chunking a stream so each
chunk fits a size/format rule — all choose cut points where each piece must pass a
test.

What the good solution buys is cutting at the moment of choice: you never recurse
past a prefix that already fails the palindrome test, so whole subtrees of doomed
partitions are skipped. Without that you'd generate all `2^(n-1)` partitions and
filter — full work to build answers you throw away.

## Start from the obvious

Generate every possible partition, then keep the ones where all pieces are
palindromes:

```diagram
   for every way to cut "aab":
     ["a","a","b"]  all palindromes   keep
     ["a","ab"]     "ab" bad          THROW AWAY (but only after building it)
     ["aa","b"]     all palindromes   keep
     ["aab"]        "aab" bad         throw away
```

Honest and correct, but wasteful: if the first piece isn't a palindrome, this
still builds out every completion of that bad start before rejecting them. The
rejection should happen the instant the first piece is known to be bad.

## The insight

Fold the test *into* the choice. Walk left to right; at position `start`, try each
possible end for the next piece — but only actually take `s[start..end]` **if it
is a palindrome**. That single `if` is the cut.

```diagram
   cut tree for "aab", branch = "where does the next piece end?"
   (X = pruned because the prefix isn't a palindrome)

                         start=0
        "a" /           "aa" |           "aab" \
        start=1          start=2            X "aab" not palindrome
      "a"/  "ab"\        "b"|
     start=2    X       start=3 (end)
       "b"|   "ab" bad    -> record ["aa","b"]
     (end)
   record ["a","a","b"]
```

```diagram
   backtrack(start):
     if start == n: record a copy of path; return   # cut everything -> valid
     for end in start..n-1:
       if s[start..end] is a palindrome:             # <-- prune
         path.push(s[start..end])                    # choose
         backtrack(end+1)                            # explore the suffix
         path.pop()                                  # un-choose
```

Reaching `start == n` means every character has been placed into a palindromic
piece — a complete valid partition, so record a **copy** of `path`. The palindrome
check is a cheap two-pointer walk from both ends. Because a bad prefix is never
chosen, we never explore any partition built on it.

## Complexity

- **Time: about `n * 2^n` worst case** (e.g. `"aaaa..."`, where every prefix is a
  palindrome so nothing gets cut): up to `2^(n-1)` partitions, each costing about
  `n` to check and copy. On typical strings the palindrome cut trims this sharply.
- **Extra memory: about `n`** — recursion depth and `path`. (You can precompute an
  `is_palindrome[i][j]` table to make each check one step; here the two-pointer
  check is kept for clarity.)

## Pitfalls

- **Off-by-one on the substring.** `s[start:end+1]` includes `end`; the next call
  must start at `end+1`, not `end`, or pieces overlap or repeat.
- **Storing the live `path`** instead of `path[:]` — all stored partitions point
  at one list and end up empty after backtracking.
- Re-checking palindromes from scratch on huge inputs — fine for the constraints,
  but the precomputed table is the standard speedup worth knowing.

## Transfer

"Advance a cursor, take a prefix only if it passes a rule, recurse on the rest" is
the sequence-partition template. It's exactly the shape of Word Break II (prefix
must be a dictionary word) and Restore IP Addresses (each segment must be a valid
octet). Whenever you split a sequence and each piece must satisfy a test, reach
for this cut-and-prune recursion.
