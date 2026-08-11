"""208. Implement Trie (Prefix Tree) — https://leetcode.com/problems/implement-trie-prefix-tree/

Build a data structure that stores words and can answer two questions fast:
"is this exact word here?" and "does any stored word start with this prefix?".
"""
from typing import Dict


class TrieNode:
    """One character position in the tree.

    Two pieces of state: a map from next-character to the child node that
    continues the word, and a flag marking whether a complete word ends *here*.
    The flag is what separates a real word from a mere prefix of one.
    """

    def __init__(self) -> None:
        self.children: Dict[str, "TrieNode"] = {}
        self.is_word: bool = False


class Trie:
    """A prefix tree.

    Why not just a hash set of words? A set answers `search` in O(1), but it
    cannot answer `startsWith` without scanning every stored word. The trie
    shares common prefixes on a single path, so walking that path *is* the
    prefix check — both queries cost O(length of the query), independent of how
    many words are stored.
    """

    def __init__(self) -> None:
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        """Walk the word char by char, creating missing nodes, then mark the end.

        Marking `is_word` on the final node is the whole trick: the same path
        that spells "app" is a prefix of the path that spells "apple", so the
        flag is the only way to know "app" was itself inserted.
        """
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_word = True

    def _walk(self, prefix: str) -> "TrieNode | None":
        """Follow `prefix` from the root; return the node it lands on, or None.

        Shared by `search` and `startsWith` because both first need to reach
        the end of the query string — they only differ in what they check there.
        """
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def search(self, word: str) -> bool:
        """True only if `word` was inserted as a complete word."""
        node = self._walk(word)
        return node is not None and node.is_word

    def startsWith(self, prefix: str) -> bool:
        """True if any inserted word begins with `prefix` (the node just existing
        is enough — we don't care whether a word ends there)."""
        return self._walk(prefix) is not None


def _test() -> None:
    # Official LeetCode example
    trie = Trie()
    trie.insert("apple")
    assert trie.search("apple") is True       # exact word present
    assert trie.search("app") is False        # only a prefix, not inserted
    assert trie.startsWith("app") is True      # a word starts with "app"
    trie.insert("app")
    assert trie.search("app") is True          # now inserted as a word

    # Edge cases
    empty = Trie()
    assert empty.search("a") is False          # nothing inserted
    assert empty.startsWith("") is True        # empty prefix matches the root
    empty.insert("")                            # empty word is a valid insert
    assert empty.search("") is True

    # Prefix must not report false positives
    t2 = Trie()
    t2.insert("banana")
    assert t2.startsWith("ban") is True
    assert t2.startsWith("bon") is False
    assert t2.search("banan") is False         # prefix of a word, not a word

    print("implement_trie: all cases passed")


if __name__ == "__main__":
    _test()
