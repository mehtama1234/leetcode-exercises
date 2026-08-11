# 1143. Longest Common Subsequence

**Pattern:** Dynamic programming (2-D table over two prefixes)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/longest-common-subsequence/

## The problem in plain words

You have two strings. A *common subsequence* is a run of characters that appears
in both, in the same order, but not necessarily next to each other. For `"abcde"`
and `"ace"`, `"ace"` appears in both in order, so the answer is `3`.

You only need the length, not the actual string.

## Start from the obvious

A subsequence is "keep or drop each character", so brute force is: generate every
subsequence of the first string, check which ones also appear in the second, and
return the longest match.

```
for every subsequence s of text1:
    if s is a subsequence of text2:
        track max length
```

`text1` has `2^m` subsequences — exponential. But it hints at the right question:
we're really deciding, character by character, whether a character is shared.

## Find the waste

Instead of whole strings, think about **prefixes**, and look at the *last*
character of each. Define:

> `dp[i][j]` = length of the LCS of `text1[:i]` and `text2[:j]`
> (the first `i` and first `j` characters).

Now compare `text1[i-1]` and `text2[j-1]`, the last characters of those prefixes:

- **They match.** Great — that character can be the *end* of a common
  subsequence. Take it, then solve the smaller problem with both last characters
  removed:
  ```
  dp[i][j] = 1 + dp[i-1][j-1]
  ```
- **They differ.** Then at least one of these two last characters is not part of
  the LCS. We don't know which, so try dropping each and keep the better:
  ```
  dp[i][j] = max(dp[i-1][j], dp[i][j-1])
  ```

The base cases are free: an empty prefix shares nothing, so row 0 and column 0
are all `0`. Fill the grid with `i`, `j` both increasing and every cell you read
(`i-1`, `j-1`) is already computed. The answer sits in `dp[m][n]`.

Notice what this kills: the brute force re-tests the same prefix pair from many
different subsequences. Here each `(i, j)` prefix pair is solved exactly once.

## The space optimization

Look at which cells `dp[i][j]` depends on: `dp[i-1][j-1]`, `dp[i-1][j]`, and
`dp[i][j-1]` — all in the current row or the one directly above. We never reach
further back than one row. So keep just **two rows** (previous and current)
instead of the full `m × n` grid, dropping space to `O(min(m, n))` if you make
the shorter string index the row.

The one gotcha: `dp[i-1][j-1]` is the diagonal — the value at column `j-1` in the
*previous* row. In a true single-array rolling version you must stash it before
overwriting; the two-row version in `solution.py` sidesteps that by reading
`prev[j-1]` directly.

## Complexity

- **Brute force:** `O(2^m · n)` time.
- **2-D DP:** `O(m·n)` time, `O(m·n)` space.
- **Rolling rows:** `O(m·n)` time, `O(min(m, n))` space.

## Pitfalls

- Index shift: `dp[i][j]` uses the *first `i`* characters, so the last one is
  `text1[i-1]`, not `text1[i]`. Off-by-one here is the classic bug.
- Confusing **subsequence** (order preserved, gaps allowed) with **substring**
  (contiguous). This problem is subsequence.
- Forgetting the zero-filled first row/column; without those base cases the
  recurrence has nothing to stand on.

## Transfer

This "compare the last characters of two prefixes" grid is the template for a
whole family: [Edit Distance / 72](https://leetcode.com/problems/edit-distance/),
[Longest Common Substring](https://en.wikipedia.org/wiki/Longest_common_substring_problem)
(reset to 0 on mismatch instead of taking the max), and
[Distinct Subsequences / 115](https://leetcode.com/problems/distinct-subsequences/).
Any time two sequences are compared position by position, reach for the 2-D
prefix table.
