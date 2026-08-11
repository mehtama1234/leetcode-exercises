# 20. Valid Parentheses

**Pattern:** Stack (match "most recent open" first)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/valid-parentheses/

## The problem in plain words

You get a string made only of the six bracket characters `()[]{}`. Say whether it
is "properly matched": every opening bracket is later closed by the *same kind* of
bracket, and they never cross. `{[]}` is fine; `([)]` is not, because the `(` and
`[` overlap instead of nesting.

## Why this matters

The fundamental operation is *tracking nested, last-opened-first-closed structure
with a stack* — the newest unfinished thing must finish before the older ones.
Once you see "properly nested," you're really asking whether a sequence of
open/close events is balanced.

This is the beating heart of parsing. Every compiler and interpreter uses a stack
to match braces, parentheses, and block scopes; a mismatched bracket is literally
this check failing. HTML/XML/JSON parsers verify tags and objects nest correctly
the same way. The call stack itself is this pattern — a function must return
before its caller does. Undo/redo, expression evaluation, and "unwind to the last
open context" in editors all lean on last-in-first-out order.

What you're solving for is a single O(n) pass instead of the O(n^2) repeated
collapse-and-rescan, by *remembering* the most recent unmatched opener rather than
re-searching for it each time. The stack makes "what must close next?" O(1).

## Start from the obvious

The naive idea is to keep collapsing matched pairs until nothing changes: scan for
an adjacent `()`, `[]`, or `{}`, delete it, and repeat. If you end with an empty
string it was valid.

```
while s contains "()" or "[]" or "{}":
    s = s with one such pair removed
return s == ""
```

That's correct — an innermost pair is always adjacent, so removing pairs peels the
nesting from the inside out. But each removal re-scans the whole string, and each
removal rebuilds it, so you're looking at `O(n^2)` work for something that should
take one pass.

## Find the waste

Look at what the collapse loop actually does: it keeps hunting for "the innermost
pair", which is just "the closing bracket sitting right after its own opener". The
opener that a closer must match is always the **most recently opened, still-open**
bracket. We keep re-searching the string to rediscover that, but we could just
*remember* it as we go.

"The most recent thing still open is the first thing that must close" is the
definition of a **stack** (last in, first out).

## The insight

Walk the string once, carrying a stack of openers we've seen but not yet closed:

1. On an **opening** bracket, push it.
2. On a **closing** bracket, the top of the stack must be its matching opener.
   - Stack empty? There's nothing to close — invalid.
   - Top is the wrong kind? Mismatch — invalid.
   - Otherwise pop it (that pair is now resolved) and continue.
3. At the end, the stack must be **empty**. Anything left is an opener that never
   got closed.

The stack top is always exactly the one bracket allowed to close next, so each
character is handled in `O(1)` and we never rescan.

## Complexity

- **Time:** `O(n)` — one pass; each push and pop is `O(1)`.
- **Space:** `O(n)` — worst case all openers, e.g. `"((((("`, sit on the stack.

## Pitfalls

- Forgetting the **final empty check**: `"("` reaches the end valid-so-far but has
  a leftover opener. `not stack` catches it.
- Popping an **empty stack**: a closer like `")"` with nothing open must return
  false, not crash. Check `not stack` before popping.
- Matching only by "is it a closer?" and not by **kind** — `"(]"` has a closer but
  the wrong opener on top.
- Order vs. count: `([)]` has balanced counts of each type but crosses, so counting
  alone is not enough; the stack enforces nesting order.

## Transfer

The move — "use a stack so the most recent open item is what you resolve first" —
drives a whole family:
[Min Stack / 155](../0155-min-stack/),
[Generate Parentheses / 22](../../08-backtracking/0022-generate-parentheses/) (the
validity rule here becomes the pruning rule there),
[Remove Invalid / 301], and any expression/nesting parser. Whenever "the newest
unfinished thing must finish before the older ones", reach for a stack.
