# 91. Decode Ways

**Pattern:** Dynamic programming (1-D, look ahead one or two, count paths)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/decode-ways/

## The problem in plain words

`A=1, B=2, ..., Z=26`. Someone encoded a message by writing those numbers with no
separators, so `"12"` could have been `AB` (1, 2) or `L` (12). Given the digit
string, **count how many different original messages** could have produced it.

## Start from the obvious

Read the string left to right. At each spot you have at most two moves:

- Take **one** digit, if it's `1`–`9`, as a letter, and continue after it.
- Take **two** digits, if they form `10`–`26`, as a letter, and continue after
  them.

The total number of decodings from position `i` is the sum of the decodings that
follow each legal move:

```
ways(i) = ways(i+1)                      if s[i]   in 1..9
        + ways(i+2)                      if s[i:i+2] in 10..26
ways(n) = 1        # reached the end = one full decoding
ways(i) = 0        # if s[i] == '0', no letter starts with 0
```

That recursion is correct and is the honest first thought.

## Find the waste

This is Fibonacci in disguise: `ways(i)` calls `ways(i+1)` and `ways(i+2)`, and
those overlap heavily. `ways(i+2)` gets reached both directly from `ways(i)` and
again through `ways(i+1)`. The call tree is exponential, but a call is fully
described by a single number — the position `i`. There are only `n + 1` positions.

So, as always: exponential recomputation sitting on top of a linear set of real
subproblems.

## The insight

Let `dp[i]` = "number of ways to decode `s[i:]`." Only `n + 1` of these exist;
solve each once.

- `dp[n] = 1` (empty tail decodes exactly one way — the empty message).
- Going backward, `dp[i] = 0` if `s[i] == '0'` (dead), otherwise
  `dp[i] = dp[i+1] + (dp[i+2] if s[i:i+2] is 10..26)`.

Because `dp[i]` only ever reads `dp[i+1]` and `dp[i+2]`, you never need the full
table — keep **two rolling variables** and slide them backward. That's the `O(1)`
space version.

## Complexity

- **Time:** `O(n)` — each of `n` positions does constant work.
- **Space:** `O(n)` memoized / table, or `O(1)` with the two rolling variables.

## Pitfalls

- **Zeros are the whole difficulty.** A `0` must be swallowed by a preceding `1`
  or `2` (as `10` or `20`); on its own or after `3`–`9` it kills the decoding.
  `"0"` -> 0, `"06"` -> 0, `"100"` -> 0.
- The pair check must be a real range test: `"27"` is not decodable as one letter
  (27 > 26), and `"10"`/`"20"` are the *only* valid pairs starting with `1`/`2`
  that end in `0`.
- Base case is `dp[n] = 1`, not `0` — otherwise every count collapses to zero.
- Compare the two-digit slice as an integer against `26`, or compare digit by
  digit; string comparison of `"9" <= "26"` is a bug.

## Transfer

Same recurrence skeleton as [Fibonacci / 509](../0509-fibonacci-number/) and
[Climbing Stairs / 70](../0070-climbing-stairs/) — "each state reaches the next
one or two, sum the ways" — with **validity guards** (the zero and `<= 26` rules)
layered on. Whenever you count paths through a line and each step has a small,
fixed set of legal moves, this is the pattern.
