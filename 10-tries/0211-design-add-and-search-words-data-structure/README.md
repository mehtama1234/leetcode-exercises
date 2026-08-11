# 211. Design Add and Search Words Data Structure

**Pattern:** Trie + DFS (a walk that branches at a wildcard)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/design-add-and-search-words-data-structure/

## The problem in plain words

Build a container that supports:

- `addWord(word)` — store a word.
- `search(word)` — is a matching word stored? A `.` in the query is a wildcard
  that matches *any single* character. So `search(".ad")` matches "bad", "dad",
  or "mad".

```diagram
   stored: bad, dad, mad

   search("bad") -> exact -> true
   search(".ad") -> first char is a wildcard:
                    _  a  d
                    ^ any letter, then a, then d  -> bad/dad/mad all fit -> true
   search("...") -> three wildcards -> any 3-letter word -> true
```

## Why this matters

The real problem is matching a *pattern with holes* against a whole dictionary
at once — not one fixed string, but a template where some positions can be
anything. The one move that makes it work: turn the trie walk into a search.
Follow one child for a fixed letter, but branch into all children at a wildcard,
and succeed if any branch completes the match.

That's the core of pattern matching in real tools. Spell-checkers and "did you
mean" suggestions treat a suspect position as a wildcard to find near-matches.
Crossword and word-game solvers query patterns like `.a.e`. Simple regex and glob
engines (`?` for one character) do exactly this branch-at-wildcard walk.

What you buy is answering these queries without scanning every stored word.
Shared prefixes are still walked once, and the search prunes the instant a fixed
letter has no matching child — so a normal, wildcard-free query is as fast as a
plain trie lookup.

## Start from the obvious

With no wildcard this is exactly
[Trie 208](../0208-implement-trie-prefix-tree/): insert words, and `search` walks
one path to the end and checks the end-of-word flag.

Now add the `.`. The first thought is to keep every word in a list and, for each
query, test it against every stored word, character by character:

```
search(q):
    for w in words:
        if len(w) == len(q) and all(qc == '.' or qc == wc
                                     for qc, wc in zip(q, w)):
            return True
    return False
```

Correct, but every search scans the whole dictionary — about `n × L` work per
query, and it re-examines words that share nothing with the pattern.

## Find the waste

Same waste as an ordinary trie: the flat list re-checks unrelated words and
re-derives shared prefixes over and over. We already know a trie collapses shared
prefixes onto one path. The only new question is: what does a trie do when the
query says "any character here"?

## The insight

A normal trie `search` walks **one** path — at each step the character names the
single child to follow. The `.` breaks that: it says *any* child could continue
the word. So at a `.` we stop walking one path and **branch into every child**,
succeeding if any branch matches the rest. That's a depth-first search over the
trie (explore one branch fully before trying the next).

Written as a recursion on `(index into query, current node)`:

- **Ran out of query characters?** Success only if this node ends a word.
- **Current char is `.`?** Recurse into *all* children; succeed if any subtree
  matches the rest of the query.
- **Current char is a real letter?** Recurse into just that child, if it exists.

A plain letter is the wildcard case with exactly one branch to try — so both are
the same DFS, one just fans out wider.

```diagram
   trie of bad, dad, mad:

        root
       / | \
      b  d  m
      |  |  |
      a  a  a
      |  |  |
      d* d* d*      (* = end of word)

   search(".ad"):
     at root, '.' -> try b, then d, then m
        b -> a -> d*   at end, is_word? yes  -> return true
        (b branch already succeeded, no need to try d or m)
```

```diagram
   search("b.."):  b is fixed, then two wildcards

     root --b--> [a-node]
        '.' -> only child is a       -> [d-node]
        '.' -> only child is d (end) -> d* , is_word? yes -> true

   search("...."): four wildcards, but every stored word has length 3
     any path runs out of children at depth 3 while query wants a 4th -> false
```

## Complexity

- **Time:** with no wildcards, about `k` steps for a query of length `k` (one
  path). Each `.` can branch to up to 26 children, so the worst case (a query of
  all dots) is about `26^k` — but real queries have few wildcards, and the DFS
  prunes the moment a character has no matching child.
- **Space:** the trie holds the total characters added, plus recursion depth
  about `k` for the search stack.

## Pitfalls

- Treating `.` as "skip a character" instead of "match exactly one" — the matched
  word must have the *same length* as the query. A length-3 query can never match
  a 2-letter word.
- At the end of the query, forgetting to check `is_word` and accepting a node
  that's only a prefix.
- On a `.`, following only the first child instead of trying all of them — you'd
  miss valid matches down the other branches.
- On a real character, forgetting the "child doesn't exist" case and crashing
  instead of returning `False`.

## Transfer

The reusable move is **DFS over a trie when the query is non-deterministic**: at
a step with more than one possible next character, try them all. The same
"branch at a wildcard" idea powers regex-style prefix matching and
autocomplete-with-typos. Once you can DFS a trie, laying one over a grid to search
many words at once is a short step to
[Word Search II / 212](../0212-word-search-ii/).
