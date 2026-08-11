# 139. Word Break

**Pattern:** Dynamic programming (1-D over string positions)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/word-break/

## The problem in plain words

You're given a string like `"applepenapple"` and a set of allowed words like
`["apple", "pen"]`. Can you chop the string into a sequence of those words, back
to back, using each word as many times as you like? Return true or false.

## Start from the obvious

Where does the *first* word end? You don't know, so try every possibility. If
some prefix `s[0:j]` is a dictionary word, then the whole string is breakable iff
the **rest** of the string, `s[j:]`, is also breakable — the same question on a
shorter string:

```
breakable(s) = any prefix that is a dict word, whose remainder is also breakable
breakable("") = True
```

Recursively: pick a word off the front, recurse on what's left. Correct, and the
natural first thought.

## Find the waste

Different prefix choices land you on the **same suffix**. Splitting
`"aaaa"` as `a|aaa` and as `aa|aa` both leave you asking "is `aaa` breakable?" —
and `a|a|aa`, `aa|a|a`, ... pile up even more repeats. The naive recursion
re-solves each suffix once per path that reaches it, and the number of paths is
exponential.

But a suffix is fully described by **one number**: where it starts. There are only
`n + 1` starting positions. So there are only `n + 1` real subproblems.

## The insight

Let `dp[i]` mean "**can `s[i:]` be broken into dictionary words?**" There are only
`n + 1` of these, so compute each once.

Base case: `dp[n] = True` — the empty suffix is trivially "broken" (you've used up
the string). Then, going from the end backward:

```
dp[i] = True  if for some j: s[i:j] is a dict word AND dp[j] is True
```

That is: some word starts at `i`, and after that word the rest is breakable. The
answer is `dp[0]`.

Top-down it's the same thing with a cache keyed on the start index; bottom-up it's
this table filled right-to-left.

## Complexity

- **Time:** `O(n^2 * L)` — `n` positions, each tries up to `n` end points, and
  each candidate substring costs `O(L)` to slice and hash (`L` = max word length).
  (Using a set of word lengths to only test real lengths trims the constant.)
- **Space:** `O(n)` for the table, plus `O(total dictionary length)` for the word
  set.

## Pitfalls

- Forgetting the base case `dp[n] = True`; without it every path dead-ends and you
  always return false.
- Testing membership against a **list** instead of a **set** — that turns each
  lookup into an `O(dict)` scan and blows up the time.
- This asks *whether* a split exists. Counting all splits or returning them (Word
  Break II) is a different, heavier problem.
- Words are **reusable**, so `"applepenapple"` legitimately uses `"apple"` twice.

## Transfer

The shape is "walk a line of positions; `dp[i]` depends on jumping ahead by an
allowed step." It's the same skeleton as
[Coin Change / 322](../0322-coin-change/) (reach an amount using reusable coins),
Jump Game, and Decode Ways (reach the end of a digit string). Whenever a brute
force keeps re-asking "is the rest solvable from here?", key the subproblem on
*here* and cache it.
