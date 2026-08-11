"""Full-arc linear trace for Last Stone Weight (1046).

Mirrors solution.py: the naive re-sort-every-round, why re-sorting the whole pile
each round is waste, then the max-heap (heaviest always on top) drawn as a sidebar
so you can watch the two heaviest get pulled, smashed, and any leftover pushed
back. Writes trace.json.
"""
import json
import os
import heapq

frames = []


def add(**f):
    frames.append(f)


NAIVE = [
    "while len(stones) > 1:",
    "    stones.sort()          # re-sort every round",
    "    y = stones.pop()       # heaviest",
    "    x = stones.pop()       # second heaviest",
    "    if y != x:",
    "        stones.append(y-x) # leftover",
]
FAST = [
    "heapq.heapify(heap)        # negated weights",
    "while len(heap) > 1:",
    "    y = -heapq.heappop(heap)   # heaviest",
    "    x = -heapq.heappop(heap)   # second",
    "    if y != x:",
    "        heapq.heappush(heap, -(y-x))",
]


def sidebar_heap(heap):
    """heap stores negated weights (min-heap faking a max-heap); show real weights desc."""
    body = sorted((-v for v in heap), reverse=True)
    rows = [[("top" if i == 0 else str(i)), str(v)] for i, v in enumerate(body)]
    if not rows:
        rows = [["", "(empty)"]]
    return {"title": "max-heap (heaviest on top)", "rows": rows}


stones0 = [2, 7, 4, 1, 8, 1]

# ---- Act 0: naive re-sort every round ----
pile = list(stones0)
add(act=0, cells=list(pile), code="naive", line=1,
    intro="every round sorts the WHOLE pile just to read the top two.",
    invariant="after each sort, the last two cells are the two heaviest.",
    note=f"Naive: pile {stones0}. To smash we need the two heaviest, so re-sort each round.",
    marks={str(i): "dim" for i in range(len(pile))},
    state=[["stones", len(pile)], ["sorts", 0]])

sorts = 0
while len(pile) > 1:
    pile.sort()
    sorts += 1
    y = pile[-1]
    x = pile[-2]
    add(act=0, cells=list(pile), code="naive", line=1,
        note=f"Sort → {pile}. Two heaviest: {y} and {x}.",
        marks={**{str(i): "dim" for i in range(len(pile))},
               str(len(pile) - 1): "active", str(len(pile) - 2): "active"},
        state=[["sorts", sorts], ["heaviest", y], ["second", x]])
    pile.pop()
    pile.pop()
    if y != x:
        pile.append(y - x)
        result_note = f"Smash {y} vs {x} → {y - x} back in the pile."
    else:
        result_note = f"Smash {y} vs {x} → equal, both gone."
    add(act=0, cells=list(pile) if pile else [], code="naive", line=5,
        note=result_note + f" Pile now {pile}.",
        marks={str(i): "dim" for i in range(len(pile))},
        state=[["after smash", str(pile)], ["stones left", len(pile)], ["sorts", sorts]])

final = pile[0] if pile else 0
add(act=0, code="naive", line=0,
    note=f"Last stone = {final}. But that cost {sorts} full sorts of a shrinking pile.",
    state=[["last stone", final], ["full sorts", sorts]],
    banner=f"last stone = {final}")

# ---- Act 1: the waste ----
add(act=1,
    intro="each round only needs the TWO largest — re-sorting the rest is waste.",
    note=f"{sorts} rounds, each an O(n log n) sort, but we only read the top two. "
         "The order of everything below is recomputed and thrown away.",
    state=[["rounds", sorts], ["per round", "O(n log n)"], ["read", "top 2"]])
add(act=1,
    note="A max-heap keeps the largest on top in O(1) and removes it in O(log n) — "
         "no re-sorting. n rounds → O(n log n) total.",
    state=[["heap top", "O(1)"], ["pop", "O(log n)"], ["total", "O(n log n)"]])

# ---- Act 2: fast max-heap ----
heap = [-w for w in stones0]
heapq.heapify(heap)
add(act=2, cells=list(stones0), code="fast", line=0,
    intro="the max-heap keeps the two heaviest reachable without any re-sort.",
    invariant="heap[0] (negated) is always the heaviest remaining stone.",
    note=f"Heapify {stones0} as a max-heap (store negated). Heaviest is always on top.",
    marks={str(i): "dim" for i in range(len(stones0))},
    sidebar=sidebar_heap(heap),
    state=[["stones", len(heap)], ["heaviest", -heap[0]]])

rounds = 0
while len(heap) > 1:
    rounds += 1
    y = -heapq.heappop(heap)
    x = -heapq.heappop(heap)
    add(act=2, code="fast", line=3,
        note=f"Round {rounds}: pop the two heaviest — {y} and {x} — straight off the top.",
        sidebar=sidebar_heap(heap),
        state=[["round", rounds], ["heaviest", y], ["second", x]])
    if y != x:
        heapq.heappush(heap, -(y - x))
        note = f"They differ: push leftover {y - x} back onto the heap."
    else:
        note = "They're equal: both destroyed, nothing pushed back."
    add(act=2, code="fast", line=5,
        note=note + f" {len(heap)} stone(s) left.",
        sidebar=sidebar_heap(heap),
        state=[["leftover", (y - x) if y != x else 0], ["stones left", len(heap)]])

final2 = -heap[0] if heap else 0
assert final2 == final, (final2, final)
add(act=2, code="fast", line=1,
    note=f"One stone remains: {final2}. No round ever re-sorted the pile.",
    sidebar=sidebar_heap(heap),
    state=[["last stone", final2], ["rounds", rounds]],
    banner=f"last stone = {final2}")

# ---- Act 3: edge case (equal pair annihilates) ----
edge = [2, 2]
heap3 = [-w for w in edge]
heapq.heapify(heap3)
add(act=3, cells=list(edge), code="fast", line=0,
    intro="two equal heaviest cancel completely — the heap can empty out to 0.",
    invariant="when y == x nothing is pushed back, so the heap can shrink to empty.",
    note="Edge: [2, 2]. The two heaviest are equal.",
    sidebar=sidebar_heap(heap3),
    state=[["stones", 2]])
y = -heapq.heappop(heap3)
x = -heapq.heappop(heap3)
add(act=3, code="fast", line=3,
    note=f"Pop both: {y} and {x}. Equal → both destroyed, nothing left.",
    sidebar=sidebar_heap(heap3),
    state=[["heaviest", y], ["second", x], ["stones left", len(heap3)]])
add(act=3, code="fast", line=1,
    note="Heap is empty, so the answer is 0.",
    sidebar=sidebar_heap(heap3),
    state=[["last stone", 0]], banner="last stone = 0")

trace = {
    "player": "linear",
    "title": "Last Stone Weight — the two heaviest, always on top",
    "acts": ["Naive: re-sort each round", "The waste", "Fast: max-heap", "Edge: equal pair"],
    "code": {"naive": NAIVE, "fast": FAST},
    "legend": [["active", "the two heaviest being smashed"], ["dim", "resting in the pile"],
               ["good", "the last stone"]],
    "cells": list(stones0),
    "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
