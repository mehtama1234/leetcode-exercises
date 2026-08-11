# 1143. Longest Common Subsequence

**Pattern:** Dynamic programming (2-D table over two prefixes)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/longest-common-subsequence/

## The problem in plain words

You have two strings. A *common subsequence* is a run of characters that appears
in both, in the same order, but not necessarily next to each other. For `"abcde"`
and `"ace"`, `"ace"` sits inside both in order, so the answer is `3`. You need
only the length, not the string.

```diagram
   text1:  a  b  c  d  e
           |     |     |
           a     c     e        same order, gaps allowed
   text2:  a  c  e

   answer = 3   ("ace")
```

## Why this matters

The core operation is **measuring how much order-preserving structure two
sequences share**, by comparing them prefix against prefix and solving each pair
of prefixes exactly once. The rule — compare the last characters of two prefixes;
if they match, take that character and shrink both, if not, drop one and keep the
better side — is the template for a whole family of two-sequence comparisons.

That grid is literally how `git diff` and merge tools find the common backbone
between two file versions, how DNA and protein alignment scores similarity between
genomes, and how spellcheck ranks near-matches by edit distance.

## Start from the obvious

A subsequence is "keep or drop each character," so brute force is: generate every
subsequence of the first string, check which also appear in the second, return the
longest match.

```
for every subsequence s of text1:
    if s is a subsequence of text2:
        track the max length
```

`text1` has `2^m` subsequences — exponential. But it points at the real question:
we're deciding, character by character, whether a character is shared.

## Find the waste

Think about **prefixes** instead of whole strings, and look at the *last*
character of each. Define:

> `dp[i][j]` = the LCS length of the first `i` characters of `text1` and the
> first `j` characters of `text2`.

Compare `text1[i-1]` and `text2[j-1]`, the last characters of those two prefixes:

- **They match.** That shared character can end a common subsequence. Take it,
  then solve the smaller problem with both last characters removed:
  ```
  dp[i][j] = 1 + dp[i-1][j-1]
  ```
- **They differ.** At least one of the two last characters isn't in the LCS. You
  don't know which, so try dropping each and keep the better:
  ```
  dp[i][j] = max(dp[i-1][j], dp[i][j-1])
  ```

Row 0 and column 0 are all `0` (an empty prefix shares nothing). Fill with `i`,
`j` both increasing, and every cell you read is already done. The answer is
`dp[m][n]`.

```diagram
   text1 = "abcde" (down)    text2 = "ace" (across)

          ""  a   c   e
      ""   0   0   0   0
      a    0   1   1   1
      b    0   1   1   1
      c    0   1   2   2
      d    0   1   2   2
      e    0   1   2   3   <- answer

   how the corner cell (e, e) got its 3:
      text1[i-1]='e' == text2[j-1]='e'  -> MATCH
      dp[e][e] = 1 + dp[d][c] = 1 + 2 = 3
```

```diagram
   each cell reads three neighbors — up, left, and the diagonal:

              dp[i-1][j-1]   dp[i-1][j]
                   \             |
                    \            v
        dp[i][j-1] --> [ dp[i][j] ]

   match at the last chars  ->  pull the DIAGONAL + 1
   mismatch                 ->  take max(up, left)
```

The brute force re-tests the same prefix pair from many different subsequences.
Here each `(i, j)` pair is solved exactly once.

## The space optimization

Look at which cells `dp[i][j]` reads: the diagonal `dp[i-1][j-1]`, the one above
`dp[i-1][j]`, and the one to the left `dp[i][j-1]` — all in the current row or the
one directly above. It never reaches two rows back. So keep just **two rows**
(previous and current) instead of the full `m × n` grid. Making the shorter string
index the columns drops the memory to about `min(m, n)`.

The one gotcha: `dp[i-1][j-1]` is the diagonal — column `j-1` in the *previous*
row. A single-array version must stash it before overwriting; the two-row version
in `solution.py` reads `prev[j-1]` directly and sidesteps that.

## Complexity

- **Brute force:** `2^m` subsequences.
- **2-D DP:** about m × n steps and m × n memory.
- **Rolling rows:** about m × n steps, about `min(m, n)` memory.

## Pitfalls

- Index shift: `dp[i][j]` uses the *first `i`* characters, so the last one is
  `text1[i-1]`, not `text1[i]`. Off-by-one here is the classic bug.
- Confusing **subsequence** (order kept, gaps allowed) with **substring**
  (contiguous). This is subsequence.
- Forgetting the zero-filled first row and column; without those base cases the
  recurrence has nothing to stand on.

## Transfer

This "compare the last characters of two prefixes" grid is the template for a
whole family: [Edit Distance / 72](https://leetcode.com/problems/edit-distance/),
[Longest Common Substring](https://en.wikipedia.org/wiki/Longest_common_substring_problem)
(reset to 0 on mismatch instead of taking the max), and
[Distinct Subsequences / 115](https://leetcode.com/problems/distinct-subsequences/).
Any time two sequences are compared position by position, reach for the 2-D prefix
table.
