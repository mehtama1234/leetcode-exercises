# 647. Palindromic Substrings

**Pattern:** Dynamic programming (interval / substring table) → expand-around-center
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/palindromic-substrings/

## The problem in plain words

Count how many substrings of `s` read the same forwards and backwards. A substring
is any contiguous slice, and each different start/end pair counts on its own — so
in `"aaa"` the three single `a`s are three separate palindromes.

```diagram
   s = "aaa"      6 palindromic substrings:

   a . .   -> "a"        . a .   -> "a"        . . a   -> "a"
   a a .   -> "aa"       . a a   -> "aa"
   a a a   -> "aaa"

   (three singles + two pairs + one triple = 6)
```

## Why this matters

The deeper move is **counting all mirror-symmetric regions in a sequence while
reusing already-decided interiors.** The recurrence — a span is a palindrome only
when its ends match and its inside already is — lets each larger palindrome grow
from a smaller one instead of being re-checked from scratch.

Counting symmetric regions is a real task. In DNA and RNA, palindromic sites mark
restriction-enzyme recognition points and binding regions, so tallying inverted
repeats is routine. Counting mirrored motifs in text, logs, or signals feeds
anomaly detection, and palindrome density can be a text feature for ML or a
data-quality check.

The fast version buys time: brute force is about `n³` because each substring's
check re-walks overlapping interiors, while reusing those interiors reaches about
`n²` — and expand-around-center does it in constant extra space by riding one
growing window instead of storing the whole table.

## Start from the obvious

There are about `n² / 2` substrings. Generate every one and check each for being a
palindrome:

```
count = 0
for i in range(n):
    for j in range(i, n):
        if s[i:j+1] == s[i:j+1][::-1]:
            count += 1
```

Correct, and the honest first move. But there are about `n²` substrings and
checking each palindrome takes about `n` work, giving about `n³`. Look at *why*
the check is slow.

## Find the waste

To test whether `s[i..j]` is a palindrome, you compare its ends and then walk
inward — re-examining `s[i+1..j-1]`, which you may have already judged on an
earlier pass. The same inner stretches get re-decided again and again.

The escape is a recurrence. A stretch of text is a palindrome exactly when

> its **two ends match** *and* the part **strictly inside** is also a palindrome.

```
dp[i][j] = (s[i] == s[j]) and (j - i < 2 or dp[i+1][j-1])
```

The `j - i < 2` clause is the base case: a single character or an adjacent pair has
no interior to check, so matching ends alone make it a palindrome.

## The insight

Two ways to use that recurrence.

**Tabulation (the teaching form).** Fill a boolean table `dp[i][j]` where `i` is
the start and `j` the end. Each cell depends on the cell **diagonally inside** it,
`dp[i+1][j-1]` — one row down, one column left. So fill short spans before long
ones (in code: `i` descending, `j` ascending), and the inner answer is always
ready. Count every `True`.

```diagram
   s = "aba"     dp[i][j] = is s[i..j] a palindrome?
   rows = i (start), cols = j (end); only j >= i is used

          j=0   j=1   j=2
        +-----+-----+-----+
   i=0  |  T  |  F  |  ?  |     dp[0][2] depends on dp[1][1]
        +-----+-----+-----+          (diagonally inside: down 1, left 1)
   i=1  |     |  T  |  F  |
        +-----+-----+-----+
   i=2  |     |     |  T  |
        +-----+-----+-----+

   dp[0][2]:  s[0]=='a' == s[2]=='a'  AND  dp[1][1] is T
              so dp[0][2] = T  ->  "aba" counts
```

The diagonal is the whole trick — each longer palindrome reads exactly one
already-solved shorter one:

```diagram
   the dependency arrow, drawn on the grid:

        dp[i+1][j-1]  ---->  dp[i][j]
             ^                  |
        inner span          outer span (one wider on each side)
        (down 1, left 1)    reads its ends s[i], s[j]

   fill order: shortest spans first, so the inner cell is always ready
```

Count all four `True` cells (three singles + `"aba"`) → answer 4. This is about
`n²` time and about `n²` space.

**Expand around center (the optimal form).** Read the recurrence from the inside
out. Every palindrome grows outward from a center — either a single character (odd
length) or the gap between two characters (even length), `2n - 1` centers in all.
From each, push two pointers outward while the characters still match; every
successful step *is* one more palindrome (that's the same `dp[i+1][j-1] ->
dp[i][j]` growth). This rides one expanding window instead of storing the table, so
it's about `n²` time but only constant space.

## Complexity

- **Brute force:** about `n³` time — about `n²` substrings times an about-`n`
  check.
- **DP table:** about `n²` time, about `n²` space.
- **Expand around center:** about `n²` time, constant space — the natural
  endpoint.

## Pitfalls

- Forgetting the even-length centers. You need both `expand(i, i)` and
  `expand(i, i+1)`; missing the second undercounts palindromes like `"aa"`.
- In the table version, filling in the wrong order so `dp[i+1][j-1]` isn't ready
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
