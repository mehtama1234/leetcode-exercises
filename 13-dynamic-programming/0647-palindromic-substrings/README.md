# 647. Palindromic Substrings

**Pattern:** Dynamic programming (interval / substring table) → expand-around-center
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/palindromic-substrings/

## The problem in plain words

Count how many substrings of `s` read the same forwards and backwards. A
substring is any contiguous slice, and each different start/end pair counts on its
own — so in `"aaa"` the three single `a`s are three separate palindromes, not one.
`"aaa"` has 6 in total: `a`, `a`, `a`, `aa`, `aa`, `aaa`.

## Why this matters

The deeper operation is **counting all mirror-symmetric regions in a sequence while reusing already-decided interiors** — the recurrence "a span is a palindrome iff its ends match and the inside already is" lets each larger palindrome grow from a smaller one instead of being re-verified from scratch.

Where counting/enumerating symmetric regions genuinely appears:

- **Bioinformatics** — tallying inverted repeats and palindromic sites in DNA/RNA (restriction-enzyme recognition sites are palindromic), which signal structure and binding regions.
- **Pattern and anomaly detection** — counting mirrored motifs in text, logs, or signals as a structural feature.
- **String-processing features** — palindrome density feeding into ML text features or data-quality checks.

The good solution buys **time**: brute force is `O(n³)` because each substring's check re-walks overlapping interiors, while the DP (or the expand-around-center form) reuses those interiors to reach `O(n²)` time — and expand-around-center does it in `O(1)` extra space by riding one growing window instead of storing the whole table.

## Start from the obvious

There are about `n^2 / 2` substrings. Generate every one and check each for being
a palindrome:

```
count = 0
for i in range(n):
    for j in range(i, n):
        if s[i:j+1] == s[i:j+1][::-1]:
            count += 1
```

Correct, and the honest first move. But there are `O(n^2)` substrings and checking
each palindrome takes `O(n)`, giving `O(n^3)`. Staring at *why* the check is slow
shows the fix.

## Find the waste

When we test whether `s[i..j]` is a palindrome, we compare its ends and then walk
inward — re-examining `s[i+1..j-1]`, which we may have already judged on an earlier
iteration. We keep re-deciding the same inner stretches.

The insight that removes that: a stretch of text is a palindrome exactly when

> its **two ends match** *and* **the part strictly inside is also a palindrome**.

That's a recurrence. Name it:

```
dp[i][j] = (s[i] == s[j]) and (j - i < 2 or dp[i+1][j-1])
```

The `j - i < 2` clause is the base case: a single character or an adjacent pair
has no interior to check, so matching ends alone make it a palindrome.

## The insight

Two ways to use that recurrence:

**Tabulation (the teaching form).** Fill a boolean table `dp[i][j]`. Each cell
depends on the cell diagonally inside it, `dp[i+1][j-1]`, so fill by increasing
length — in code, let `i` descend and `j` ascend so the inner answer is always
ready. Count every `True`. `O(n^2)` time, `O(n^2)` space.

**Expand around center (the optimal form).** Read the recurrence from the inside
out. Every palindrome grows outward from a center — either a single character
(odd length) or the gap between two characters (even length). There are `2n - 1`
possible centers. From each, push two pointers outward while the characters still
match; every successful step *is* one more palindrome (`dp[i+1][j-1] -> dp[i][j]`).
This rides one expanding window instead of storing the whole table, so it's still
`O(n^2)` time but only `O(1)` space.

## Complexity

- **Brute force:** `O(n^3)` time — `O(n^2)` substrings times an `O(n)` check.
- **DP table:** `O(n^2)` time, `O(n^2)` space.
- **Expand around center:** `O(n^2)` time, `O(1)` space — the natural endpoint.

## Pitfalls

- Forgetting the even-length centers. You need both `expand(i, i)` and
  `expand(i, i+1)`; missing the second undercounts palindromes like `"aa"`.
- In the table version, filling in the wrong order so `dp[i+1][j-1]` isn't computed
  yet. Fill by length (or `i` descending).
- Counting each substring once by *value* instead of by *position* — the problem
  wants every start/end pair, so `"aaa"` is 6, not 3.

## Transfer

The "ends match + inner is already solved" recurrence and the expand-around-center
trick carry straight over to
[Longest Palindromic Substring / 5](../0005-longest-palindromic-substring/) — same
centers, but you track the widest instead of counting. The interval-DP shape
(`dp[i][j]` built from a smaller interval inside it) also underlies problems like
Longest Palindromic Subsequence and matrix-chain-style DPs.
