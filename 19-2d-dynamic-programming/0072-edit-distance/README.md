# 72. Edit Distance

**Pattern:** 2-D dynamic programming (two-prefix cost grid — Levenshtein)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/edit-distance/

## The problem in plain words

You have two words. You may change one into the other using three moves: insert a
letter, delete a letter, or replace a letter with another. Each move costs one.
Give back the smallest number of moves that turns `word1` into `word2`.

```diagram
   word1 = "horse"      word2 = "ros"

   horse -> rorse   (replace h with r)
   rorse -> rose    (delete r)
   rose  -> ros     (delete e)

   3 moves.  Can we do it in fewer?  No.
```

## Why this matters

This is the distance between two pieces of text: how far apart are they, measured
in edits. That number is the quiet engine behind spell-check ("did you mean…?"),
`git diff`, DNA comparison, and the "fuzzy match" in a search box. Any time a
system asks *how similar are these two strings, really?*, it is computing some
flavor of this.

The reusable idea is bigger than strings. You have two things to line up, you look
at their last pieces, and the answer to the whole problem is built from the answer
to slightly smaller versions of the same problem. Solve the small overlaps once,
write them down, and the big answer assembles itself.

## Start from the obvious

Look at the last letter of each word. Two cases:

- They match. Then that letter is free — line them up and the cost is whatever it
  takes to fix the two shorter prefixes behind them.
- They differ. Then you must pay one move, and you get to pick which:
  - **replace** the last letter of `word1` — now both shrink by one.
  - **delete** the last letter of `word1` — only `word1` shrinks.
  - **insert** `word2`'s last letter onto `word1` — only `word2` shrinks.

So the cost of `(word1, word2)` depends on the cost of three slightly shorter
pairs. Write that as recursion and it works — but the same shorter pairs get asked
for again and again down different branches, so the plain recursion balloons.

## The insight

Index the smaller problems by *how much of each word is left to reconcile*: let
`dp[i][j]` be the cost to turn the first `i` letters of `word1` into the first `j`
letters of `word2`. That is a grid — one axis per word — and every cell reads three
neighbors that are already filled.

```diagram
   dp[i][j] = edits( word1[:i] -> word2[:j] )

              j:  ""  r   o   s
        i     +----+---+---+---+
        ""    | 0  | 1 | 2 | 3 |   turn "" into "ros": 3 inserts
        h     | 1  |   |   |   |
        o     | 2  |   |   |   |
        r     | 3  |   |   |   |
        s     | 4  |   |   |   |
        e     | 5  |   |   |   |
              +----+---+---+---+
   row 0 / col 0 are free: turning something into "" is all deletes,
   and turning "" into something is all inserts.
```

Now watch one cell fill. Each interior cell pulls from three already-known
neighbors — the cell above (delete), the cell to the left (insert), and the cell
on the diagonal (replace, or free if the letters match):

```diagram
   filling dp[i][j], comparing word1[i-1] vs word2[j-1]

        diag        up
      dp[i-1][j-1]  dp[i-1][j]
              \      |
               \     v
       dp[i][j-1] -> dp[i][j]
        left

   letters match  ->  dp[i][j] = diag              (free ride)
   letters differ ->  dp[i][j] = 1 + min(diag, up, left)
                                     replace delete insert
```

Fill the grid row by row, left to right, and the bottom-right cell is the answer.
Because each cell only needs the row above and the cell just written, you can keep
a single row plus one stashed diagonal value and drop the memory to one line — that
is the rolled version in `solution.py`.

## Complexity

- **Time: about m × n steps** (m and n the two word lengths). One cheap decision
  per grid cell. Doubling both words roughly quadruples the work.
- **Extra memory: about n** in the rolled version — one row over the second word.
  The full-grid version uses about m × n.

## Pitfalls

- Getting the three directions crossed. Fix them once: diagonal = replace,
  up = delete from `word1`, left = insert into `word1`. Draw it.
- Forgetting the free row and column. Turning `""` into a length-`j` word costs
  `j` inserts; that seeds row 0. The empty-vs-empty corner is 0.
- On a match, don't take `1 + min(...)`. The matched letters cost nothing — copy
  the diagonal straight across.

## Transfer

The reusable skeleton is *a two-prefix grid whose cell = "free on match, else 1 +
best of {replace-diagonal, delete-up, insert-left}."* Siblings:
[Longest Common Subsequence / 1143](https://leetcode.com/problems/longest-common-subsequence/)
(same grid, max instead of min, only diagonal-on-match),
[Delete Operation for Two Strings / 583](https://leetcode.com/problems/delete-operation-for-two-strings/)
(edit distance with no replace),
[Distinct Subsequences / 115](../0115-distinct-subsequences/) and
[Interleaving String / 97](../0097-interleaving-string/) share the grid shape.
