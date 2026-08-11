"""Full-arc linear trace for Kth Largest Element in an Array (215).

Mirrors solution.py: the naive full sort, why ordering the other n-1 numbers is
waste, then the size-k MIN-heap (its top is the kth largest) drawn as a sidebar
so you can watch it fill to k and evict its smallest. Writes trace.json.
"""
import json
import os
import heapq

frames = []


def add(**f):
    frames.append(f)


NAIVE = [
    "return sorted(nums, reverse=True)[k-1]",
]
FAST = [
    "for x in nums:",
    "    heapq.heappush(heap, x)",
    "    if len(heap) > k:",
    "        heapq.heappop(heap)   # evict smallest",
    "return heap[0]                # kth largest",
]


def sidebar(heap):
    body = sorted(heap)
    rows = [[("top" if i == 0 else str(i)), str(v)] for i, v in enumerate(body)]
    if not rows:
        rows = [["", "(empty)"]]
    return {"title": "min-heap (size ≤ k)", "rows": rows}


nums = [3, 2, 1, 5, 6, 4]
K = 2  # answer = 5
ans = sorted(nums, reverse=True)[K - 1]

# ---- Act 0: naive full sort ----
add(act=0, cells=list(nums), code="naive", line=0,
    intro="the full sort orders ALL six numbers to read just one.",
    invariant="after sorting, index k-1 is the kth largest by definition.",
    note=f"Naive k={K}: sort {nums} descending, then read index k-1.",
    marks={str(i): "dim" for i in range(len(nums))},
    state=[["k", K], ["n", len(nums)], ["compares", "~n log n"]])
ordered = sorted(nums, reverse=True)
kth_pos = K - 1
add(act=0, cells=ordered, code="naive", line=0,
    note=f"Sorted desc → {ordered}. Index {kth_pos} = {ans}. Correct, but every other "
         f"number was ordered too — work the answer never reads.",
    marks={**{str(i): "dim" for i in range(len(ordered))}, str(kth_pos): "good"},
    state=[["sorted", str(ordered)], ["index k-1", kth_pos], ["answer", ans]],
    banner=f"kth largest = {ans}")

# ---- Act 1: the waste ----
add(act=1,
    intro="only the top k matter; the ordering of the rest is thrown away.",
    note="Sorting is O(n log n) and fully orders n numbers. We read one. The rank of "
         "the bottom n-k numbers among themselves is pure waste.",
    state=[["cost", "O(n log n)"], ["needed", f"top {K}"], ["kth is", "smallest of top k"]])
add(act=1,
    note="Key idea: the kth largest is the SMALLEST of the top k. Keep only k numbers "
         "in a min-heap — its top is the answer. One pass, O(n log k).",
    state=[["keep", f"top {K}"], ["per push", "O(log k)"], ["total", "O(n log k)"]])

# ---- Act 2: fast size-k min-heap ----
heap = []
add(act=2, cells=list(nums), code="fast", line=0,
    intro="the heap FILLS to k, then each new number either joins or is rejected.",
    invariant=f"the heap holds the {K} largest numbers seen so far; heap[0] is their smallest.",
    note=f"Sweep {nums} once. Push each; whenever the heap exceeds {K}, evict its smallest.",
    marks={str(i): "dim" for i in range(len(nums))},
    sidebar=sidebar(heap),
    state=[["k", K], ["heap size", 0]])

for i, x in enumerate(nums):
    heapq.heappush(heap, x)
    over = len(heap) > K
    add(act=2, code="fast", line=1,
        pointers={"x": i},
        marks={str(i): "active"},
        note=f"x = {x} (index {i}): push it. Heap size {len(heap)}"
             + (" — over k, trim next." if over else "."),
        sidebar=sidebar(heap),
        state=[["x", x], ["heap size", len(heap)], ["over k?", "yes" if over else "no"]])
    if over:
        dropped = heapq.heappop(heap)
        add(act=2, code="fast", line=3,
            pointers={"x": i},
            marks={str(i): "dim"},
            note=f"Evict the smallest keeper ({dropped}) — it's outside the top {K}. "
                 f"Heap top now {heap[0]}.",
            sidebar=sidebar(heap),
            state=[["evicted", dropped], ["heap size", len(heap)], ["heap top", heap[0]]])

assert heap[0] == ans, (heap[0], ans)
add(act=2, code="fast", line=4,
    note=f"Pass done. heap holds the top {K} = {sorted(heap, reverse=True)}. "
         f"heap[0] = {ans} is the kth largest.",
    marks={str(i): "dim" for i in range(len(nums))},
    sidebar=sidebar(heap),
    state=[["heap top", heap[0]], ["answer", ans]],
    banner=f"kth largest = {ans}   (never fully sorted)")

# ---- Act 3: edge case (all duplicates) ----
edge = [2, 2, 2, 2]
K2 = 3  # kth largest of all-2s is 2
heap2 = []
add(act=3, cells=list(edge), code="fast", line=0,
    intro="duplicates count as distinct positions — the kth largest can equal the max.",
    invariant="equal values still fill k slots; heap[0] stays the smallest kept.",
    note=f"Edge: {edge}, k={K2}. All equal, so the 3rd largest is still 2.",
    marks={str(i): "dim" for i in range(len(edge))},
    sidebar=sidebar(heap2),
    state=[["k", K2], ["heap size", 0]])
for i, x in enumerate(edge):
    heapq.heappush(heap2, x)
    dropped = None
    if len(heap2) > K2:
        dropped = heapq.heappop(heap2)
    note = f"x = {x}: push. "
    if dropped is not None:
        note += f"Over k, evict {dropped}. "
    note += f"Heap top = {heap2[0]}."
    add(act=3, code="fast", line=1,
        pointers={"x": i}, marks={str(i): "active"},
        note=note, sidebar=sidebar(heap2),
        state=[["x", x], ["heap size", len(heap2)], ["heap top", heap2[0]]])
assert heap2[0] == 2
add(act=3, code="fast", line=4,
    note="All four 2s tried; three fill the heap. 3rd largest = 2.",
    sidebar=sidebar(heap2), marks={str(i): "dim" for i in range(len(edge))},
    state=[["answer", 2]], banner="kth largest = 2")

trace = {
    "player": "linear",
    "title": "Kth Largest in an Array — keep only the k biggest",
    "acts": ["Naive: full sort", "The waste", "Fast: size-k min-heap", "Edge: all duplicates"],
    "code": {"naive": NAIVE, "fast": FAST},
    "legend": [["active", "number being pushed"], ["good", "the kth-largest answer"],
               ["dim", "ordered-then-discarded / seeded"]],
    "cells": list(nums),
    "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
