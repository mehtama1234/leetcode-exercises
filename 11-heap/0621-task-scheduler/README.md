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

```diagram
   tasks = A A A B B B,  n = 2

   one valid schedule:
   slot:  1  2  3  4  5  6  7  8
   task:  A  B  _  A  B  _  A  B      (_ = forced idle)
                 ^        ^
                 A must wait 2 slots between runs

   answer = 8 slots
```

## Why this matters

The real operation is *greedy scheduling under a spacing constraint*: you have a
resource that must rest between uses, many competing demands, and you want to
finish in the least time. The winning move is to always serve the most-pressing
demand first, because the item with the most work left is the one most likely to
create forced gaps if you leave it for later.

This is real scheduling. A CPU spacing out retries of the same failing job; a rate
limiter that must leave a gap between calls to the same API key; a manufacturing
line where a machine needs cooldown between identical runs. The "most frequent
thing paces everything" insight is how you reason about the bottleneck resource.

What you buy is either an easy-to-trust simulation (walk every slot with a heap)
or, once you see *why* the most frequent task dominates, a formula that computes
the answer with no simulation at all.

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

"The task with the most remaining" is a repeated *max* query over a changing set —
that's a max-heap. Tasks on cooldown wait in a queue tagged with the time they're
allowed back, and rejoin the heap when that time arrives.

```diagram
   tasks A:3 B:3, n=2. max-heap keyed by copies-left, most on top.

   t=1: heap{A3,B3} run A -> A2 cools until t=4    | out: A
   t=2: heap{B3}    run B -> B2 cools until t=5    | out: A B
   t=3: heap{}      nothing off cooldown -> idle   | out: A B _
   t=4: A2 returns. run A -> A1 cools until t=7    | out: A B _ A
   t=5: B2 returns. run B -> B1 cools until t=8    | out: A B _ A B
   t=6: idle ; t=7: run A ; t=8: run B             | out: A B _ A B _ A B
   -> 8 slots
```

## Find the waste

The simulation is correct and clear, but it *walks every slot*, including all the
idle ones, to arrive at a single number. Watch it run and a pattern jumps out: the
whole schedule is paced by the **most frequent task**. Everything else just fills
the gaps that task's cooldown creates.

So the real question is: *how many gaps does the most frequent task force, and do
the other tasks fill them?*

## The insight

Let `f_max` be the count of the most frequent task. Lay its copies out as anchors
with `n` empty slots between consecutive copies:

```diagram
   f_max = 3, n = 3:

   A . . . A . . . A
   |<-block->|<-block->|A|
   two blocks of width (n+1)=4, plus the final A

   frame = (f_max - 1) * (n + 1) + 1
         =    (3 - 1)  *  (3 + 1) + 1  =  9
```

If several tasks tie for `f_max`, each tie rides in the final column alongside the
last `A`, so add one per tied task:

```diagram
   A A B B tied at f_max=2, n=2:

   A B . A B          <- A and B both anchor
   frame = (2-1)*(2+1) + (2 tied) = 3 + 2 = 5
   but len(tasks)=4, and gaps here actually fill... take the max (below)
```

The remaining tasks drop into the dots. If there are so many other tasks that the
gaps overflow, there are **no idle slots at all** and the answer is just the number
of tasks. So take the larger of the two:

```
answer = max(len(tasks), frame)
```

Both the heap simulation and this formula are in `solution.py`, cross-checked
against each other on hundreds of random inputs.

## Complexity

- **Simulation:** about `total slots` time — it visits each slot once, each slot
  doing `log k` heap work (`k` = number of distinct labels, at most 26). Space
  `k` for the heap and wait queue.
- **Formula:** about `m` time to count `m` tasks, `k` space for the counts, and
  constant arithmetic after that.

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
  idle slots. With `n = 0` the formula must reduce to the number of tasks, and it
  does.
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
