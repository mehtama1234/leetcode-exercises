# 5. Longest Palindromic Substring

**Pattern:** Dynamic programming (substring table) → expand-around-center
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/longest-palindromic-substring/

## The problem in plain words

Find the longest contiguous slice of `s` that reads the same both ways. In
`"babad"` the answer is `"bab"` (or `"aba"` — ties are fine). In `"cbbd"` it's
`"bb"`.

## Start from the obvious

Every substring, checked for being a palindrome, keep the longest:

```
best = ""
for i in range(n):
    for j in range(i, n):
        sub = s[i:j+1]
        if sub == sub[::-1] and len(sub) > len(best):
            best = sub
```

Correct, but `O(n^2)` substrings times an `O(n)` palindrome check is `O(n^3)`.
The check is where the waste hides.

## Find the waste

Testing whether `s[i..j]` is a palindrome compares the two ends and then walks
inward — re-checking `s[i+1..j-1]`, a stretch we may already have judged. The same
inner regions get re-examined again and again. The escape is the recurrence:

> a stretch is a palindrome iff its **ends match** and the part **strictly inside**
> is also a palindrome.

```
dp[i][j] = (s[i] == s[j]) and (j - i < 2 or dp[i+1][j-1])
```

`j - i < 2` is the base case: a single character or an adjacent pair has no
interior, so matching ends make it a palindrome outright.

## The insight

**Tabulation (teaching form).** Fill boolean `dp[i][j]`. Each cell depends on the
one diagonally inside it, `dp[i+1][j-1]`, so fill by increasing length (`i`
descending, `j` ascending). Track the widest `True` span. `O(n^2)` time and space.

**Expand around center (optimal).** Read the recurrence from the inside out. Every
palindrome grows outward from a center — a single character (odd length) or the
gap between two characters (even length), `2n - 1` centers total. From each center
push two pointers outward while the ends match; the widest window any center
reaches is the answer. This is the same `dp[i+1][j-1] -> dp[i][j]` growth, but on
one sliding window instead of a stored table — `O(n^2)` time, `O(1)` space.

(There is an `O(n)` method, Manacher's algorithm, but it's an intricate special
case; expand-around-center is the honest, general DP-derived answer.)

## Complexity

- **Brute force:** `O(n^3)` time.
- **DP table:** `O(n^2)` time, `O(n^2)` space.
- **Expand around center:** `O(n^2)` time, `O(1)` space — the natural endpoint.

## Pitfalls

- Handle the empty string and length-1 strings up front so index math doesn't
  reach out of bounds.
- When expanding, the `while` loop overshoots by one step on both sides before it
  stops — pull `left` and `right` back in by one before measuring the window.
- Both odd and even centers are required; skipping even centers misses answers like
  `"bb"`.
- Ties are allowed — don't over-engineer to return a *specific* one.

## Transfer

This is [Palindromic Substrings / 647](../0647-palindromic-substrings/) with the
counter swapped for a "widest so far" tracker — same recurrence, same centers.
The substring-DP shape (`dp[i][j]` from a smaller interval inside it) recurs in
Longest Palindromic Subsequence and other interval DPs.
