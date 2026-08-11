"""621. Task Scheduler — https://leetcode.com/problems/task-scheduler/

Given task labels and a cooldown n, the same task must be at least n slots apart.
Each slot runs one task or is idle. Return the minimum number of slots to finish.

Two approaches are kept side by side: a greedy max-heap simulation that shows the
mechanism tick by tick, and an O(1) counting formula that computes the answer
directly. Both agree; the formula is derived from what the simulation reveals.
"""
from typing import List
from collections import Counter, deque
import heapq


def least_interval(tasks: List[str], n: int) -> int:
    """Greedy simulation with a max-heap. O(total time) per tick, O(k) heap.

    Insight: at each moment, run the task with the most copies remaining — using
    up the most frequent task early is what prevents it from bottlenecking the end.
    A max-heap gives that "most remaining" task in O(log k).

    The cooldown means a task we just ran can't return for n more slots, so we park
    it in a waiting queue with the time it becomes available, and push it back onto
    the heap when its cooldown expires. We advance the clock one slot at a time; if
    the heap is empty but tasks are still waiting, that slot is an idle tick.

    Python's heapq is a MIN-heap, so we store NEGATED counts (most-remaining on top).
    """
    if not tasks:
        return 0
    counts = Counter(tasks)
    heap = [-c for c in counts.values()]      # negate for max-heap
    heapq.heapify(heap)
    wait: deque[tuple[int, int]] = deque()    # (ready_time, negated remaining count)

    time = 0
    while heap or wait:
        time += 1
        if heap:
            remaining = heapq.heappop(heap) + 1   # run one copy (count is negative)
            if remaining < 0:                     # still copies left -> cool it down
                wait.append((time + n, remaining))
        # (if heap was empty, this slot is idle — nothing to run yet)
        # release any task whose cooldown just expired
        if wait and wait[0][0] == time:
            heapq.heappush(heap, wait.popleft()[1])
    return time


def least_interval_formula(tasks: List[str], n: int) -> int:
    """O(k) counting formula — the answer without simulating.

    The schedule is paced by the most frequent task. Say it appears `f_max` times.
    Lay those copies out as anchors with n gaps between them:

        A . . . A . . . A            (here f_max = 3, n = 3)

    That skeleton spans (f_max - 1) blocks of size (n + 1), then one final A:

        frame = (f_max - 1) * (n + 1) + 1

    Other tasks slot into the gaps (the dots). If several tasks tie at f_max, each
    tie adds one more task to the final column, so add (number of tasks with count
    == f_max) - 1... i.e. `+ max_count_ties`. The gaps might all fill up and even
    overflow, in which case there are no idle slots at all and the answer is simply
    len(tasks). So the answer is the LARGER of the frame and len(tasks):

        answer = max(len(tasks), frame + (ties - 1))
    """
    if not tasks:
        return 0
    counts = Counter(tasks)
    f_max = max(counts.values())
    ties = sum(1 for c in counts.values() if c == f_max)   # tasks tied at the max
    frame = (f_max - 1) * (n + 1) + ties
    return max(len(tasks), frame)


def _test() -> None:
    # Official LeetCode examples:
    #   ["A","A","A","B","B","B"], n=2 -> 8   (A B idle A B idle A B)
    #   ["A","A","A","B","B","B"], n=0 -> 6   (no cooldown -> just run them)
    #   ["A","A","A","A","A","A","B","C","D","E","F","G"], n=2 -> 16
    cases = [
        (["A", "A", "A", "B", "B", "B"], 2, 8),
        (["A", "A", "A", "B", "B", "B"], 0, 6),
        (list("AAAAAABCDEFG"), 2, 16),
        (["A"], 0, 1),                                  # single task
        (["A", "B", "C"], 2, 3),                        # all distinct, gaps fill
        (["A", "A"], 3, 5),                             # A idle idle idle A
    ]
    for tasks, n, expected in cases:
        assert least_interval(tasks, n) == expected, (tasks, n)
        assert least_interval_formula(tasks, n) == expected, (tasks, n)

    # Cross-check the simulation and formula agree on many random inputs.
    import random
    rng = random.Random(0)
    for _ in range(500):
        k = rng.randint(1, 6)
        labels = [chr(ord("A") + i) for i in range(k)]
        tasks = [rng.choice(labels) for _ in range(rng.randint(1, 20))]
        n = rng.randint(0, 5)
        assert least_interval(tasks, n) == least_interval_formula(tasks, n), (tasks, n)

    print("task_scheduler: all cases passed")


if __name__ == "__main__":
    _test()
