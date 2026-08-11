"""51. N-Queens — https://leetcode.com/problems/n-queens/

Place n queens on an n x n board so that no two attack each other (no shared row,
column, or diagonal). Return every valid board as a list of strings using 'Q' and
'.'.

We place one queen per row and, before committing, check the column and both
diagonals in O(1) using three sets. An attack means prune — don't recurse.
"""
from typing import List


def solve_n_queens(n: int) -> List[List[str]]:
    """Backtracking row by row with O(1) attack checks. Exponential but pruned hard.

    One queen per row removes row conflicts by construction, so a placement is just
    a column choice per row. Three sets track what's already threatened:
      - cols:      columns taken
      - diag:      cells share a '\\' diagonal iff (row - col) is equal
      - anti_diag: cells share a '/' diagonal iff (row + col) is equal
    Before placing at (row, col) we check all three in O(1); a conflict prunes the
    branch instantly. choose = add to the three sets + record the column; explore =
    recurse to the next row; un-choose = remove from the sets.
    """
    result: List[List[str]] = []
    cols: set[int] = set()
    diag: set[int] = set()          # row - col
    anti_diag: set[int] = set()     # row + col
    placement: List[int] = []       # placement[row] = column of the queen in that row

    def build_board() -> List[str]:
        board = []
        for col in placement:
            board.append("." * col + "Q" + "." * (n - col - 1))
        return board

    def backtrack(row: int) -> None:
        if row == n:
            result.append(build_board())
            return
        for col in range(n):
            if col in cols or (row - col) in diag or (row + col) in anti_diag:
                continue                # under attack -> prune this column
            cols.add(col)               # choose
            diag.add(row - col)
            anti_diag.add(row + col)
            placement.append(col)
            backtrack(row + 1)          # explore next row
            placement.pop()             # un-choose
            cols.remove(col)
            diag.remove(row - col)
            anti_diag.remove(row + col)

    backtrack(0)
    return result


def _key(boards: List[List[str]]) -> set:
    """Order-independent key: a set of boards, each board a tuple of its rows."""
    return {tuple(b) for b in boards}


def _valid(board: List[str]) -> bool:
    """Independent re-check that a board really has no two queens attacking."""
    n = len(board)
    queens = [(r, c) for r in range(n) for c in range(n) if board[r][c] == "Q"]
    if len(queens) != n:
        return False
    for i in range(len(queens)):
        for j in range(i + 1, len(queens)):
            (r1, c1), (r2, c2) = queens[i], queens[j]
            if r1 == r2 or c1 == c2 or abs(r1 - r2) == abs(c1 - c2):
                return False
    return True


def _test() -> None:
    # Known solution counts (OEIS A000170).
    counts = {1: 1, 2: 0, 3: 0, 4: 2, 5: 10, 6: 4, 7: 40, 8: 92}
    for n, expected_count in counts.items():
        boards = solve_n_queens(n)
        assert len(boards) == expected_count, (n, len(boards))
        # every returned board must independently pass the no-attack check
        assert all(_valid(b) for b in boards), n
        # no duplicate boards
        assert len(_key(boards)) == len(boards), (n, "duplicate board")

    # Check the exact set for n = 4.
    n4 = solve_n_queens(4)
    assert _key(n4) == _key([
        [".Q..", "...Q", "Q...", "..Q."],
        ["..Q.", "Q...", "...Q", ".Q.."],
    ]), n4
    print("solve_n_queens: all cases passed")


if __name__ == "__main__":
    _test()
