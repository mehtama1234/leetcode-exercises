"""79. Word Search — https://leetcode.com/problems/word-search/

Given a grid of letters and a `word`, decide whether the word can be spelled by
walking from cell to adjacent cell (up/down/left/right). You may not reuse the
same cell twice in one path. Return True/False.
"""
from typing import List


def exist(board: List[List[str]], word: str) -> bool:
    """DFS from every cell, marking visited in place and un-marking on the way out.

    Spelling the word is a path problem: pick a starting cell that matches the
    first letter, then keep stepping to a neighbor that matches the next letter.
    The "can't reuse a cell" rule means the path is a walk with no repeats, so we
    need to remember which cells the CURRENT path already used.

    Two decisions make this efficient and simple:

    1. We try every cell as a possible start. If the word starts here, we recurse
       deeper; if the branch fails, we back out and try the next start.
    2. Instead of a separate visited set, we temporarily overwrite the current
       cell with a sentinel ('#') before recursing and restore its real letter
       right after. This marks the cell as "in use for this path" for free, and
       restoring it on the way out is the backtracking step — it leaves the board
       untouched so other starting cells and branches see the original grid.

    We stop a branch the instant a letter mismatches or we step off the grid, so
    most starts die immediately.
    """
    if not word:
        return True
    rows, cols = len(board), len(board[0])

    def dfs(r: int, c: int, k: int) -> bool:
        if k == len(word):
            return True  # matched every letter
        if r < 0 or r >= rows or c < 0 or c >= cols:
            return False  # walked off the board
        if board[r][c] != word[k]:
            return False  # this cell can't be the k-th letter

        board[r][c] = "#"  # mark as used for the current path
        found = (
            dfs(r + 1, c, k + 1)
            or dfs(r - 1, c, k + 1)
            or dfs(r, c + 1, k + 1)
            or dfs(r, c - 1, k + 1)
        )
        board[r][c] = word[k]  # restore — backtrack so other paths see it whole
        return found

    for r in range(rows):
        for c in range(cols):
            if dfs(r, c, 0):
                return True
    return False


def _test() -> None:
    board1 = [
        ["A", "B", "C", "E"],
        ["S", "F", "C", "S"],
        ["A", "D", "E", "E"],
    ]
    assert exist([row[:] for row in board1], "ABCCED") is True
    assert exist([row[:] for row in board1], "SEE") is True
    assert exist([row[:] for row in board1], "ABCB") is False  # would reuse 'B'

    # single cell
    assert exist([["A"]], "A") is True
    assert exist([["A"]], "B") is False

    # word longer than the whole grid can never fit
    assert exist([["A", "B"]], "ABA") is False

    # snake path that must bend around itself
    board2 = [
        ["C", "A", "A"],
        ["A", "A", "A"],
        ["B", "C", "D"],
    ]
    assert exist([row[:] for row in board2], "AAB") is True

    print("word_search: all cases passed")


if __name__ == "__main__":
    _test()
