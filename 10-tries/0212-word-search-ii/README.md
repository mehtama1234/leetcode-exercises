# 212. Word Search II

**Pattern:** Trie + grid DFS (search many words in one walk, prune off the trie)
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/word-search-ii/

## The problem in plain words

You have a grid of letters and a list of words. A word is "on the board" if you
can spell it by starting at some cell and stepping to an up/down/left/right
neighbor each time, never stepping on the same cell twice. Return every word from
the list that is on the board.

```diagram
   board:            words: oath, eat, pea, rain

     o  a  a  n
     e  t  a  e
     i  h  k  r
     i  f  l  v

   "oath": o(0,0)->a(0,1)->t(1,1)->h(2,1)   found
   "eat":  e(1,0)->a(0,1)... wait, must be adjacent each step
           e(1,3)->a(1,2)->t(1,1)          found
   "pea":  no 'p' on the board             not found
```

## Why this matters

The real problem is searching for *many patterns at once* over a shared space,
instead of running one search per pattern. The one move that makes it work: drive
a single traversal with a trie of all the target words, so overlapping words are
explored together and a dead end kills the search for every word that shares it.

This "match many strings in one pass" idea is a workhorse. Multi-keyword scanners
— intrusion detection, spam and malware filters, content moderation — check text
against thousands of patterns at the same time (Aho-Corasick is the classic
trie-driven version). Search engines and DNA tools screen for many motifs at once.
Boggle-style word games are this exact grid version.

What you buy is turning "run one search per word" into one guided walk, and using
"fell off the trie" as instant pruning — a single unmatched letter eliminates all
the words that would have needed it.

## Start from the obvious

We already know how to check whether *one* word is on the board — that's
[Word Search / 79](../../09-backtracking/0079-word-search/): a DFS from every
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
`o -> a -> t` from every cell. The shared prefix "oat" is re-walked once per word,
from scratch. The search is organized around *words*, so it can't see that many
words share a beginning.

```diagram
   brute force, per word, re-hunts the shared start:

   search "oat":     o -> a -> t
   search "oath":    o -> a -> t -> h      <- re-walks o,a,t
   search "oatmeal": o -> a -> t -> m ...  <- re-walks o,a,t again

   the "oat" prefix is paid for 3 times
```

We fixed this exact "shared prefixes re-derived over and over" waste before — with
a **trie** (see [208](../0208-implement-trie-prefix-tree/)).

## The insight

Flip the loop. Instead of "for each word, search the board," do **one** DFS over
the board that is *guided by a trie of all the words at once*.

Put every word into a trie. Then DFS from each cell while stepping down the trie
in lockstep:

- At a grid cell with letter `ch` and trie node `node`, look up
  `node.children[ch]`.
- No such child? **This letter can't extend any remaining word — prune the whole
  branch now.** That's the payoff: one dead letter kills the search for *all*
  words at once.
- Child exists? Keep walking the grid's neighbors from that child.
- Child marks the end of a word? Record that word.

```diagram
   words oat, oath  ->  trie:

        root
         |
         o
         |
         a
         |
         t*(oat)
         |
         h*(oath)

   grid path o->a->t lands on t*(oat)  -> collect "oat"
   keep going ->h    lands on h*(oath) -> collect "oath"
   both words found in ONE descent of the shared o-a-t path
```

Two implementation tricks keep it clean:

1. **Store the whole word on its end node** (`node.word = word`). When the DFS
   lands on an end node, the answer is right there — no path to reconstruct.
2. **De-duplicate by clearing `node.word = None`** after collecting it, so a word
   reachable by two grid paths is reported only once.

Visited-cell handling is the same backtracking as Word Search 79: mark the cell
(`board[r][c] = "#"`) before recursing, restore it after, so each path uses a cell
at most once but other starting paths can still use it.

## Complexity

Let the board be `m × n` and let `L` be the length of the longest word.

- **Time:** about `m · n · 4^L` in the worst case — a DFS from every cell,
  branching up to 4 directions, depth capped at `L` because the trie has no path
  longer than the longest word. In practice the trie pruning cuts this
  enormously: most branches die at the first letter that isn't a valid prefix.
- **Space:** the total characters in all words for the trie, plus recursion depth
  about `L`.

## Pitfalls

- Not marking cells visited (or forgetting to restore them) — a path could reuse
  a cell, so "abcb" on a board with a single `b` would wrongly match.
- Reporting the same word multiple times when several grid paths spell it. Clear
  the end marker after collecting.
- Reconstructing the found word from the path instead of storing it on the end
  node — easy to get subtly wrong; the stored word is exact.
- Building the trie inside the per-cell loop instead of once up front.
- A common extra optimization is pruning dead trie leaves as words are found;
  it's not required for correctness, so this solution keeps it simple.

## Transfer

The reusable idea is **use a trie to search for many strings at once, and let
"fell off the trie" be your pruning signal.** This turns "one search per word"
into a single guided walk. The board-DFS backtracking is
[Word Search / 79](../../09-backtracking/0079-word-search/); the trie half is
[208](../0208-implement-trie-prefix-tree/) and
[211](../0211-design-add-and-search-words-data-structure/). Any time you're about
to loop "for each pattern, search the whole space," ask whether a trie lets you
search for all patterns in one pass.
