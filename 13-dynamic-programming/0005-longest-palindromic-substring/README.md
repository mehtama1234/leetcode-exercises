# 5. Longest Palindromic Substring

**Pattern:** Dynamic programming (substring table) → expand-around-center
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/longest-palindromic-substring/

## The problem in plain words

Find the longest contiguous slice of `s` that reads the same both ways. In
`"babad"` the answer is `"bab"` (or `"aba"` — ties are fine). In `"cbbd"` it's
`"bb"`.

```diagram
   s = "babad"
        b a b a d
        \___/          "bab" reads the same both ways, length 3
          \___/        "aba" also length 3 -> either is accepted

   answer: "bab" (or "aba")
```

## Why this matters

Underneath the puzzle is a core string operation: **find the largest region with a
mirror symmetry**, reusing sub-results so you never re-verify the same interior
twice. The reusable idea is the recurrence — a span is symmetric only when its ends
match and its inside already is.

Symmetry-detection-with-reuse is a real task. DNA hairpins and inverted repeats are
reverse-complement palindromes, so finding the longest one flags secondary
structure in RNA and DNA. Detecting mirrored or repeated patterns in text and logs
uses the same expand-from-center idea, and spotting the longest reusable structure
inside data underlies compression and diffing.

The fast version buys time and memory: brute force is about `n³` because it
re-checks overlapping interiors; reusing those already-decided interiors drops it
to about `n²` time and constant space — the difference between "hangs on a long
genome read" and "returns at once."

## Start from the obvious

Check every substring for being a palindrome, keep the longest:

```
best = ""
for i in range(n):
    for j in range(i, n):
        sub = s[i:j+1]
        if sub == sub[::-1] and len(sub) > len(best):
            best = sub
```

Correct, but about `n²` substrings times an about-`n` palindrome check is about
`n³`. The check is where the waste hides.

## Find the waste

Testing whether `s[i..j]` is a palindrome compares the two ends and then walks
inward — re-checking `s[i+1..j-1]`, a stretch you may already have judged. The same
inner regions get re-examined again and again. The escape is a recurrence:

> a stretch is a palindrome iff its **ends match** and the part **strictly inside**
> is also a palindrome.

```
dp[i][j] = (s[i] == s[j]) and (j - i < 2 or dp[i+1][j-1])
```

`j - i < 2` is the base case: a single character or an adjacent pair has no
interior, so matching ends make it a palindrome outright.

## The insight

**Tabulation (teaching form).** Fill a boolean table `dp[i][j]` (`i` = start, `j` =
end). Each cell depends on the one **diagonally inside** it, `dp[i+1][j-1]` — down
one row, left one column — so fill short spans before long ones (`i` descending,
`j` ascending) and track the widest `True` span as you go.

```diagram
   s = "cbbd"     dp[i][j] = is s[i..j] a palindrome?
   rows = i (start), cols = j (end)

          j=0   j=1   j=2   j=3
        +-----+-----+-----+-----+
   i=0  |  T  |  F  |  F  |  F  |   c
        +-----+-----+-----+-----+
   i=1  |     |  T  |  T  |  F  |   b   dp[1][2] = "bb"  <- widest True
        +-----+-----+-----+-----+
   i=2  |     |     |  T  |  F  |   b
        +-----+-----+-----+-----+
   i=3  |     |     |     |  T  |   d
        +-----+-----+-----+-----+

   dp[1][2] ("bb"): ends s[1]=='b' == s[2]=='b', and j-i < 2 (adjacent pair,
   no interior) -> T. Length 2 beats every single char, so best = "bb".
```

The dependency is always that one diagonal step inward:

```diagram
        dp[i+1][j-1]  ---->  dp[i][j]
             ^                  |
        inner span          add s[i] on the left, s[j] on the right;
        (down 1, left 1)    if those two match and the inside was T, this is T

   e.g. dp[0][4] would read dp[1][3]; you can't know the outer span
   until the inner one is filled -> fill shortest spans first
```

This is about `n²` time and about `n²` space.

**Expand around center (optimal).** Read the recurrence from the inside out. Every
palindrome grows outward from a center — a single character (odd length) or the gap
between two characters (even length), `2n - 1` centers total. From each, push two
pointers outward while the ends match; the widest window any center reaches is the
answer. Same `dp[i+1][j-1] -> dp[i][j]` growth, but on one sliding window instead
of a stored table — about `n²` time, constant space.

(There is an about-`n` method, Manacher's algorithm, but it's an intricate special
case; expand-around-center is the honest, general DP-derived answer.)

## Complexity

- **Brute force:** about `n³` time.
- **DP table:** about `n²` time, about `n²` space.
- **Expand around center:** about `n²` time, constant space — the natural
  endpoint.

## Pitfalls

- Handle the empty string and length-1 strings up front so index math doesn't reach
  out of bounds.
- When expanding, the `while` loop overshoots by one step on both sides before it
  stops — pull `left` and `right` back in by one before measuring the window.
- Both odd and even centers are required; skipping even centers misses answers like
  `"bb"`.
- Ties are allowed — don't over-engineer to return a *specific* one.

## Transfer

This is [Palindromic Substrings / 647](../0647-palindromic-substrings/) with the
counter swapped for a "widest so far" tracker — same recurrence, same centers. The
substring-DP shape (`dp[i][j]` from a smaller interval inside it) recurs in Longest
Palindromic Subsequence and other interval DPs.
