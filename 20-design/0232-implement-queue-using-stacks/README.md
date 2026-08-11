# 232. Implement Queue using Stacks

**Pattern:** Compose one structure from another + spread-out cost
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/implement-queue-using-stacks/

## The problem in plain words

You may only use stacks — where the last thing in is the first thing out (LIFO).
Build a queue on top of them: first in, first out (FIFO), with `push`, `pop`
(remove front), `peek` (look at front), and `empty`. Each operation should cost a
small fixed amount *on average*.

```diagram
   A stack hands back the newest first:
       push 1, 2, 3   ->   [ 1, 2, 3 ]   pop gives 3   (wrong for a queue)

   A queue must hand back the oldest first:
       push 1, 2, 3   ->   pop should give 1
```

## Why this matters

The real skill is **building the tool you need out of the tool you're handed**, and
reasoning about *spread-out cost* — where one occasional expensive step is fine
because it pays for many cheap ones that follow.

Both ideas run through real systems. Language runtimes build higher-level control
flow on a raw call stack. Growable arrays (Python's `list`, Go's slices, Java's
`ArrayList`) give a fast append on average even though a resize copies everything —
the exact accounting used here. Log-structured storage and batching layers gather
writes and flush in bulk: cheap to enqueue, occasionally expensive to drain.

What the good solution buys is turning a worst-case full-pass operation into a
fixed cost *on average* by promising each element is moved at most once. You spend
a burst of work rarely, and in return every element's total lifetime cost stays
small — which is what keeps throughput steady under load.

## Start from the obvious

Use two stacks and reverse on every read: to pop the front, pour everything into a
second stack, take the bottom, and pour it back.

```diagram
   s_in = [1, 2, 3]           (3 on top)

   pop front:
     pour s_in -> tmp   =>   tmp = [3, 2, 1]   (1 on top now)
     front = tmp.pop()  =>   1
     pour tmp -> s_in   =>   s_in = [1, 2, 3]  again
                             ^ moved everything twice for one pop
```

Correct, but every single `pop`/`peek` shuffles the whole queue twice — a full
pass per call. We keep reversing back and forth for nothing.

## Find the waste

The pour-back is pure waste. Once elements sit in arrival order on the second
stack, *leave them there*. Later pops take from its top directly. You only need to
refill it when it runs dry.

## The insight

Keep two stacks with distinct jobs:

- `s_in` — where new elements land (`push` is a single step).
- `s_out` — where elements are served from.

When you need the front and `s_out` is **empty**, pour all of `s_in` into `s_out`
once. A stack reverses order, so pouring the already-reversed `s_in` lands the
*oldest* element on top of `s_out` — exactly the queue front. Then serve from
`s_out` until it drains again.

```diagram
   push 1,2,3:   s_in = [1,2,3]      s_out = []

   pop (s_out empty -> pour once):
       s_in = []                     s_out = [3,2,1]   (1 on top = front)
       pop -> 1                      s_out = [3,2]

   push 4:       s_in = [4]          s_out = [3,2]
   pop -> 2                          s_out = [3]       (no pour needed)
   pop -> 3                          s_out = []
   pop (empty -> pour): s_in=[] s_out=[4], pop -> 4
```

Each element is pushed to `s_in` once, moved to `s_out` once, and popped once:
three fixed steps over its whole life. A single `pop` that triggers a transfer
looks like a full pass, but that cost is split across all the elements it moved.

## Complexity

- **Time: a fixed cost per operation on average.** `push` is always one step. A
  transfer is proportional to how many elements it moves, but it only fires when
  `s_out` is empty and moves each element exactly once — so averaged over all
  operations, each is a fixed cost.
- **Space: about n.** The elements live in one of the two stacks.

## Pitfalls

- Transferring when `s_out` is **not** empty. That interleaves old and new elements
  and breaks FIFO order — only pour when `s_out` is drained.
- Reporting `empty` by checking just one stack. It's empty only when **both** are.
- Claiming a fixed *worst-case* cost. It's fixed *on average*; one unlucky `pop`
  does a full pass.

## Transfer

The "compose a structure from a humbler one" idea has a mirror image:
[Implement Stack using Queues / 225](https://leetcode.com/problems/implement-stack-using-queues/).
The spread-out-cost reasoning reappears in
[Min Stack / 155](../0155-min-stack/) and in any growable-array append analysis.
When one operation is occasionally expensive, ask "does each element pay that cost
at most once?" — if so, the average cost stays small.
