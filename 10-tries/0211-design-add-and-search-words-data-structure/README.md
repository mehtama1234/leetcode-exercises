# 211. Design Add and Search Words Data Structure

**Pattern:** Trie + DFS (wildcard search)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/design-add-and-search-words-data-structure/

## The problem in plain words

Build a container that supports:

- `addWord(word)` — store a word.
- `search(word)` — is a matching word stored? A `.` in the query is a wildcard
  that matches *any single* character. So `search(".ad")` matches "bad", "dad",
  or "mad".

## Start from the obvious

If there were no wildcard, this is exactly [Trie 208](../0208-implement-trie-prefix-tree/):
insert words, and `search` walks a single path to the end and checks the
end-of-word flag.

Now add the `.`. The obvious first thought is to keep every word in a list and,
for each query, test it against every stored word character by character:

```
search(q):
    for w in words:
        if len(w) == len(q) and all(qc == '.' or qc == wc
                                     for qc, wc in zip(q, w)):
            return True
    return False
```

Correct, but every search scans the whole dictionary — `O(n·L)` per query.

## Find the waste

Same waste as an ordinary trie: the flat list re-examines unrelated words that
share nothing with the query, and it re-derives shared prefixes over and over.
We already know a trie collapses shared prefixes onto one path. The only new
question is: what does a trie do when the query says "any character here"?

## The insight

A normal trie `search` is a walk down **one** deterministic path — at each step
the character tells you the single child to follow. The `.` breaks that
determinism: it says *any* child could continue the word. So at a `.` we stop
walking a single path and instead **branch into every child**, succeeding if any
branch eventually matches. That's a depth-first search over the trie.

Written as a recursion on `(index into query, current node)`:

- **Ran out of query characters?** Success only if this node ends a word.
- **Current char is `.`?** Recurse into *all* children; succeed if any subtree
  matches the rest of the query.
- **Current char is a real letter?** Recurse into just that child, if it exists.

A plain letter is simply the wildcard case with exactly one branch to try — so
the two cases are the same DFS, one just has a wider fan-out.

```
addWord: bad, dad, mad
search(".ad"):
    at root, '.' -> try children b, d, m
      b -> a -> d (is_word) ✓  → return True
```

## Complexity

- **Time:** with no wildcards, `O(k)` for a query of length `k` (one path).
  Each `.` can fan out to up to 26 children, so the worst case is `O(26^k)` when
  the query is all dots — but real queries have few wildcards, and the DFS
  prunes the moment a character has no matching child.
- **Space:** `O(total characters added)` for the trie, plus `O(k)` recursion
  depth for the search stack.

## Pitfalls

- Treating `.` as "skip a character" instead of "match exactly one" — the
  matched word must have the *same length* as the query. A query of length 3
  can never match a 2-letter word.
- At the end of the query, forgetting to check `is_word` and accepting a node
  that's only a prefix.
- On a `.`, following only the first child instead of trying all of them —
  you'd miss valid matches down the other branches.
- On a real character, forgetting the "child doesn't exist" case and crashing
  instead of returning `False`.

## Transfer

The reusable move is **DFS over a trie when the query is non-deterministic**.
The same "branch into all children at a wildcard" idea powers regex-style prefix
matching and autocomplete-with-typos. Once you can DFS a trie, laying one over a
grid to search many words at once is a short step to
[Word Search II / 212](../0212-word-search-ii/).
