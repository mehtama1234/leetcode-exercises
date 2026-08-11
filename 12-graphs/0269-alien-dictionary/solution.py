"""269. Alien Dictionary — https://leetcode.com/problems/alien-dictionary/

You're given a list of words sorted according to some unknown alien alphabet.
Deduce a valid ordering of the alien letters. Return "" if no valid order exists.

Sorted words leak ordering hints: comparing two adjacent words, the first place
they differ tells you one letter comes before another. Collect all those "x before
y" facts into a directed graph and topologically sort the letters.
"""
from typing import List, Dict, Set
from collections import deque


def alien_order(words: List[str]) -> str:
    """Build ordering edges from adjacent words, then topo-sort. O(C) time.

    (C = total number of characters across all words.)

    Two ideas stitched together:
      1. EXTRACT constraints. Every pair of adjacent words is already in order.
         Their first differing character (a in the earlier word, b in the later)
         proves 'a comes before b'. Characters before that point are equal and say
         nothing; characters after it are irrelevant to *this* pair.
      2. ORDER the letters. Those 'a before b' facts form a directed graph over the
         letters; a valid alphabet is any topological sort of it (Kahn's here). A
         cycle means the constraints contradict each other -> no valid order -> "".

    One nasty edge case: if an earlier word is a PREFIX of a longer later word yet
    appears AFTER it (e.g. "abc" before "ab"), the input is inconsistent — return
    "" — because a prefix must sort first.
    """
    # Seed the graph with every letter that appears, so lonely letters still show
    # up in the output.
    adj: Dict[str, Set[str]] = {c: set() for word in words for c in word}
    indegree: Dict[str, int] = {c: 0 for c in adj}

    # Derive one edge per adjacent pair from their first difference.
    for first, second in zip(words, words[1:]):
        min_len = min(len(first), len(second))
        # Prefix-inconsistency: longer word first but they match up to min_len.
        if len(first) > len(second) and first[:min_len] == second[:min_len]:
            return ""
        for a, b in zip(first, second):
            if a != b:
                if b not in adj[a]:
                    adj[a].add(b)   # a must come before b
                    indegree[b] += 1
                break               # only the FIRST difference is informative

    # Kahn's topological sort over the letters.
    ready = deque(c for c in indegree if indegree[c] == 0)
    order: List[str] = []
    while ready:
        c = ready.popleft()
        order.append(c)
        for nxt in adj[c]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                ready.append(nxt)

    # If we couldn't place every letter, a cycle blocked us -> invalid.
    if len(order) != len(indegree):
        return ""
    return "".join(order)


def _test() -> None:
    # Official example: order is w < e < r < t < f (one valid answer).
    r1 = alien_order(["wrt", "wrf", "er", "ett", "rftt"])
    assert set(r1) == set("wertf")
    # Verify it's a valid topological order for the known constraints.
    for a, b in [("w", "e"), ("e", "r"), ("r", "t"), ("t", "f")]:
        assert r1.index(a) < r1.index(b), (a, b, r1)

    # Contradiction: t<f from pair 1, but f<t from pair 2 -> impossible.
    assert alien_order(["z", "x", "z"]) == ""

    # Prefix inconsistency: "abc" sorted before "ab" is invalid.
    assert alien_order(["abc", "ab"]) == ""

    # Simple two-letter order.
    assert alien_order(["z", "x"]) == "zx"

    # Single word: no ordering constraints, all its distinct letters valid in any
    # order.
    assert set(alien_order(["abc"])) == set("abc")

    # Valid prefix ordering ("ab" before "abc") is fine.
    assert set(alien_order(["ab", "abc"])) == set("abc")

    print("alien_order: all cases passed")


if __name__ == "__main__":
    _test()
