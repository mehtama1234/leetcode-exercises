# 139. Word Break

**Pattern:** Dynamic programming (walk string positions, cache "is the rest solvable?")
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/word-break/

## The problem in plain words

You get a string like `"applepenapple"` and a set of allowed words like
`["apple", "pen"]`. Can you chop the string into those words, back to back, using
each word as many times as you want? Return true or false.

```diagram
   s = "applepenapple"     words = { apple, pen }

     apple | pen | apple
     -----   ---   -----
       ok     ok     ok      ->  TRUE
```

## Why this matters

The real question is **can this sequence be cut into legal pieces from a known
vocabulary**. It's a reachability walk: from position `i`, does some allowed chunk
carry me to a position from which the rest is *also* solvable? You store that
yes/no per position instead of re-deriving it down every path.

That's the machinery behind splitting space-free text into words (Chinese,
Japanese, or run-together hashtags like `#thisisawesome`), a lexer deciding
whether an input breaks into valid tokens, and a spellchecker asking whether a
compound is built from real words.

## Start from the obvious

Where does the *first* word end? You don't know, so try every cut. If a prefix
`s[0:j]` is an allowed word, then the whole string works exactly when the **rest**,
`s[j:]`, also works — the same question on a shorter string.

```
breakable(s) = some prefix is a word AND the remainder is breakable
breakable("") = True
```

Peel a word off the front, recurse on what's left. Correct, and the honest first
thought.

## Find the waste

Different cuts land you on the **same leftover**. Splitting `"aaaa"` as `a|aaa`
and as `aa|aa` both leave you asking "is `aaa` breakable?" — and `a|a|aa`,
`aa|a|a`, ... pile on more repeats.

```diagram
   "aaaa"          the recursion reaches "aa" (start index 2) many ways:

     a | a | aa...   -> asks breakable("aa")
     aa | aa         -> asks breakable("aa")   again
     a | aaa? no...

   same suffix, re-solved once per path that reaches it -> exponential
```

But a leftover is fully described by **one number**: where it starts. There are
only `n + 1` start positions, so only `n + 1` real subproblems.

## The insight

Let `dp[i]` mean "**can `s[i:]` be broken into allowed words?**" Only `n + 1` of
these exist. Fill from the end:

- `dp[n] = True` — the empty tail is already done (you used up the string).
- Going backward: `dp[i] = True` if for some `j`, `s[i:j]` is a word **and**
  `dp[j]` is already True. The answer is `dp[0]`.

```diagram
   s = "leetcode"   words = { leet, code }   (n=8)

   index: 0 1 2 3 4 5 6 7 8
          l e e t c o d e

   dp[8] = True                          (empty tail)
   dp[4]: "code" is a word, dp[8] True  -> dp[4] = True
   dp[0]: "leet" is a word, dp[4] True  -> dp[0] = True   <-- answer

   dp:  [ T,  _,  _,  _,  T,  _,  _,  _,  T ]
          0               4               8
          |_______________^_______________^
          "leet" jumps 0->4     "code" jumps 4->8

   dp[i] reads dp[j] for the word that starts at i
```

Top-down it's the same rule with a cache keyed on the start index; bottom-up it's
this table filled right to left.

## Complexity

- **Time:** about n × n × L — `n` start positions, each tries up to `n` end
  points, and each candidate chunk costs about `L` to slice and hash (`L` = the
  longest word). Testing only real word lengths trims the constant.
- **Space:** about n for the table, plus the size of the word set.

## Pitfalls

- Forgetting `dp[n] = True`. Without it every path dead-ends and you always
  return false.
- Storing the vocabulary as a **list** instead of a **set** — that turns each
  membership check into a full scan and blows up the time.
- This asks *whether* a split exists. Counting all splits or listing them (Word
  Break II) is a heavier, different problem.
- Words are **reusable**, so `"applepenapple"` legitimately uses `"apple"` twice.

## Transfer

The shape is "walk a line of positions; `dp[i]` depends on jumping ahead by an
allowed step." Same skeleton as [Coin Change / 322](../0322-coin-change/) (reach
an amount with reusable coins), Jump Game, and its true/false-vs-counting sibling
[Decode Ways / 91](../0091-decode-ways/). Whenever a brute force keeps re-asking
"is the rest solvable from here?", key the subproblem on *here* and cache it.
