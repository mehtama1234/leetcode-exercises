# 10. Regular Expression Matching

**Pattern:** 2-D dynamic programming (two-suffix grid with a branching wildcard)
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/regular-expression-matching/

## The problem in plain words

You have a string `s` and a pattern `p`. In the pattern, `.` matches any single
character, and `*` means "zero or more of the character right before it." Decide
whether the pattern matches the *entire* string — not a piece of it, the whole
thing.

```diagram
   s = "aab"     p = "c*a*b"

   c*  -> zero c's   (used 0 times)
   a*  -> two a's    (used 2 times)
   b   -> one b

   "aab" fully consumed  ->  match
```

## Why this matters

The whole difficulty lives in the `*`, because `x*` can stand for any number of
copies — zero, one, five. You can't decide up front how many to use. The move that
untangles it is: don't count copies, offer a binary choice at each step — *skip the
`x*` entirely* or *eat one character and keep the `x*` around for more*. Every count
you could have chosen is reachable by repeating that second option.

This "let a repeated choice cover an unknown quantity" idea is exactly how regex
engines, glob matching, and simple parsers work. And the two-string grid it lives on
is the same grid behind edit distance and subsequence counting — one axis per
string, cells reading nearby cells.

## Start from the obvious

Compare the fronts of the two suffixes (`s[i:]` and `p[j:]`). If the next pattern
piece is a plain character or `.`, it either matches the next `s` character or it
doesn't — advance both, or fail. The one real fork is `x*`:

```diagram
   pattern piece is  x*  (x is a letter or '.')

     option A: use it ZERO times   ->  skip "x*", keep same s
     option B: if x matches s[i]   ->  eat s[i], KEEP "x*" for reuse

   answer = A  OR  B
```

Write that as recursion on `(i, j)` and it's correct. But the same `(i, j)` suffix
pair gets asked about repeatedly through different chains of `*` choices, so plain
recursion re-solves the same states.

## The insight

Let `dp[i][j]` mean *does `s[i:]` match `p[j:]`?* — one axis per string, a grid of
yes/no answers. Fill it from the bottom-right corner (both suffixes empty, which is
a match) back toward `(0, 0)`.

```diagram
   dp[i][j] = does s[i:] match p[j:]

   s = "aa"        p = "a*"
            j:  a    *    ""
       i    +----+----+----+
       a    |    |    |  F |
       a    |    |    |  F |
       ""   |    |    |  T |   empty vs empty = match
            +----+----+----+
   bottom-right seeded True; everything else reads cells below/right of it.
```

Now watch a cell fill. A plain character reads one neighbor (down-and-right on the
diagonal). A `x*` reads two: the cell two columns right (skip the pair) and the cell
directly below (consumed one `s` char, kept the `*`):

```diagram
   filling dp[i][j]

   plain char / '.' :         '  x* '  case:
                              skip pair        consume via *
     dp[i+1][j+1]             dp[i][j+2]       dp[i+1][j]
          ^                        \              |
          |                         \             v
        dp[i][j]                     +---> dp[i][j] = skip OR (x~s[i] AND consume)

   plain:  dp[i][j] = (p[j] matches s[i])  AND  dp[i+1][j+1]
```

Sweep `i` from bottom, `j` from right; the top-left cell `dp[0][0]` is the answer.
The recursion and this table are the same computation — the table just fills the
grid in a safe order instead of recursing.

## Complexity

- **Time: about m × n steps** (m = len `s`, n = len `p`). One cheap decision per
  grid cell. Doubling both roughly quadruples the work.
- **Extra memory: about m × n** for the grid (or the memo cache in the top-down
  version).

## Pitfalls

- Reading `*` as "match anything." It matches zero-or-more of *the one character
  before it*, not any run of any characters.
- Forgetting the zero-copies branch. `x*` must be allowed to vanish — `dp[i][j+2]`
  — even when `x` could match, because using it zero times is often the only path.
- Requiring a partial match. The pattern must cover the whole string; that's why the
  base case is "both suffixes empty," not "`s` empty."
- Peeking at `p[j+1]` without a bounds check before deciding it's a `*`.

## Transfer

The reusable idea is *a two-suffix (or two-prefix) grid where one construct branches
into "skip it" OR "consume one and stay."* The nearest sibling is
[Wildcard Matching / 44](https://leetcode.com/problems/wildcard-matching/) (`*`
matches any run of *any* characters — a simpler branch). It also shares the
two-string grid skeleton with [Edit Distance / 72](../0072-edit-distance/) and
[Distinct Subsequences / 115](../0115-distinct-subsequences/).
