# 20. Valid Parentheses

**Pattern:** Stack (the newest open bracket must close first)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/valid-parentheses/

## The problem in plain words

You get a string made only of the six bracket characters `()[]{}`. Say whether it
is properly matched: every opening bracket is later closed by the *same kind*, and
they never cross. `{[]}` is fine; `([)]` is not, because the `(` and `[` overlap
instead of nesting.

```diagram
   {[]}   ok:   { opens, [ opens, ] closes the [, } closes the {   -> nested
   ([)]   bad:  ( opens, [ opens, ) tries to close ( but [ is still open -> crossed
```

## Why this matters

The one reusable idea is *tracking nested, last-opened-first-closed structure with
a stack* — the newest unfinished thing must finish before the older ones. Once you
see "properly nested," you're really asking whether a run of open/close events
stays balanced.

This is the core of parsing. Every compiler matches braces and block scopes with a
stack; a mismatched bracket is this exact check failing. HTML, XML, and JSON parsers
verify tags and objects the same way. The call stack itself is this pattern — a
function must return before its caller does.

What you're solving for is a single pass instead of repeated collapse-and-rescan, by
*remembering* the most recent unmatched opener instead of re-searching for it each
time. The stack makes "what must close next?" a one-step lookup.

## Start from the obvious

The naive idea: keep collapsing matched pairs until nothing changes. Scan for an
adjacent `()`, `[]`, or `{}`, delete it, repeat. End with an empty string and it was
valid.

```diagram
   {[]}  ->  {}   ->  ""      (remove [], then remove {})   -> valid
   ([)]  ->  (no adjacent pair to remove)  -> leftover -> invalid
```

Correct — an innermost pair is always adjacent, so removing pairs peels the nesting
from the inside out. But each removal re-scans and rebuilds the whole string, so it's
about n × n work for something that should take one pass.

## Find the waste

The collapse loop keeps hunting for "the innermost pair," which is just "a closer
sitting right after its own opener." The opener a closer must match is always the
**most recently opened, still-open** bracket. We keep re-scanning to rediscover
that — but we could just *remember* it as we go.

"The most recent thing still open is the first thing that must close" is the
definition of a **stack** (last in, first out).

## The insight

Walk the string once, carrying a stack of openers seen but not yet closed. On an
opener, push it. On a closer, the top of the stack must be its matching opener.

```diagram
   input: { [ ] }          stack grows DOWN, top is the last line
   read {  push {          stack: {
   read [  push [          stack: { [
   read ]  top is [ ? yes  pop     stack: {
   read }  top is { ? yes  pop     stack: (empty)
   end -> stack empty -> VALID

   input: ( ] 
   read (  push (          stack: (
   read ]  needs [ on top, top is ( -> MISMATCH -> invalid

   input: )
   read )  stack empty, nothing to close -> invalid

   input: (
   read (  push (          stack: (
   end -> stack NOT empty -> invalid (leftover opener)
```

The stack top is always exactly the one bracket allowed to close next, so each
character is handled in one step and nothing is rescanned.

## Complexity

- **Time: about n steps.** One pass; each push and pop is one step.
- **Extra memory: up to n.** Worst case all openers, e.g. `"((((("`, sit on the
  stack at once.

## Pitfalls

- Forgetting the **final empty check**: `"("` reaches the end valid-so-far but has a
  leftover opener. An empty stack at the end is the real pass.
- Popping an **empty stack**: a closer like `")"` with nothing open must return
  false, not crash. Check for empty before popping.
- Matching only by "is it a closer?" and not by **kind** — `"(]"` has a closer but
  the wrong opener on top.
- Order vs. count: `([)]` has balanced counts of each type but crosses, so counting
  alone is not enough; the stack enforces nesting order.

## Transfer

The move — "use a stack so the most recent open item is what you resolve first" —
drives a whole family: [Min Stack / 155](../../20-design/0155-min-stack/),
*Generate Parentheses / 22* (the validity rule here becomes the pruning rule
there), and any expression or nesting parser. Whenever the newest unfinished thing
must finish before the older ones, reach for a stack.
