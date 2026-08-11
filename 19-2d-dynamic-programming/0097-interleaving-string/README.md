# 97. Interleaving String

**Pattern:** 2-D dynamic programming (grid over two string prefixes)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/interleaving-string/

## The problem in plain words

You have three strings `s1`, `s2`, `s3`. Can you build `s3` by shuffling `s1` and
`s2` together, like riffling two decks of cards? Each string's characters must stay
in their original order, but you may switch back and forth between the two sources
however you like. Return true if some such shuffle produces exactly `s3`.

## Why this matters

The deep operation is *deciding whether one sequence is a valid merge of two, when
at every step you face a fork with no obvious right choice.* The greedy instinct —
"take from whichever string matches the next character" — fails, because sometimes
both match and only one leads to a full solution. That "a local match can be a
trap" quality is what forces DP: you can't commit, so you remember which
`(prefix-of-s1, prefix-of-s2)` positions are reachable.

This exact merge-validation appears in real systems. Reconstructing whether a
combined event log could have come from interleaving two ordered producers is this
problem. Verifying that a merged data stream preserves the per-source order (as in
CRDT/merge reasoning, or checking a k-way merge kept each input monotonic) is the
same check. Parsing a format built by shuffling two ordered token streams reduces to
it too.

What the good solution buys is `O(m·n)` time instead of the `2^(m+n)` blind
enumeration of every possible interleaving, and — rolled — `O(n)` memory.

## Start from the obvious

To match the next character of `s3`, take it from `s1` or from `s2`, whichever
matches, and recurse. Track how much of each we've used with `(i, j)`:

```
def solve(i, j):                 # used s1[:i] and s2[:j]
    if i == m and j == n: return True
    k = i + j                    # so we've filled s3[:k]
    return (i < m and s1[i] == s3[k] and solve(i+1, j)) \
        or (j < n and s2[j] == s3[k] and solve(i,   j+1))
```

The key simplification: there is **no third pointer**. Because every s3 character
comes from s1 or s2, once you've used `i` of one and `j` of the other you've
necessarily produced `s3[:i+j]`. So `k = i + j` is derived — two dimensions, not
three. Without memoization it's exponential (each fork doubles).

## Find the waste

There are only `(m+1)·(n+1)` distinct `(i, j)` states, but the recursion revisits
them along many interleaving orders. Cache on `(i, j)` → `O(m·n)`.

## The insight

Bottom-up, `dp[i][j]` = "can `s1[:i]` and `s2[:j]` interleave into `s3[:i+j]`?"

```
dp[i][j] = (dp[i-1][j] and s1[i-1] == s3[i+j-1])   # last char came from s1
        or (dp[i][j-1] and s2[j-1] == s3[i+j-1])   # last char came from s2
```

Base: `dp[0][0] = True`; the first row/column handle "used only s2" / "only s1". A
cell depends only on the cell above and the cell to the left, so sweeping row by row
we can keep just **one row**: the "from-s1" term reads the same column in the old row
(`dp[j]`), the "from-s2" term reads the just-updated `dp[j-1]`.

## Complexity

- **Time:** `O(m·n)` — fill each grid cell once.
- **Space:** `O(n)` rolled (`O(m·n)` for the full grid). Only the previous row is
  needed.

## Pitfalls

- **The length gate.** If `len(s1) + len(s2) != len(s3)`, it's immediately false —
  check first, or the indexing breaks.
- Being greedy: when `s1[i]` and `s2[j]` both equal `s3[k]`, you must consider both
  branches, not pick one.
- Off-by-one in the 1-D roll: within the new row, `from_s2` reads the *updated*
  `dp[j-1]` (current row) while `from_s1` reads the *old* `dp[j]` (previous row);
  overwrite in place carefully.
- Empty-string cases (`""`,`""`,`""` is true) must fall out of the base row/column.

## Transfer

The reusable idea is *a grid indexed by two prefixes, where a valid extension asks
"did the last piece come from string A or string B?"* Siblings:
[Edit Distance / 72](../0072-edit-distance/) and
[Distinct Subsequences / 115](../0115-distinct-subsequences/) share the
two-prefix-grid skeleton; [Longest Common Subsequence / 1143](https://leetcode.com/problems/longest-common-subsequence/)
is the same table shape with a different cell rule.
