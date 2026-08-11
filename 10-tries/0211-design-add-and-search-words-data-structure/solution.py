"""211. Design Add and Search Words Data Structure — https://leetcode.com/problems/design-add-and-search-words-data-structure/

Store words, then search for them where a '.' in the query matches any single
character. Like a trie, but search can branch.
"""
from typing import Dict


class TrieNode:
    """One character position: children by next-char, plus an end-of-word flag."""

    def __init__(self) -> None:
        self.children: Dict[str, "TrieNode"] = {}
        self.is_word: bool = False


class WordDictionary:
    """A trie whose search understands the '.' wildcard.

    `addWord` is an ordinary trie insert. The interesting part is `search`: a
    normal trie walks a single deterministic path, but '.' means "any child
    could continue the word." At a '.', instead of following one edge we must
    try *every* child and succeed if any branch does. That's a depth-first
    search over the trie, and plain characters are just the degenerate case
    with exactly one branch to try.
    """

    def __init__(self) -> None:
        self.root = TrieNode()

    def addWord(self, word: str) -> None:
        """Standard trie insert — the wildcard only ever appears in queries."""
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_word = True

    def search(self, word: str) -> bool:
        """DFS from the root, branching on every '.'.

        We match character index `i` of `word` against tree `node`:
        - past the last character -> success iff this node ends a word;
        - a '.' -> recurse into *all* children, succeed if any subtree matches;
        - a real char -> recurse into that one child if it exists.
        """

        def dfs(i: int, node: "TrieNode") -> bool:
            if i == len(word):
                return node.is_word
            ch = word[i]
            if ch == ".":
                # try every possible next character
                return any(dfs(i + 1, child) for child in node.children.values())
            # ordinary character: only one path can match
            if ch not in node.children:
                return False
            return dfs(i + 1, node.children[ch])

        return dfs(0, self.root)


def _test() -> None:
    # Official LeetCode example
    wd = WordDictionary()
    wd.addWord("bad")
    wd.addWord("dad")
    wd.addWord("mad")
    assert wd.search("pad") is False   # no such word
    assert wd.search("bad") is True    # exact match
    assert wd.search(".ad") is True    # '.' matches b/d/m
    assert wd.search("b..") is True    # b + any two -> "bad"

    # Edge cases
    assert wd.search("...") is True    # any 3-letter word (bad/dad/mad)
    assert wd.search("....") is False  # no 4-letter words stored
    assert wd.search("ba") is False    # prefix of a word, not a word
    assert wd.search(".a.") is True    # matches all three

    # Wildcard must not walk off a shorter branch
    wd2 = WordDictionary()
    wd2.addWord("a")
    assert wd2.search(".") is True
    assert wd2.search("a") is True
    assert wd2.search("..") is False

    print("word_dictionary: all cases passed")


if __name__ == "__main__":
    _test()
