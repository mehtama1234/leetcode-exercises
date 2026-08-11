# 51. N-Queens

**Pattern:** Backtracking with constraint propagation (place, check, prune, undo)
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/n-queens/

## The problem in plain words

Put `n` queens on an `n×n` chessboard so that no two can attack each other. A queen
attacks along its row, its column, and both diagonals. Return every valid board,
drawn with `Q` for a queen and `.` for an empty square. For `n=4` there are exactly
two solutions; for `n=8`, ninety-two.

## Why this matters

This is the archetypal **constraint-satisfaction search**: fill a set of slots with
values so a web of "these two can't coexist" rules all hold. N-Queens is the
teaching example precisely because the constraints are simple to state (same row /
column / diagonal) yet dense enough that blind enumeration is hopeless — `8×8`
placements of 8 queens is over four billion arrangements, but only 92 are legal.

That shape is the honest core of real solvers. Sudoku, graph coloring, exam and
shift scheduling (no person in two places, no room double-booked), register
allocation in a compiler (interfering values can't share a register), and hardware
placement all say "assign values so no pair of conflicting assignments coexists."

What good backtracking buys is **pruning by constraint propagation**: you check a
placement's legality *before* committing and abandon a whole subtree the instant a
partial board is already doomed. That's the difference between exploring billions of
dead boards and thousands of live ones — the constraint check turns an intractable
enumeration into a fast search.

## Start from the obvious

The definition suggests: try every way to place `n` queens, keep the boards with no
attacks.

```
for every choice of n squares:
    if no two queens attack: record the board
```

Correct and completely hopeless — `C(64,8)` boards for `n=8`. But two facts shrink
it immediately. First, **no two queens can share a row**, so with `n` queens on `n`
rows there's exactly one per row: a solution is just "which column in each row?",
cutting the space to `n^n`. Second, most partial boards are dead early — the moment
two placed queens conflict, every completion of that board is wasted.

## The insight

Place queens **one row at a time**, and before committing a queen to `(row, col)`,
check it against everything already placed. The clever part is making that check
`O(1)` with three sets:

- **Column:** `col in cols` — a column is taken or it isn't.
- **`\` diagonal:** two cells lie on the same top-left-to-bottom-right diagonal iff
  `row - col` is equal. Track the set of used `row - col`.
- **`/` diagonal:** same for the other diagonal iff `row + col` is equal. Track used
  `row + col`.

```
backtrack(row):
    if row == n: record the board; return          # all rows filled -> a solution
    for col in 0..n-1:
        if col in cols or (row-col) in diag or (row+col) in anti_diag:
            continue                                # attacked -> prune
        add col, row-col, row+col to the sets       # choose
        backtrack(row+1)                            # explore
        remove them again                           # un-choose
```

This is the full backtracking template with a real prune. **Choose** commits the
queen and marks its three lines of attack; **explore** moves to the next row;
**un-choose** retracts the queen and *all three* marks so the sibling column sees a
clean board. Reaching `row == n` means all queens are placed with no conflict — a
solution.

## Complexity

- **Time:** exponential but hard to state tightly — bounded above by `O(n!)` (at
  most `n` legal columns in row 0, fewer below as diagonals fill), and far smaller
  in practice because the constraint prune kills most branches high in the tree.
  Building each solution board costs `O(n^2)`.
- **Space:** `O(n)` for the recursion, the three sets, and the column placement
  array. The output holds the solution boards.

## Pitfalls

- **The diagonal identities.** `\` is `row - col` constant, `/` is `row + col`
  constant. Swap them or use `+`/`-` wrong and boards leak diagonal attacks.
- **Incomplete undo.** You must remove the queen from *all three* sets on the way
  back up; forgetting the diagonals is a classic silent bug that drops solutions.
- **Rebuilding an `O(n^2)` attack grid every check** instead of the `O(1)` set
  lookups — correct but needlessly slow.
- Assuming a solution always exists — `n=2` and `n=3` have none; return an empty
  list, don't loop forever.

## Transfer

The move — *assign slots in order, check each assignment against the constraints
before recursing, undo on the way back* — is the general constraint-satisfaction
solver. It's exactly how you'd solve Sudoku (check row/column/box before writing a
digit) or graph coloring (check neighbors before assigning a color). Whenever the
task is "assign values so no pair of conflicting assignments coexists," this
place-check-prune-undo skeleton is the tool.
