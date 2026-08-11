# 115. Distinct Subsequences

**Pattern:** 2-D dynamic programming (two-prefix counting grid)
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/distinct-subsequences/

## The problem in plain words

You have a source string `s` and a target `t`. Count how many different ways you can
delete some characters from `s` (without reordering the rest) so that what remains is
exactly `t`. Two ways are different if they keep a different *set of positions*, even
when the leftover text looks identical.

## Why this matters

The core operation is *counting distinct alignments of a pattern inside a sequence
when the same characters can align in many positions.* It's not "does `t` occur?"
(that's easy) — it's "in how many positionally-distinct ways?" That subtlety, where
`aaa` contains `aa` three times, is exactly where naive counting double-counts or
under-counts, and it's why you need to sum "use this character" and "save it for
later" as separate branches.

This shape appears in real work. Counting how many ways a template's required fields
can be filled from an ordered log (which log lines satisfy which slots) is this
count. In bioinformatics, counting occurrences of a motif as a subsequence of a
genome is literally this. Diff and patch tooling that quantifies how many minimal
deletions transform one sequence into another leans on the same grid.

What the good solution buys is `O(m·n)` time versus the `2^m` brute force of trying
every subset of `s`, plus a `O(n)` rolled version that fits a large `s` in tiny
memory.

## Start from the obvious

Walk `s` left to right, matching against `t`. State `(i, j)` = "how many ways to
match the rest of `t` (`t[j:]`) using the rest of `s` (`s[i:]`)":

```
def count(i, j):
    if j == len(t): return 1         # all of t matched
    if i == len(s): return 0         # s ran out, t didn't
    ways = count(i+1, j)             # skip s[i]
    if s[i] == t[j]: ways += count(i+1, j+1)   # also try using s[i]
    return ways
```

When characters match you must count **both** using and skipping — that's the whole
game. Unmemoized it's exponential.

## Find the waste

Only `(m+1)·(n+1)` distinct `(i, j)` states exist, revisited endlessly by the
overlapping recursion. Cache them → `O(m·n)`.

## The insight

Bottom-up, `dp[i][j]` = ways `t[:j]` appears in `s[:i]`:

```
dp[i][j] = dp[i-1][j]                              # ignore s[i-1]
         + (dp[i-1][j-1] if s[i-1] == t[j-1] else 0)  # match s[i-1] to t[j-1]
```

Base: `dp[i][0] = 1` (the empty target matches any prefix one way — delete
everything). A cell needs only the row above, so keep **one row** and iterate `j`
from **high to low**, so `dp[j-1]` still holds the *previous* character's count when
you read it:

```
for c in s:
    for j in range(n, 0, -1):
        if c == t[j-1]: dp[j] += dp[j-1]
```

## Complexity

- **Time:** `O(m·n)` — one pass per grid cell.
- **Space:** `O(n)` rolled (`O(m·n)` full grid).

## Pitfalls

- **Direction of the 1-D update.** Must go `j` high→low. Left-to-right would let a
  single `s`-character match the same `t`-character twice, inflating the count.
- `dp[0] = 1` and it must stay 1 through the whole run — never touch it in the loop
  (the loop stops at `j >= 1`).
- Answers can be large; in languages other than Python you need 64-bit / big-int.
- Empty `t` gives 1 (not 0); `t` longer than `s` gives 0.

## Transfer

The reusable move is *a two-prefix grid where each cell = "skip a source character"
plus (on a match) "consume it," and you sum for counts / max for lengths / min for
costs.* Siblings: [Edit Distance / 72](../0072-edit-distance/) (min over the same
grid), [Interleaving String / 97](../0097-interleaving-string/) (boolean over a
two-prefix grid), [Longest Common Subsequence / 1143](https://leetcode.com/problems/longest-common-subsequence/)
(max over it).
