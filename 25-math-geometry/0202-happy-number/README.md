# 202. Happy Number

**Pattern:** Cycle detection (a sequence that either terminates or loops)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/happy-number/

## The problem in plain words

Take a number. Replace it with the sum of the squares of its digits. Repeat. If
you ever land on `1`, the number is "happy". If instead you keep going around
the same handful of numbers forever, it's not. Return true or false.

Example: `19 → 1²+9² = 82 → 8²+2² = 68 → 6²+8² = 100 → 1²+0²+0² = 1`. Happy.

## Why this matters

Underneath the puzzle is a question that comes up constantly: *I'm following a
chain of states one step at a time — how do I know when I'm stuck in a loop
versus making progress?* The chain has no obvious length; the only way to know
it's cyclic is to detect that you've returned somewhere you've been.

That exact move runs real systems. Detecting infinite loops in a state machine
or a config-resolution graph (does "environment A extends B extends A" cycle?)
is this problem. Following a linked list and asking "is it corrupted into a
loop?" is the identical algorithm. Garbage collectors and dependency resolvers
must spot reference cycles. Even hash functions are studied for their cycle
structure the same way.

What the good solution buys is **constant memory**. The naive fix remembers
every state it has seen; Floyd's two-pointer trick detects the loop while
storing only two numbers — which matters when the chain is long or you're
detecting cycles in a stream you can't afford to buffer.

## Start from the obvious

A number is *not* happy exactly when the process repeats a value it has already
produced (it's going in circles). So remember everything you've seen:

```
seen = set()
while n != 1 and n not in seen:
    seen.add(n)
    n = square_digit_sum(n)
return n == 1
```

Why does this even terminate? Because `square_digit_sum` can't grow without
bound: a 3-digit number maxes out at `9²·3 = 243`, so after a step or two every
value is under ~810. In that bounded range the sequence *must* eventually repeat
or hit 1. Correct and honest — but it stores a set.

## Find the waste

The set is only there to answer one yes/no question: "have I looped?" We're
paying `O(k)` memory to detect a property — the existence of a cycle — that
doesn't actually require remembering the values, only noticing that a fast
traveler catches up to a slow one.

## The insight

Floyd's tortoise and hare. Run two positions through the same sequence:

- `slow` takes one step per round: `n → f(n) → f(f(n)) → ...`
- `fast` takes two steps per round.

If the sequence reaches `1`, `fast` gets there first and we answer happy. If the
sequence is a loop, `fast` goes around twice as fast and eventually meets `slow`
*inside* the loop — a meeting proves a cycle, so we answer not happy. No set
needed.

```
slow, fast = n, f(n)
while fast != 1 and slow != fast:
    slow = f(slow)
    fast = f(f(fast))
return fast == 1
```

## Complexity

- **Time:** `O(log n)` to add up the digit-squares the first time (a number has
  `~log10(n)` digits), then a bounded number of steps because the sequence falls
  into the range under ~810 almost immediately. Effectively constant iterations.
- **Space:** `O(1)` for the two-pointer version — just `slow` and `fast`. The
  set version is `O(k)` where `k` is the number of distinct values seen.

## Pitfalls

- **`0` is not happy** — it maps to itself forever, never reaching 1.
- Forgetting to advance `slow` and `fast` at *different* speeds — equal speeds
  never meet inside a loop, so the loop never terminates.
- Recomputing `square_digit_sum` incorrectly (e.g. summing digits instead of
  their squares).
- Assuming it could run forever — it can't; the bounded range guarantees a
  cycle or a 1.

## Transfer

The tortoise-and-hare cycle detection is the reusable core. It's the standard
way to find a loop in a
[Linked List Cycle / 141](https://leetcode.com/problems/linked-list-cycle/),
locate the loop's entry in
[Linked List Cycle II / 142](https://leetcode.com/problems/linked-list-cycle-ii/),
and spot the duplicate in
[Find the Duplicate Number / 287](https://leetcode.com/problems/find-the-duplicate-number/),
where the array is read as a "next pointer" just like `square_digit_sum` is here.
