# 212. Word Search II

**Pattern:** Trie + grid DFS (backtracking with pruning)
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/word-search-ii/

## The problem in plain words

You have a grid of letters and a list of words. A word is "on the board" if you
can spell it by starting at some cell and repeatedly stepping to an
up/down/left/right neighbor, never stepping on the same cell twice. Return all
the words from the list that are on the board.

## Why this matters

The deeper problem is searching for *many patterns at once* over a shared space, instead of running one search per pattern. The fundamental operation is driving a single traversal with a trie of all the targets, so overlapping patterns are explored together and a dead end kills the search for every pattern that shares it.

This "match many strings in one pass" idea is a real workhorse. Multi-keyword scanners — intrusion detection, spam and malware filters, content moderation — check text against thousands of patterns simultaneously (Aho-Corasick is the classic trie-driven version). Search engines and DNA/sequence tools screen for many motifs at once. Log analyzers and DLP systems flag any of a large ruleset in a single scan. Boggle-style word-game solvers are this exact grid version.

What you're solving for is collapsing an `O(patterns × search_cost)` problem into one guided search, and using "fell off the trie" as instant pruning — a single unmatched letter eliminates all the words that would have needed it. That's what makes screening against huge pattern sets fast enough to run in real time.

## Start from the obvious

We already know how to check whether *one* word is on the board — that's
[Word Search / 79](../../11-backtracking/0079-word-search/): a DFS from every
cell, marking cells visited so a path can't reuse them. So just do that for each
word:

```
for w in words:
    if board_contains(w):   # a full DFS over the whole board
        answer.append(w)
```

Correct. But look at what it repeats.

## Find the waste

Suppose the list has "oath", "oat", and "oatmeal". The brute force runs three
separate board searches, and all three begin by hunting for the same path
`o → a → t` from every cell. The shared prefix "oat" is re-walked once per word,
from scratch. The search is organized around *words*, so it can't see that many
words share a beginning.

We fixed this exact "shared prefixes re-derived over and over" waste before —
with a **trie** (see [208](../0208-implement-trie-prefix-tree/)).

## The insight

Flip the loop. Instead of "for each word, search the board," do **one** DFS over
the board that is *guided by a trie of all the words at once*.

Put every word into a trie. Then DFS from each cell while simultaneously
descending the trie:

- At grid cell with letter `ch` and trie node `node`, look up `node.children[ch]`.
- If there's no such child, **this letter cannot extend any remaining word — prune
  the whole branch immediately.** This is the payoff: one dead letter kills the
  search for *all* words at once.
- If the child exists, keep walking the grid's neighbors from that child.
- If the child node marks the end of a word, record that word.

All words sharing a prefix travel that prefix together, exactly once, and the
trie prunes any grid path that doesn't spell some word's prefix.

Two implementation tricks make it clean:

1. **Store the whole word on its end node** (`node.word = word`). When the DFS
   lands on an end node, the answer is right there — no need to reconstruct the
   path.
2. **De-duplicate by clearing `node.word = None`** after collecting it, so the
   same word found via two grid paths is reported only once.

```
words: oath, oat        trie:  o─a─t*(oat)
                                     └h*(oath)
grid path o→a→t hits t*  -> collect "oat"
continue    →h  hits h*  -> collect "oath"
```

Visited-cell handling is the same backtracking as Word Search 79: mark the cell
(`board[r][c] = "#"`) before recursing, restore it after, so each path uses a
cell at most once but other starting paths can still use it.

## Complexity

Let the board be `m × n` and let `L` be the length of the longest word.

- **Time:** `O(m · n · 4^L)` in the worst case — a DFS from every cell, branching
  up to 4 directions, depth capped at `L` because the trie has no path longer
  than the longest word. In practice the trie pruning cuts this enormously: most
  branches die at the first letter that isn't a valid prefix.
- **Space:** `O(total characters in all words)` for the trie, plus `O(L)`
  recursion depth.

## Pitfalls

- Not marking cells visited (or forgetting to restore them) — you'd let a path
  reuse a cell, so "abcb" on a board with a single `b` would wrongly match.
- Reporting the same word multiple times when several grid paths spell it. Clear
  the end marker after collecting.
- Reconstructing the found word from the path instead of storing it on the end
  node — easy to get subtly wrong; the stored word is exact.
- Building the trie inside the per-cell loop instead of once up front.
- A common extra optimization is pruning dead trie leaves as words are found;
  it's not required for correctness, so this solution keeps it simple.

## Transfer

The reusable idea is **use a trie to search for many strings simultaneously,
and let "fell off the trie" be your pruning signal.** This turns an
`O(number_of_words × search_cost)` problem into a single guided search. The same
board-DFS backtracking is [Word Search / 79](../../11-backtracking/0079-word-search/);
the trie half is [208](../0208-implement-trie-prefix-tree/) and
[211](../0211-design-add-and-search-words-data-structure/). Any time you're about
to loop "for each pattern, search the whole space," ask whether a trie lets you
search for all patterns in one pass.
