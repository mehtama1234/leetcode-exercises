# 232. Implement Queue using Stacks

**Pattern:** Compose one structure from another + amortized analysis
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/implement-queue-using-stacks/

## The problem in plain words

You can only use stacks — structures where the last thing in is the first thing
out (LIFO). Build a queue on top of them: first in, first out (FIFO), with
`push`, `pop` (remove front), `peek` (look at front), and `empty`. Each
operation should be O(1) on average.

## Why this matters

The real skill here is **building the abstraction you need out of the primitive
you're given**, and reasoning about *amortized* cost — where an occasional
expensive step is fine because it pays for many cheap ones.

Both ideas are everywhere in real systems. Language runtimes and interpreters
implement higher-level control flow using a raw call stack. Dynamic arrays
(Python's `list`, Go's slices, Java's `ArrayList`) give O(1) *amortized* append
even though a resize copies everything — the exact accounting used here. Log-
structured storage and batching layers gather writes and flush in bulk: cheap
enqueue, occasional expensive drain.

What the good solution buys is turning a worst-case-O(n) operation into O(1)
**amortized** by guaranteeing each element is moved at most once. You spend a
burst of work rarely, and in exchange every element's *total* lifetime cost is
constant — which is what keeps throughput predictable under load.

## Start from the obvious

Use two stacks and reverse on every operation: to pop the front, pour everything
into a second stack, take the bottom, and pour it back.

```
pop():
    move all of s_in -> tmp        # reverses order
    front = tmp.pop()
    move all of tmp -> s_in        # reverses back
    return front
```

Correct, but every single `pop`/`peek` moves the whole queue twice — O(n) per
call. We're reversing back and forth over and over.

## Find the waste

The pour-back is pure waste. Once elements are in arrival order on the second
stack, *leave them there*. Future pops can just take from its top directly. We
only need to refill it when it runs dry.

## The insight

Keep two stacks with distinct jobs:

- `s_in` — where new elements land (`push` = O(1)).
- `s_out` — where elements are served from.

When you need the front and `s_out` is **empty**, pour all of `s_in` into
`s_out` once. A stack reverses order, so pouring the reversed `s_in` makes the
*oldest* element land on top of `s_out` — exactly the queue front. Then serve
from `s_out` until it empties again.

Each element is pushed to `s_in` once, transferred to `s_out` once, and popped
once: three constant steps over its whole life. A single `pop` that triggers a
transfer looks O(n), but that cost is spread across all the elements it moved.

## Complexity

- **Time:** `O(1)` amortized for every operation. `push` is always O(1). A
  transfer is O(k), but it only happens when `s_out` is empty, and it moves each
  element exactly once — so averaged over all operations, each is O(1).
- **Space:** `O(n)` — the elements live in one of the two stacks.

## Pitfalls

- Transferring when `s_out` is **not** empty. That interleaves old and new
  elements and breaks FIFO order — only pour when `s_out` is drained.
- Reporting `empty` by checking just one stack. It's empty only when **both** are.
- Claiming O(1) *worst case*. It's O(1) *amortized*; one unlucky `pop` is O(n).

## Transfer

The "compose a structure from a humbler one" idea has a mirror image:
[Implement Stack using Queues / 225](https://leetcode.com/problems/implement-stack-using-queues/).
The amortized-cost reasoning reappears in
[Min Stack / 155](../0155-min-stack/) and in any dynamic-array append analysis.
When one operation is occasionally expensive, ask "does each element pay that
cost at most once?" — if so, it's amortized O(1).
