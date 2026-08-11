# 10. Regular Expression Matching

**Pattern:** 2-D dynamic programming (two-suffix grid with a branching wildcard)
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/regular-expression-matching/

## The problem in plain words

Match a string `s` against a pattern `p`. In the pattern, `.` matches any one
character, and `*` means "zero or more of the character right before it" (so `a*` is
any run of `a`s, including none). The whole string must be consumed — a prefix match
doesn't count. Return whether they match.

## Why this matters

The deep operation is *matching against a pattern where one construct (`*`) can
expand to many lengths, so a single position offers a fork you can't resolve
greedily.* Greedy "eat as many as possible" fails — sometimes `a*` must give back
characters so the rest of the pattern can fit. That backtracking is exactly what DP
replaces with a clean two-suffix table, and it's a miniature version of how real
regex engines reason about ambiguity.

This is not a toy: it's the heart of every regex library, `grep`, and lexer/tokenizer.
Log filtering, input validation, search-and-replace, syntax highlighting, and route
matching in web frameworks all run a pattern matcher with this zero-or-more
branching. Understanding the `*` recurrence is understanding why a badly written
pattern can blow up (catastrophic backtracking) — and why the DP form doesn't.

What the good solution buys is `O(m·n)` time, turning the exponential backtracking of
naive `*`-expansion into one pass over a grid — a bounded, predictable cost.

## Start from the obvious

Compare the fronts of `s[i:]` and `p[j:]`. A plain character or `.` must match, then
both advance. The only branch is when the pattern char is followed by `*`:

```
def match(i, j):
    if j == len(p): return i == len(s)
    first = i < len(s) and (p[j] == s[i] or p[j] == '.')
    if j+1 < len(p) and p[j+1] == '*':
        return match(i, j+2)                    # use x* ZERO times: skip 'x*'
            or (first and match(i+1, j))        # use x* once more: eat s[i], keep 'x*'
    return first and match(i+1, j+1)            # plain single-char match
```

The `x*` fork — skip the pair, or consume one `s` char and *stay* on `x*` — is the
whole trick. Naively this re-explores overlapping `(i, j)` states exponentially.

## Find the waste

There are only `(m+1)·(n+1)` distinct `(i, j)` suffix pairs. The branching recursion
revisits them constantly (many expansions of `*` land on the same state). Memoize on
`(i, j)` → `O(m·n)`.

## The insight

Bottom-up, `dp[i][j]` = "does `s[i:]` match `p[j:]`?" Fill from the bottom-right
(empty suffixes) back to `(0,0)`, exactly mirroring the recurrence:

```
dp[m][n] = True
if p[j+1] == '*':
    dp[i][j] = dp[i][j+2]                      # zero copies
            or (first and dp[i+1][j])          # one+ copy
else:
    dp[i][j] = first and dp[i+1][j+1]
```

`dp[i][j+2]` is the "star matches nothing" jump over `x*`; `dp[i+1][j]` is "star ate
one `s` char, keep the star." No backtracking — every state is decided once.

## Complexity

- **Time:** `O(m·n)` — one pass over the grid, constant work per cell.
- **Space:** `O(m·n)` for the table (reducible to `O(n)` with two rolling rows).

## Pitfalls

- `*` binds to the character **before** it and always comes as a pair — read
  `p[j], p[j+1]` together; never treat a lone `*` as a normal char.
- **Empty string, non-empty pattern can still match:** `""` matches `"a*"`, `".*"`,
  `"a*b*"`. The base row/`dp[i][j+2]` path handles this — don't early-return false
  just because `s` is empty.
- The `first` guard must check `i < m` *before* indexing `s[i]`.
- Whole-string match: `dp[m][n]` is the only true base; a prefix match is not a match.
- Order matters: for `x*`, evaluate the zero-use skip AND the consume branch — a
  greedy "consume as long as it matches" is wrong (see `"aaa"` vs `"a*a"`).

## Transfer

The reusable idea is *a two-suffix (or two-prefix) grid where one construct branches
into "skip it" OR "consume one and stay."* The nearest sibling is
[Wildcard Matching / 44](https://leetcode.com/problems/wildcard-matching/) (`*`
matches any run of *any* characters — a simpler branch). It also shares the
two-string grid skeleton with [Edit Distance / 72](../0072-edit-distance/) and
[Distinct Subsequences / 115](../0115-distinct-subsequences/).
