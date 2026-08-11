# 97. Interleaving String

**Pattern:** 2-D dynamic programming (grid over two string prefixes)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/interleaving-string/

## The problem in plain words

You have three strings: `s1`, `s2`, and `s3`. You want to know if `s3` can be built
by shuffling `s1` and `s2` together — drawing letters one at a time from either one,
never reordering the letters inside `s1` or inside `s2`. Think of two decks of
cards riffled into one pile: each deck keeps its order, but they interleave.

```diagram
   s1 = "aab"    s2 = "dbbca"    s3 = "aadbbcbcac"

   draw:  a a        b   b c   c
   from:  1 1  d b b   c   b   a c
          ^^^  ^^^^^   ^   ^   ^^^
          s1   s2     s1   ...    -> "aadbbcbcac"  works
```

## Why this matters

The real move here is recognizing that a third pointer you thought you needed is
already decided by the other two. If you've used `i` letters of `s1` and `j` letters
of `s2`, then you've placed exactly `i + j` letters of `s3` — there's no freedom
left in where you are in `s3`. Spotting a variable that's forced by the others is
what collapses a seemingly 3-D search into a plain 2-D grid.

That's the same instinct that keeps merge steps, log-interleaving, and stream-
merging honest: two sources feed one output, order preserved on each side, and the
output position is bookkeeping, not a real choice.

## Start from the obvious

At each step you're at some position in `s3`, and the next `s3` letter must come
from either the front of what's left in `s1` or the front of what's left in `s2`.
So branch: try taking it from `s1`, try taking it from `s2`. If a source's next
letter doesn't match, that branch is dead.

```diagram
   need s3[k].  take from s1 if s1[i] == s3[k];  take from s2 if s2[j] == s3[k].

              (i, j)
              /     \
       s1[i]==s3   s2[j]==s3
          |            |
       (i+1, j)     (i, j+1)
```

This explores a tree, and different paths land on the same `(i, j)` again and again
— you re-solve "from here, does the rest interleave?" many times. That repetition
is the waste.

## The insight

Let `dp[i][j]` mean: *can the first `i` letters of `s1` and first `j` letters of
`s2` interleave to form the first `i + j` letters of `s3`?* Only two dimensions,
because the `s3` position is `i + j`.

```diagram
   s1 = "aab" (down)   s2 = "dbbca" (across)   target = s3

            j:  ""   d    b    b    c    a
       i    +----+----+----+----+----+----+
       ""   | T  |    |    |    |    |    |
       a    |    |    |    |    |    |    |
       a    |    |    |    |    |    |    |
       b    |    |    |    |    |    |    |
            +----+----+----+----+----+----+
   dp[""][""] = True: empty + empty makes empty.
```

Each cell asks a yes/no question and reads two neighbors — the cell above (last
letter came from `s1`) and the cell to the left (last letter came from `s2`):

```diagram
   filling dp[i][j], target letter is s3[i+j-1]

        up = dp[i-1][j]           left = dp[i][j-1]
        "came from s1"            "came from s2"
             |                         |
             v                         v
        (up  AND s1[i-1]==s3[i+j-1])  OR  (left AND s2[j-1]==s3[i+j-1])
                                  = dp[i][j]

   True can arrive from EITHER neighbor.  One valid path is enough.
```

Fill row by row; the bottom-right cell is the answer. Since a row only needs the
row above it, you can roll the grid down to a single row — that's the version in
`solution.py`.

One quick gate first: if `len(s1) + len(s2) != len(s3)`, the answer is no before
you start.

## Complexity

- **Time: about m × n steps** (m, n the lengths of `s1`, `s2`). One yes/no check
  per grid cell. Doubling both inputs roughly quadruples the work.
- **Extra memory: about n** in the rolled version — one row over `s2`. The full
  grid uses about m × n.

## Pitfalls

- Skipping the length gate. If `m + n != len(s3)`, no interleaving can exist.
- A greedy "take from whichever matches" fails: sometimes both match and you must
  keep both branches open. The grid keeps every reachable state, so it's safe.
- Getting the `s3` index wrong. When filling `dp[i][j]`, the letter under scrutiny
  is `s3[i+j-1]`, not `s3[i]` or `s3[j]`.

## Transfer

The reusable idea is *a grid indexed by two prefixes, where a valid extension asks
"did the last piece come from string A or string B?"* Siblings:
[Edit Distance / 72](../0072-edit-distance/) and
[Distinct Subsequences / 115](../0115-distinct-subsequences/) share the
two-prefix-grid skeleton; [Longest Common Subsequence / 1143](https://leetcode.com/problems/longest-common-subsequence/)
is the same table shape with a different cell rule.
