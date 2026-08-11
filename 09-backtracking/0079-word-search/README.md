# 79. Word Search

**Pattern:** Backtracking on a grid (DFS with in-place visited marking)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/word-search/

## The problem in plain words

You have a grid of letters. Can you spell a given word by starting on some cell
and stepping to a neighbor (up, down, left, right) for each next letter? You may
not step on the same cell twice within one spelling.

## Why this matters

Stripped of the letters, this is: *does a path exist through a graph that matches a required sequence and never reuses a node?* The fundamental operation is a depth-first search that tries a step, marks where it's been so the current path can't loop, and un-marks on the way back so other paths stay free.

That "explore, mark, backtrack" loop is everywhere something searches a space of paths or configurations. Maze and route solvers walk a grid this way. Compilers and constraint solvers backtrack through partial assignments, undoing a choice when it leads to a dead end. Game engines search move sequences (and prune the ones that can't win). Circuit routers and puzzle solvers (Sudoku, crosswords) place a value, recurse, and retract it if it fails.

What you're solving for is memory and cleanliness: the in-place mark-and-restore means you carry only the current path, not a separate visited copy per branch, and the board is left untouched for the next search. You avoid re-scanning the whole space and you never pay for state you'd have to reset by hand.

## Start from the obvious

Spelling the word is walking a path where cell 0 is `word[0]`, cell 1 is a
neighbor equal to `word[1]`, and so on. So try each cell as a start, and from
there walk to whichever neighbor matches the next letter:

```
for each cell (r, c):
    if dfs(r, c, index=0): return True

dfs(r, c, k):
    if k == len(word): return True          # matched everything
    if off-grid or board[r][c] != word[k]: return False
    for each neighbor: if dfs(neighbor, k+1): return True
```

This is correct in spirit but has a hole: nothing stops the walk from stepping
back onto a cell it already used, so `"ABCB"` could bounce between two cells and
falsely succeed.

## Find the waste / the insight

We need "which cells does the *current path* already use?" A separate visited set
works, but there's a cheaper move: the board itself can remember. Before
recursing into a cell, overwrite it with a sentinel like `'#'` — no real letter
equals `'#'`, so any branch that wanders back hits the mismatch check and dies.
The moment the recursion returns, put the real letter back.

That restore is the whole point of backtracking: the mark is temporary, scoped to
exactly the path currently being explored. Once we back out, the cell is free
again for other paths and other starting cells — the board ends up untouched.

## Complexity

- **Time:** `O(rows · cols · 4^L)` where `L = len(word)`. Every cell is a
  potential start (`rows · cols`), and from each the search branches up to 4 ways
  per letter for `L` letters. In practice the letter-match check prunes almost
  every branch immediately, so it's far faster than the bound suggests.
- **Space:** `O(L)` for the recursion stack (the path depth). The in-place
  marking means no extra visited grid.

## Pitfalls

- Forgetting to restore the cell after recursing — you'd permanently blank out
  cells and break later searches (and corrupt the caller's board).
- Reusing a cell in one path — the visited mark (or a set) is not optional; a
  naive DFS gives wrong answers on words like `"ABCB"`.
- Checking bounds/mismatch *after* indexing instead of before — guard `r`, `c`,
  and `board[r][c] != word[k]` at the top of `dfs` so you never index off-grid.
- Empty word: by convention it "exists" (return True) before touching the grid.

## Transfer

In-place marking + DFS + restore-on-return is the grid-backtracking template:
[Number of Islands / 200](../../11-graphs/0200-number-of-islands/) (flood-fill
uses the same visited-in-place idea), [Word Search II / 212](../0212-word-search-ii/)
(same walk, but drive many words at once with a Trie), and any "find a path/shape
in a matrix" problem. Whenever a search must avoid revisiting cells on the
current path, mark before recursing and unmark after.
