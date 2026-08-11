# 621. Task Scheduler

**Pattern:** Greedy max-heap simulation (and a counting formula)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/task-scheduler/

## The problem in plain words

You have a list of tasks, each labeled by a letter, and a cooldown number `n`.
Each unit of time is one slot: you either run one task or sit idle. The rule: the
*same* task must have at least `n` other slots (running something else or idle)
before it can run again. Different tasks have no such restriction. Return the
smallest number of slots needed to run every task.

Example: `["A","A","A","B","B","B"]`, `n = 2` → `8`, one valid schedule being
`A B _ A B _ A B` (the underscores are forced idle slots).

## Why this matters

The deeper operation is *greedy scheduling under a spacing constraint*: you have a
resource that must rest between uses, many competing demands, and you want to
finish in the least time. The winning move is to always serve the most-pressing
demand first, because the item with the most work left is the one most likely to
create forced gaps if you leave it for later.

This is real scheduling. A CPU or thread pool spacing out retries of the same
failing job; a rate limiter that must leave a gap between calls to the same API
key; a manufacturing line where a machine needs cooldown between identical runs; a
message system enforcing per-recipient send intervals. The "most frequent thing
paces everything" insight is exactly how you reason about the bottleneck resource.

What the good solution buys is either an easy-to-trust simulation (`O(total time)`
with a heap) or, once you see *why* the most frequent task dominates, an `O(k)`
formula that computes the answer with no simulation at all — no time budget spent
walking every slot.

## Start from the obvious

The rule is stated slot by slot, so the honest first move is to *simulate* it. At
each slot, which task should you run? Greedy answer: run the task with the **most
copies left**. Burning down the most frequent task early keeps it from stranding
copies at the end that have nowhere to go but idle slots.

```
each slot:
    run the task with the most remaining copies (if any is off cooldown)
    put it on cooldown for n slots
    if nothing is available, idle
```

"The task with the most remaining" is a repeated *max* query over a changing
set — that's a max-heap. Tasks on cooldown wait in a queue tagged with the time
they're allowed back, and rejoin the heap when that time arrives.

## Find the waste

The simulation is correct and clear, but it *walks every slot*, including all the
idle ones, to arrive at a single number. If you watch it run, a pattern jumps out:
the whole schedule is paced entirely by the **most frequent task**. Everything
else just fills the gaps that task's cooldown creates.

So the real question is: *how many gaps does the most frequent task force, and do
the other tasks fill them?*

## The insight

Let `f_max` be the count of the most frequent task. Lay its copies out as anchors
with `n` empty slots between consecutive copies:

```
A . . . A . . . A          (f_max = 3, n = 3)
```

That skeleton is `(f_max - 1)` blocks of width `(n + 1)`, plus the final anchor:

```
frame = (f_max - 1) * (n + 1) + 1
```

If several tasks tie for `f_max`, each tie rides in the final column alongside the
last `A`, so add one per extra tied task:

```
frame = (f_max - 1) * (n + 1) + (number of tasks tied at f_max)
```

The remaining tasks drop into the dots. If there are so many other tasks that the
gaps overflow, there are **no idle slots at all** and the answer is just
`len(tasks)`. So take the larger of the two:

```
answer = max(len(tasks), frame)
```

Both the heap simulation and this formula are in `solution.py`, cross-checked
against each other on hundreds of random inputs.

## Complexity

- **Simulation:** `O(total slots)` time — it visits each slot once, and each slot
  does `O(log k)` heap work (`k` = number of distinct task labels ≤ 26). Space
  `O(k)` for the heap and wait queue.
- **Formula:** `O(m)` time to count `m` tasks, `O(k)` space for the counts, and
  `O(1)` arithmetic after that.

## Pitfalls

- **Max-heap in a min-heap language.** `heapq` is min-only; store **negated**
  counts so the most-remaining task is on top.
- **Cooldown bookkeeping.** A task just run can't rejoin the heap until `time + n`;
  releasing it too early (or off by one) breaks the spacing rule. Use a queue keyed
  by ready-time.
- **Idle slots still advance the clock.** When nothing is available but tasks
  remain, that slot counts toward the total.
- **The `max(len(tasks), frame)` guard.** With many distinct tasks the gaps fill
  and overflow — forgetting the guard *under*counts by ignoring that there are no
  idle slots. With `n = 0` the formula must reduce to `len(tasks)`, and it does.
- **Ties at the top.** Multiple tasks sharing `f_max` all sit in the final column;
  add one per tie, or you undercount the tail.

## Transfer

The move is: **serve the highest-demand item first via a max-heap when you must
simulate, but look for the counting shortcut once you see which item paces the
whole schedule.** The greedy-max-heap half is the same engine as
[Last Stone Weight / 1046](../1046-last-stone-weight/) and
[Reorganize String / 767](https://leetcode.com/problems/reorganize-string/) (space
out the most frequent character); the "derive a formula from the bottleneck" half
is the transferable insight for spacing and interval-packing problems. Whenever a
greedy simulation keeps re-picking the current maximum, reach for a heap — then ask
whether the answer has a closed form.
