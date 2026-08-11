# 208. Implement Trie (Prefix Tree)

**Pattern:** Trie (prefix tree)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/implement-trie-prefix-tree/

## The problem in plain words

Build a container for words that supports three operations:

- `insert(word)` — remember a word.
- `search(word)` — is this exact word here?
- `startsWith(prefix)` — does any stored word begin with this prefix?

The catch is the third one. "Exact word here?" is easy. "Does anything start
with `app`?" is the operation that shapes the whole design.

## Start from the obvious

Keep the words in a hash set.

```
words = set()
insert(w):      words.add(w)
search(w):      return w in words
startsWith(p):  return any(w.startswith(p) for w in words)
```

`insert` and `search` are `O(1)` — great. But `startsWith` has to look at
*every* stored word and test its prefix. With `n` words of length up to `L`,
that's `O(n·L)` per prefix query. As the dictionary grows, prefix checks get
slower and slower even though the prefix itself is short.

## Find the waste

Why should asking "does anything start with `app`?" depend on how many words we
stored? The answer only depends on the three characters `a`, `p`, `p`. The hash
set throws away all the *shared structure* between words — "apple", "apply", and
"app" all begin the same way, but the set stores three unrelated strings and
re-derives the shared prefix on every scan.

## The insight

Store the words as a **tree of characters**, one node per character position.
Words that share a prefix share a path from the root. Then:

- Following a string down the tree, character by character, is the prefix check.
  If you fall off the tree (a character has no child), nothing has that prefix.
- To tell a *word* apart from a mere prefix, mark the node where a word ends with
  a boolean flag `is_word`. "app" and "apple" travel the same first three nodes;
  only the flag says whether "app" was actually inserted.

```
insert("apple"); insert("app")

root
 └a─p─p*        (* = is_word)
       └l─e*
```

`search` walks to the end of the string and returns the flag there.
`startsWith` walks to the end of the prefix and just checks that it *arrived*.

## Complexity

- **Time:** every operation is `O(k)` where `k` is the length of the query
  string — one step per character. Crucially, this is independent of how many
  words are stored, which is exactly what the hash set couldn't promise for
  `startsWith`.
- **Space:** `O(total characters inserted)` in the worst case (no shared
  prefixes). Shared prefixes collapse onto one path, so real dictionaries use
  far less.

## Pitfalls

- Forgetting the `is_word` flag and treating "reached a node" as "found a word".
  Then `search("app")` wrongly returns true just because "apple" exists.
- Setting `is_word` on every node instead of only the final one.
- Confusing `search` and `startsWith` — they walk identically and differ *only*
  in the check at the end. Factor the walk out so the difference is visible.
- The empty string: inserting `""` should mark the root as a word, and
  `startsWith("")` should be true whenever the trie exists (you're already at
  the root).

## Transfer

The trie is the base structure for a whole family of prefix problems: add a
wildcard match and you get
[Add and Search Word / 211](../0211-design-add-and-search-words-data-structure/);
lay a trie over a board and you can prune a DFS in
[Word Search II / 212](../0212-word-search-ii/). Reach for a trie whenever you
need prefix queries, autocomplete, or to search many words *simultaneously*
instead of one at a time.
