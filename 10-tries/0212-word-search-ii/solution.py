"""212. Word Search II — https://leetcode.com/problems/word-search-ii/

Given a grid of letters and a list of words, return every word that can be spelled
by walking to adjacent (up/down/left/right) cells without reusing a cell.
"""
from typing import Dict, List, Optional


class TrieNode:
    """A character position in the trie of target words.

    `word` holds the full string at the node where a word ends (and doubles as
    the end-of-word marker). Storing the whole word here means that when the DFS
    reaches an end node it can collect the answer directly, with no path tracking.
    """

    def __init__(self) -> None:
        self.children: Dict[str, "TrieNode"] = {}
        self.word: Optional[str] = None  # the complete word, only at end nodes


def find_words_brute(board: List[List[str]], words: List[str]) -> List[str]:
    """For each word, DFS the whole board looking for it. The honest baseline.

    Straightforward but wasteful: two words like "oath" and "oat" each launch
    their own full board search, re-treading the shared "oat" prefix from every
    starting cell. With `w` words this is `w` independent searches.
    """
    rows, cols = len(board), len(board[0])

    def exists(word: str) -> bool:
        def dfs(r: int, c: int, i: int) -> bool:
            if i == len(word):
                return True
            if r < 0 or r >= rows or c < 0 or c >= cols or board[r][c] != word[i]:
                return False
            saved, board[r][c] = board[r][c], "#"  # mark visited
            found = (
                dfs(r + 1, c, i + 1)
                or dfs(r - 1, c, i + 1)
                or dfs(r, c + 1, i + 1)
                or dfs(r, c - 1, i + 1)
            )
            board[r][c] = saved
            return found

        return any(dfs(r, c, 0) for r in range(rows) for c in range(cols))

    return [w for w in words if exists(w)]


class Solution:
    """Optimal: one board DFS guided by a trie of *all* the words at once.

    The brute force restarts for every word and re-walks shared prefixes. Put
    the words into a trie and walk the *board* instead: from each cell, descend
    the trie as long as the current letter is a valid next character. All words
    sharing a prefix are explored together in a single pass, and the instant the
    grid path leaves the trie we prune. When a trie node carries a full word,
    we've found it.
    """

    def findWords(self, board: List[List[str]], words: List[str]) -> List[str]:
        root = self._build_trie(words)
        rows, cols = len(board), len(board[0])
        found: List[str] = []

        def dfs(r: int, c: int, node: TrieNode) -> None:
            ch = board[r][c]
            nxt = node.children.get(ch)
            if nxt is None:
                return  # this grid letter can't extend any remaining word -> prune

            if nxt.word is not None:
                found.append(nxt.word)
                nxt.word = None  # de-duplicate: collect each word only once

            board[r][c] = "#"  # mark visited so this path can't reuse the cell
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != "#":
                    dfs(nr, nc, nxt)
            board[r][c] = ch  # restore for other starting paths

        for r in range(rows):
            for c in range(cols):
                dfs(r, c, root)
        return found

    @staticmethod
    def _build_trie(words: List[str]) -> TrieNode:
        root = TrieNode()
        for word in words:
            node = root
            for ch in word:
                if ch not in node.children:
                    node.children[ch] = TrieNode()
                node = node.children[ch]
            node.word = word
        return root


def _test() -> None:
    sol = Solution()

    # Official LeetCode example 1
    board1 = [
        ["o", "a", "a", "n"],
        ["e", "t", "a", "e"],
        ["i", "h", "k", "r"],
        ["i", "f", "l", "v"],
    ]
    words1 = ["oath", "pea", "eat", "rain"]
    assert sorted(sol.findWords(board1, words1)) == ["eat", "oath"]

    # Official LeetCode example 2
    board2 = [["a", "b"], ["c", "d"]]
    words2 = ["abcb"]
    assert sol.findWords(board2, words2) == []  # would need to reuse 'b'

    # Edge cases
    board3 = [["a"]]
    assert sorted(sol.findWords(board3, ["a"])) == ["a"]      # single cell word
    assert sol.findWords(board3, ["b"]) == []                  # letter not present

    # Overlapping-prefix words are all found in one pass, each once
    board4 = [
        ["o", "a", "t"],
        ["x", "x", "h"],
        ["x", "x", "x"],
    ]
    got = sorted(sol.findWords(board4, ["oat", "oath", "oat"]))
    assert got == ["oat", "oath"], got  # duplicate "oat" collected only once

    # Optimal must agree with the brute force on the main example
    assert sorted(sol.findWords(board1, words1)) == sorted(
        find_words_brute(board1, words1)
    )

    print("word_search_ii: all cases passed")


if __name__ == "__main__":
    _test()
