# 208. Implement Trie (Prefix Tree)

**Pattern:** Trie (share the common start of many words on one path)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/implement-trie-prefix-tree/

## The problem in plain words

Build a container for words with three operations:

- `insert(word)` — remember a word.
- `search(word)` — is this exact word in here?
- `startsWith(prefix)` — does any stored word begin with this prefix?

The first two are easy to picture. The third one shapes the whole design:
answering "does anything start with `app`?" is what a plain list of words is bad
at.

```diagram
   insert: apple, app, apricot

              root
               |
               a
               |
               p
              / \
             p   r
             |   |
             l   i
             |   |
             e   c
                 |
                 o
                 |
                 t

   startsWith("ap") -> walk a, p  -> arrived -> yes
```

## Why this matters

The real question is answering *prefix* queries fast: "does anything begin with
these few characters?" in time that depends on the query, not on how much you've
stored. The one move that makes it work is sharing the common start of many
words on a single path, so a prefix is checked by walking characters instead of
scanning words.

This is the structure behind autocomplete. Every keystroke asks "which stored
terms start with what I've typed?", and a trie answers in a few steps no matter
how large the dictionary. IP routers do longest-prefix matching on address bits
to pick a route. Spell-checkers, predictive text on phones, and command-line tab
completion all lean on prefix trees.

What you buy is prefix queries whose cost is the length of the prefix (a few
steps), not the size of the dictionary. Under a per-keystroke deadline, being
independent of how many words are stored is the whole point.

## Start from the obvious

Keep the words in a hash set.

```
words = set()
insert(w):      words.add(w)
search(w):      return w in words
startsWith(p):  return any(w.startswith(p) for w in words)
```

`insert` and `search` are one step each. But `startsWith` has to test *every*
stored word. With `n` words up to length `L`, that's about `n × L` work per
prefix query. As the dictionary grows, a check on a three-letter prefix gets
slower and slower — even though the prefix never changed.

## Find the waste

Why should asking "does anything start with `app`?" depend on how many words you
stored? The answer only needs the three characters `a`, `p`, `p`. The set throws
away all the *shared structure* between words: "apple", "apply", and "app" begin
the same way, but the set holds three unrelated strings and re-derives that
shared beginning on every scan.

```diagram
   hash set:   [ "apple" ] [ "apply" ] [ "app" ]
                  a p p       a p p       a p p     <- same start, stored 3 times
                              ^ re-checked from scratch on every startsWith
```

## The insight

Store the words as a **tree of characters** — one node per character position.
Words that share a prefix share a path down from the root. Now:

- Following a string down the tree, character by character, *is* the prefix
  check. If you fall off the tree (a character has no child), nothing has that
  prefix.
- To tell a real *word* apart from a mere prefix, mark the node where a word ends
  with a flag `is_word`. "app" and "apple" walk the same first three nodes; only
  the flag says whether "app" was itself inserted.

```diagram
   insert("apple"); insert("app")

      root
       |
       a
       |
       p
       |
       p  <- is_word (app was inserted)
       |
       l
       |
       e  <- is_word (apple was inserted)

   search("app")    -> walk a,p,p -> node exists AND is_word -> true
   search("appl")   -> walk a,p,p,l -> node exists but is_word=false -> false
   startsWith("appl")-> walk a,p,p,l -> arrived -> true
```

`search` walks to the end of the string and returns the flag there.
`startsWith` walks to the end of the prefix and only checks that it *arrived*.
Same walk, different question at the end.

## Complexity

- **Time:** every operation is about `k` steps, where `k` is the length of the
  query string — one step per character. This does not depend on how many words
  are stored, which is exactly what the hash set couldn't promise for
  `startsWith`.
- **Space:** in the worst case (no shared prefixes) about the total number of
  characters inserted. Shared prefixes collapse onto one path, so real
  dictionaries use far less.

## Pitfalls

- Forgetting the `is_word` flag and treating "reached a node" as "found a word".
  Then `search("app")` wrongly returns true just because "apple" exists.
- Setting `is_word` on every node instead of only the final one.
- Confusing `search` and `startsWith` — they walk identically and differ *only*
  in the check at the end. Factor the walk out so the difference is visible.
- The empty string: inserting `""` marks the root as a word, and `startsWith("")`
  is true whenever the trie exists (you're already at the root).

## Transfer

The trie is the base structure for a whole family of prefix problems. Add a
wildcard to the search and you get
[Add and Search Word / 211](../0211-design-add-and-search-words-data-structure/);
lay a trie over a grid and it prunes a DFS in
[Word Search II / 212](../0212-word-search-ii/). Reach for a trie whenever you
need prefix queries, autocomplete, or to search many words *at once* instead of
one at a time.
