# 72. Edit Distance

**Pattern:** 2-D dynamic programming (two-prefix cost grid — Levenshtein)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/edit-distance/

## The problem in plain words

Given two words, find the smallest number of one-character edits that turn the first
into the second. An edit is: insert a character, delete a character, or replace one
character with another. Return that minimum count (the *Levenshtein distance*).

## Why this matters

The underlying operation is *measuring how far apart two sequences are, allowing for
insertions and gaps, not just position-by-position mismatch.* A naive comparison
breaks the moment lengths differ or characters shift by one; edit distance is the
principled answer to "how similar are these, really?" It's the canonical example of
DP over two prefixes, and the recurrence — match for free, else pay one and take the
best of three moves — is worth knowing cold.

It runs a lot of software you use daily. Spell-checkers and "did you mean…?" rank
candidates by edit distance. `git diff`, `diff`, and merge tools compute edits (a
close cousin, with only insert/delete) to show minimal changes. DNA/protein
alignment in bioinformatics is a weighted edit distance. Fuzzy search, deduplicating
near-identical records, and OCR post-correction all score matches this way.

What the good solution buys is `O(m·n)` time instead of the exponential blow-up of
trying every sequence of edits, and — rolled to one row — `O(min(m,n))` memory, so
even long strings compare cheaply.

## Start from the obvious

Compare the two words from the end. State `(i, j)` = edits to turn `word1[:i]` into
`word2[:j]`. If the last characters match, they cost nothing; otherwise pay 1 and
try the three edits, each shrinking the problem:

```
def dist(i, j):
    if i == 0: return j                 # insert j chars
    if j == 0: return i                 # delete i chars
    if w1[i-1] == w2[j-1]: return dist(i-1, j-1)
    return 1 + min(dist(i-1, j-1),      # replace
                   dist(i-1, j),        # delete from w1
                   dist(i,   j-1))      # insert into w1
```

Each call spawns up to three, so raw recursion is exponential.

## Find the waste

There are only `(m+1)·(n+1)` distinct `(i, j)` states, but the three-way branching
revisits them enormously. Memoize on `(i, j)` → `O(m·n)`. This is the standard
Wagner–Fischer table.

## The insight

Bottom-up, `dp[i][j]` fills a grid. Each cell reads only three neighbours — the cell
above (`delete`), the cell left (`insert`), and the diagonal (`replace`/`match`):

```
dp[i][j] = dp[i-1][j-1]                     if w1[i-1] == w2[j-1]
         = 1 + min(dp[i-1][j-1],            # replace
                   dp[i-1][j],              # delete
                   dp[i][j-1])              # insert   otherwise
```

Because a cell needs only the previous row plus the current row's left neighbour, keep
**one row** and stash the diagonal in a scalar `diag` before overwriting it — that
old value is the `dp[i-1][j-1]` the next column's replace needs.

## Complexity

- **Time:** `O(m·n)` — fill each cell once, constant work.
- **Space:** `O(n)` rolled (`O(m·n)` full grid); iterate over the shorter word to
  make it `O(min(m,n))`.

## Pitfalls

- **Base rows/columns.** Turning `""` into a length-`j` string costs `j` inserts;
  the reverse costs `i` deletes. Initialize `dp[0][j]=j` and `dp[i][0]=i` or the
  recurrence has no floor.
- In the 1-D roll, you need three values but only two survive per cell — forgetting
  to save the *pre-overwrite* diagonal is the classic bug.
- On a character **match** the cost is the diagonal *unchanged* — don't add 1.
- Insert vs delete are symmetric here (both cost 1); if the problem weights them
  differently, keep the branches separate.

## Transfer

The reusable skeleton is *a two-prefix grid whose cell = "free on match, else 1 +
best of {replace-diagonal, delete-up, insert-left}."* Siblings:
[Longest Common Subsequence / 1143](https://leetcode.com/problems/longest-common-subsequence/)
(same grid, max instead of min, only diagonal-on-match),
[Delete Operation for Two Strings / 583](https://leetcode.com/problems/delete-operation-for-two-strings/)
(edit distance with no replace),
[Distinct Subsequences / 115](../0115-distinct-subsequences/) and
[Interleaving String / 97](../0097-interleaving-string/) share the grid shape.
