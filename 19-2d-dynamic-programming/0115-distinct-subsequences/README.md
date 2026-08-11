# 115. Distinct Subsequences

**Pattern:** 2-D dynamic programming (two-prefix counting grid)
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/distinct-subsequences/

## The problem in plain words

You have a big string `s` and a small string `t`. Count how many different ways you
can cross out some letters of `s` (keeping the rest in order) so that what's left
reads exactly `t`. Two ways count as different if they cross out different letters,
even if the surviving text is the same.

```diagram
   s = "rabbbit"    t = "rabbit"

   pick which 'b's to keep (t needs two b's, s has three):

   ra[bb]bit   ra[b_b]it   ra[_bb]it     -> 3 distinct ways
      keep 1,2    keep 1,3    keep 2,3
```

## Why this matters

The trick is counting alignments, not just deciding yes/no. When you stand on a
letter of `s` that could match, you don't have to commit — you can *use* it here,
or *skip* it and hope a later copy matches instead. Adding up "use" and "skip"
tallies every distinct way separately, without ever listing them.

That "sum over the choices you didn't have to make" move is the heart of counting
problems everywhere: number of paths through a grid, number of ways to make change,
number of parse trees. The shape of the recurrence changes, but the habit — one
choice splits into a sum of sub-counts — carries over.

## Start from the obvious

Walk `s` and `t` together from the front. Look at the current `s` letter:

- It doesn't match the current `t` letter → you have no choice, skip it and move on
  in `s`.
- It matches → you have two choices. **Use** it (advance in both `s` and `t`) or
  **skip** it (advance in `s` only, leave `t` where it is, hoping a later `s` letter
  matches). The total count is the sum of both.

```diagram
   at s-letter c, needing t-letter d:

        c == d ?
        /        \
      no          yes
      |          /    \
     skip     use      skip
      |     (both++)   (s++ only)
   count(skip)  count(use) + count(skip)
```

Written as recursion this is correct, but the same "still need `t[j:]` inside
`s[i:]`" state is reached from many prefixes, so it's re-solved over and over.

## The insight

Let `dp[i][j]` be the number of ways `t[:j]` shows up in `s[:i]`. That's a grid: one
axis per string. The whole top row is 1 — the empty target matches any prefix
exactly one way (cross everything out).

```diagram
   s = "rab..." (down)   t = "rab" (across)

            j:  ""   r    a    b
       i    +----+----+----+----+
       ""   | 1  | 0  | 0  | 0  |   empty t: 1 way; nonempty t in "": 0
       r    | 1  |    |    |    |
       a    | 1  |    |    |    |
       b    | 1  |    |    |    |
            +----+----+----+----+
   left column all 1: empty t is always matchable.
```

Now fill one cell. It always inherits the "skip this `s` letter" count from the cell
directly above. If the letters also match, it *adds* the "use it" count from the
cell up-and-to-the-left (the diagonal):

```diagram
   filling dp[i][j], comparing s[i-1] vs t[j-1]

        diag = dp[i-1][j-1]     up = dp[i-1][j]
        "use s[i-1]"            "skip s[i-1]"
              \                    |
               \                   v
                +-----------> dp[i][j]

   letters differ ->  dp[i][j] = up
   letters match  ->  dp[i][j] = up + diag
```

Sweep the grid; the bottom-right cell is the count. Because a cell only needs the
row above, you can roll it to a single row — scanning `j` from high to low so the
"before this letter" counts stay intact. That's the version in `solution.py`.

## Complexity

- **Time: about m × n steps** (m = len `s`, n = len `t`). One add per grid cell.
  Doubling both roughly quadruples the work.
- **Extra memory: about n** in the rolled version — one row over `t`. The full grid
  uses about m × n.

## Pitfalls

- Seeding the empty-target case wrong. `dp[i][0] = 1` for every `i`: there's exactly
  one way to spell the empty string (delete everything).
- On the rolled 1-D version, sweeping `j` low-to-high double-counts, because
  `dp[j-1]` would already include the current letter. Go high-to-low.
- Overwriting the "skip" count. The new cell must add to the old `dp[j]` (skip), not
  replace it, when the letters don't match.

## Transfer

The reusable move is *a two-prefix grid where each cell = "skip a source character"
plus (on a match) "consume it," and you sum for counts / max for lengths / min for
costs.* Siblings: [Edit Distance / 72](../0072-edit-distance/) (min over the same
grid), [Interleaving String / 97](../0097-interleaving-string/) (boolean over a
two-prefix grid), [Longest Common Subsequence / 1143](https://leetcode.com/problems/longest-common-subsequence/)
(max over it).
