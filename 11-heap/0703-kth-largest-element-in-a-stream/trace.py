"""Full-arc linear trace for Kth Largest Element in a Stream (703).

Mirrors solution.py: the naive re-sort-every-add, why that's wasteful, then the
size-k MIN-heap whose top is the kth largest. The heap is drawn as a sidebar so
you can watch it fill to k and then evict its smallest on every add. Writes
trace.json.
"""
import json
import os
import heapq

frames = []


def add(**f):
    frames.append(f)


NAIVE = [
    "self._nums.append(val)",
    "return sorted(self._nums, reverse=True)[k-1]",
]
FAST = [
    "heapq.heappush(heap, val)",
    "if len(heap) > k:",
    "    heapq.heappop(heap)   # drop smallest",
    "return heap[0]            # kth largest",
]


def sidebar(heap, note_top=True):
    """Show the min-heap sorted for reading; smallest (the answer) on top."""
    body = sorted(heap)
    rows = [[("top" if (i == 0 and note_top) else str(i)), str(v)]
            for i, v in enumerate(body)]
    if not rows:
        rows = [["", "(empty)"]]
    return {"title": "min-heap (size ≤ k)", "rows": rows}


K = 3
start = [4, 5, 8, 2]
# stream of adds and the expected kth-largest after each (from solution._test)
stream = [(3, 4), (5, 5), (10, 5), (9, 8), (4, 8)]

# ---- Act 0: naive re-sort every add ----
history = list(start)
add(act=0, cells=list(history), code="naive", line=0,
    intro="every add re-sorts the ENTIRE history just to read one value.",
    invariant="_nums holds every number ever seen, in arrival order.",
    note=f"Naive k={K}: start with {start}. To answer, sort all of it and take index k-1.",
    marks={str(i): "dim" for i in range(len(history))},
    state=[["k", K], ["stored", len(history)], ["sorts", 0]])

sorts = 0
for val, ans in stream:
    history.append(val)
    sorts += 1
    ordered = sorted(history, reverse=True)
    kth_idx = ordered.index(ans)  # position of the answer in the descending order
    add(act=0, cells=list(history), code="naive", line=1,
        note=f"add({val}): now {len(history)} numbers. Sort desc → {ordered}. "
             f"kth largest = index {K-1} = {ans}.",
        marks={str(len(history) - 1): "active"},
        state=[["added", val], ["stored", len(history)], ["answer", ans], ["sorts", sorts]],
        banner=f"add({val}) → {ans}")

add(act=0, code="naive", line=1,
    note=f"5 adds cost 5 full sorts of a growing list — and we only ever read one value.",
    state=[["adds", 5], ["full sorts", sorts], ["values read", 5]])

# ---- Act 1: the waste ----
add(act=1,
    intro="how much order we compute and throw away.",
    note="Each add sorts all n numbers (O(n log n)) but reads only rank k. "
         "The order among every other number is pure waste.",
    state=[["per add", "O(n log n)"], ["needed", "the k biggest"], ["kth is", "smallest of top k"]])
add(act=1,
    note="Key idea: the kth largest is the SMALLEST of the top k. So keep only the "
         "k biggest in a min-heap — its top is the answer, read in O(1).",
    state=[["keep", f"top {K} only"], ["read answer", "O(1)"], ["per add", "O(log k)"]])

# ---- Act 2: fast size-k min-heap ----
heap = list(start)
heapq.heapify(heap)
while len(heap) > K:
    heapq.heappop(heap)

add(act=2, cells=list(start), code="fast", line=3,
    intro="the heap FILLS to k, then every add pushes one and pops the smallest.",
    invariant=f"the heap holds exactly the {K} largest seen; heap[0] is the kth largest.",
    note=f"Seed {start}, trimmed to the top {K}. heap[0] = {heap[0]} is already the kth largest.",
    marks={str(i): "dim" for i in range(len(start))},
    sidebar=sidebar(heap),
    state=[["k", K], ["heap size", len(heap)], ["kth largest", heap[0]]])

for val, ans in stream:
    heapq.heappush(heap, val)
    over = len(heap) > K
    add(act=2, code="fast", line=0,
        note=f"add({val}): push it. Heap now holds {len(heap)} "
             + ("— one over k, so trim." if over else "(still ≤ k)."),
        sidebar=sidebar(heap),
        state=[["added", val], ["heap size", len(heap)], ["over k?", "yes" if over else "no"]])
    if over:
        dropped = heapq.heappop(heap)
        add(act=2, code="fast", line=2,
            note=f"Pop the smallest ({dropped}) — it can't be in the top {K}. "
                 f"heap[0] = {heap[0]} is the kth largest.",
            sidebar=sidebar(heap),
            state=[["evicted", dropped], ["heap size", len(heap)], ["kth largest", heap[0]]])
    assert heap[0] == ans, (val, heap[0], ans)
    add(act=2, code="fast", line=3,
        note=f"Answer for add({val}) = heap[0] = {ans}. One push, at most one pop — O(log k).",
        sidebar=sidebar(heap),
        state=[["answer", ans], ["heap size", len(heap)]],
        banner=f"add({val}) → {ans}   (no full sort)")

# ---- Act 3: edge case (k = 1, empty start) ----
K2 = 1
heap2 = []
edge_stream = [(-1, -1), (-2, -1), (0, 0)]
add(act=3, cells=[], code="fast", line=3,
    intro="k=1 means the heap holds a single number — the running maximum.",
    invariant="with k=1 the heap has one slot; heap[0] is the largest seen so far.",
    note="Edge: k=1, empty start. The kth (1st) largest is just the maximum so far.",
    sidebar=sidebar(heap2),
    state=[["k", K2], ["heap size", 0]])
for val, ans in edge_stream:
    heapq.heappush(heap2, val)
    dropped = None
    if len(heap2) > K2:
        dropped = heapq.heappop(heap2)
    assert heap2[0] == ans, (val, heap2[0], ans)
    note = f"add({val}): push. "
    if dropped is not None:
        note += f"Over k=1, drop smaller {dropped}. "
    note += f"Max so far = {ans}."
    add(act=3, code="fast", line=3, note=note,
        sidebar=sidebar(heap2),
        state=[["added", val], ["heap size", len(heap2)], ["answer (max)", ans]],
        banner=f"add({val}) → {ans}")

trace = {
    "player": "linear",
    "title": "Kth Largest in a Stream — keep only the k biggest",
    "acts": ["Naive: re-sort every add", "The waste", "Fast: size-k min-heap", "Edge: k = 1"],
    "code": {"naive": NAIVE, "fast": FAST},
    "legend": [["active", "the number just added"], ["dim", "seeded / filed away"],
               ["good", "the kth-largest answer"]],
    "cells": list(start),
    "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
