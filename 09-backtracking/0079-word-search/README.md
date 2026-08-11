# 79. Word Search

**Pattern:** Backtracking on a grid (walk, mark the cell, restore on the way back)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/word-search/

## The problem in plain words

You have a grid of letters. Can you spell a given word by starting on some cell and
stepping to a neighbor (up, down, left, right) for each next letter? You may not
step on the same cell twice within one spelling.

```diagram
   board:            spell "ABCCED":
     A  B  C  E        A -> B -> C -> C -> E -> D   (path bends around)
     S  F  C  S        (0,0)(0,1)(0,2)(1,2)(2,2)(2,1)
     A  D  E  E        -> True
```

## Why this matters

Stripped of the letters, this is: *does a path exist through a grid that matches a
required sequence and never reuses a cell?* The one reusable move is a depth-first
search — try a step, mark where you've been so the current path can't loop, and
un-mark on the way back so other paths stay free.

That "explore, mark, backtrack" loop is everywhere something searches a space of
paths. Maze and route solvers walk a grid this way. Constraint solvers back out of a
partial assignment when it dead-ends. Sudoku and crossword solvers place a value,
recurse, and retract it if it fails.

What you're solving for is memory and cleanliness. The in-place mark-and-restore
means you carry only the current path, not a separate "visited" copy per branch, and
the board is left untouched for the next search.

## Start from the obvious

Spelling the word is walking a path: cell 0 is `word[0]`, cell 1 is a neighbor equal
to `word[1]`, and so on. So try each cell as a start, and from there walk to whichever
neighbor matches the next letter.

```diagram
   for each cell (r, c): if dfs(r, c, k=0): return True

   dfs(r, c, k):
     if k == len(word): return True           # matched everything
     if off-grid or board[r][c] != word[k]: return False
     for each neighbor: if dfs(neighbor, k+1): return True
```

Correct in spirit, but there's a hole: nothing stops the walk from stepping back
onto a cell it already used, so `"ABCB"` could bounce between two cells and falsely
succeed.

## Find the waste / the insight

We need "which cells does the *current path* already use?" A separate visited set
works, but there's a cheaper move: the board itself can remember. Before recursing
into a cell, overwrite it with a sentinel like `'#'` — no real letter equals `'#'`,
so any branch that wanders back hits the mismatch check and dies. The instant the
recursion returns, put the real letter back.

```diagram
   spelling "ABCB" from (0,0):     board while exploring (# = in current path)
     A  B  ...        step A(0,0):   #  B  ...
     ...              step B(0,1):   #  #  ...
                      now need 'C'; try to step back to A(0,0)?
                      board[0][0] is '#', not 'C' -> mismatch -> that branch dies
                      (this is exactly why "ABCB" can't cheat by reusing a cell)

   on return, restore each cell:
     #  #   ->   A  #   ->   A  B     board ends up whole again
```

That restore is the whole point of backtracking: the mark is temporary, scoped to
exactly the path being explored. Once we back out, the cell is free again for other
paths and other starting cells — the board ends up untouched.

## Complexity

- **Time: about rows · cols · 4^L** where `L = len(word)`. Every cell is a possible
  start, and from each the search branches up to 4 ways per letter for L letters. In
  practice the letter-match check kills almost every branch immediately, so it runs
  far faster than that bound.
- **Extra memory: about L** for the recursion depth (the path). The in-place marking
  means no separate visited grid.

## Pitfalls

- Forgetting to restore the cell after recursing — you'd permanently blank out cells
  and break later searches (and corrupt the caller's board).
- Reusing a cell in one path — the visited mark (or a set) is not optional; a naive
  DFS gives wrong answers on words like `"ABCB"`.
- Checking bounds and mismatch *after* indexing instead of before — guard `r`, `c`,
  and `board[r][c] != word[k]` at the top of `dfs` so you never index off-grid.
- Empty word: by convention it "exists" (return True) before touching the grid.

## Transfer

Mark-in-place + DFS + restore-on-return is the grid-backtracking template:
[Number of Islands / 200](../../12-graphs/0200-number-of-islands/) (flood-fill uses
the same visited-in-place idea) and
[Word Search II / 212](../../10-tries/0212-word-search-ii/) (same walk, but drive
many words at once with a Trie). Whenever a search must avoid revisiting cells on the
current path, mark before recursing and unmark after.
