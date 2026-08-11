# 91. Decode Ways

**Pattern:** Dynamic programming (walk a line, sum the ways in, with legality checks)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/decode-ways/

## The problem in plain words

`A=1, B=2, ..., Z=26`. Someone wrote a message as those numbers with no spaces
between them, so `"12"` could have been `AB` (1 then 2) or `L` (12). Given the
digit string, count how many different original messages could have made it.

```diagram
   "226"  can split three ways:

     2 | 2 | 6   ->  B B F
     22 | 6      ->  V F
     2 | 26      ->  B Z

   answer = 3
```

## Why this matters

The real question is **how many legal ways can you cut an ambiguous sequence into
pieces**, where each step has a small set of moves and some moves are illegal. The
count at one spot is the sum of the counts at the spots you can legally jump to.
It's the same shape as counting ways up a staircase, with "is this chunk a real
letter?" checks bolted on.

That shows up wherever a stream splits many ways: a lexer deciding how a run of
characters breaks into tokens, word-segmentation for text with no spaces, reading
a variable-length code like a barcode. The legality rules here (the zero rules,
the `<= 26` cap) are the honest version of "not every chunk is a valid piece."

## Start from the obvious

Read left to right. At each spot you have at most two moves:

- take **one** digit, if it's `1`–`9`, as a letter, then continue after it;
- take **two** digits, if they read `10`–`26`, as a letter, then continue after
  them.

The number of decodings starting at position `i` is the sum over each legal move
of the decodings that follow it:

```
ways(i) = ways(i+1)                 if s[i]     is 1..9
        + ways(i+2)                 if s[i:i+2] is 10..26
ways(n) = 1        # reached the end = one finished message
ways(i) = 0        # if s[i] == '0', no letter starts with 0
```

That recursion is correct and is the honest first thought.

## Find the waste

This is Fibonacci wearing a costume: `ways(i)` calls `ways(i+1)` and `ways(i+2)`,
and those two overlap. `ways(i+2)` gets reached straight from `ways(i)` and again
through `ways(i+1)`, so the call tree branches exponentially.

```diagram
   ways(0)
    ├── ways(1)
    │    ├── ways(2)      <-- computed here
    │    └── ways(3)
    └── ways(2)           <-- and AGAIN here (same answer, recomputed)
         ├── ...
```

But a call is fully described by one number — the position `i`. There are only
`n + 1` positions, so only `n + 1` real subproblems. The exponential tree is
piled on top of a linear set of distinct questions. Answer each once.

## The insight

Let `dp[i]` = the number of ways to decode `s[i:]` (the tail starting at `i`).
Fill it from the back, where the answers it needs are already known.

- `dp[n] = 1` — the empty tail decodes exactly one way (the finished message).
- Going backward: `dp[i] = 0` if `s[i] == '0'` (dead end), otherwise
  `dp[i] = dp[i+1] + (dp[i+2] if s[i:i+2] is 10..26)`.

```diagram
   s = "226"          index:  0   1   2   (n=3)

   dp[3] = 1                              (empty tail)
   dp[2]: s[2]='6' ok, "6.." single only
          dp[2] = dp[3]           = 1
   dp[1]: s[1]='2' ok, "26" is 10..26 too
          dp[1] = dp[2] + dp[3]   = 1 + 1 = 2
   dp[0]: s[0]='2' ok, "22" is 10..26 too
          dp[0] = dp[1] + dp[2]   = 2 + 1 = 3

   table:  dp = [ 3 , 2 , 1 , 1 ]
                  ^answer

   each cell reads only the one or two cells to its right:

        dp[0]   dp[1]   dp[2]   dp[3]
          \      / \      / \      /
           +----+   +----+   (single only)
```

Because `dp[i]` only ever reads `dp[i+1]` and `dp[i+2]`, you never need the whole
table — keep **two rolling numbers** and slide them backward. That's the `O(1)`
space version.

## Complexity

- **Time:** about n steps — each of `n` positions does constant work.
- **Space:** about n for the table or cache, or `O(1)` with the two rolling
  numbers.

## Pitfalls

- **Zeros are the entire difficulty.** A `0` must be absorbed by a preceding `1`
  or `2` (as `10` or `20`); alone or after `3`–`9` it kills the decoding.
  `"0"` → 0, `"06"` → 0, `"100"` → 0.
- The pair check must be a real range test. `"27"` is not one letter (27 > 26),
  and `"10"`/`"20"` are the only valid pairs that end in `0`.
- Base case is `dp[n] = 1`, not `0`. Set it to `0` and every count collapses.
- Compare the two-digit chunk as a number against `26`, or compare digit by
  digit. Comparing strings (`"9" <= "26"`) is a bug.

## Transfer

Same skeleton as [Climbing Stairs / 70](../0070-climbing-stairs/) and Fibonacci —
"each spot reaches the next one or two, sum the ways" — with **legality guards**
(the zero rules and the `<= 26` cap) added. Its sibling
[Word Break / 139](../0139-word-break/) is the true/false version of the same
walk. Whenever you count paths along a line and each step has a small fixed set of
legal moves, this is the pattern.
