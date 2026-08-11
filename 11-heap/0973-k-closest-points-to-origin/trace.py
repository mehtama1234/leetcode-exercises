"""Full-arc linear trace for K Closest Points to Origin (973).

Mirrors solution.py: naive sort-all-by-distance, why ordering the far points is
waste, then a size-k MAX-heap that watches the FARTHEST current keeper and swaps
a nearer point in. The input row is the points; the heap of the k nearest so far
is drawn as a sidebar. Distance shown is squared (x*x + y*y), as in the code.
Writes trace.json.
"""
import json
import os
import heapq

frames = []


def add(**f):
    frames.append(f)


NAIVE = [
    "return sorted(points,",
    "   key=lambda p: p[0]**2 + p[1]**2)[:k]",
]
FAST = [
    "for p in points:",
    "    d2 = p[0]**2 + p[1]**2",
    "    heapq.heappush(heap, (-d2, p))",
    "    if len(heap) > k:",
    "        heapq.heappop(heap)   # drop farthest",
    "return [p for _, p in heap]",
]

points = [[3, 3], [5, -1], [-2, 4], [1, 3], [-2, 2]]
K = 2


def d2(p):
    return p[0] * p[0] + p[1] * p[1]


def label(p):
    return f"({p[0]},{p[1]})"


cells = [label(p) for p in points]


def sidebar_heap(heap):
    """heap holds (-d2, p); show kept points with real squared distance, nearest first."""
    kept = sorted(((-nd, p) for nd, p in heap))  # by real d2 ascending
    rows = [[label(p), f"d²={dd}"] for dd, p in kept]
    if not rows:
        rows = [["", "(empty)"]]
    # mark the farthest keeper (heap top) so the eviction target is visible
    if kept:
        rows[-1][0] += "  ← farthest"
    return {"title": "k nearest so far (max-heap top = farthest)", "rows": rows}


# ---- Act 0: naive sort-all ----
add(act=0, cells=list(cells), code="naive", line=0,
    intro="the sort orders ALL points by distance, then keeps only the first k.",
    invariant="after sorting by d², the first k entries are the k nearest.",
    note=f"Naive k={K}: compute each point's squared distance and sort them all.",
    labels=[d2(p) for p in points],
    marks={str(i): "dim" for i in range(len(points))},
    state=[["k", K], ["n", len(points)], ["cost", "O(n log n)"]])

order = sorted(range(len(points)), key=lambda i: d2(points[i]))
ordered_cells = [cells[i] for i in order]
ordered_d = [d2(points[i]) for i in order]
marks = {str(i): ("good" if i < K else "dim") for i in range(len(order))}
add(act=0, cells=ordered_cells, labels=ordered_d, code="naive", line=1,
    note=f"Sorted by d² → {ordered_d}. The first {K} are nearest: "
         f"{[ordered_cells[i] for i in range(K)]}. The rest were ordered for nothing.",
    marks=marks,
    state=[["nearest", str([ordered_cells[i] for i in range(K)])], ["kept", K], ["ordered", len(points)]],
    banner=f"{K} nearest = {[ordered_cells[i] for i in range(K)]}")

# ---- Act 1: the waste ----
add(act=1,
    intro="only the k nearest matter; ordering the far points is discarded work.",
    note="Sorting is O(n log n) and ranks every point. We keep k. The full order of the "
         "far points is computed then thrown away.",
    state=[["cost", "O(n log n)"], ["kept", f"{K}"], ["discarded order", f"{len(points) - K} pts"]])
add(act=1,
    note="To keep the k NEAREST, watch the FARTHEST of the ones you're keeping. That "
         "farthest is the top of a size-k max-heap. If a new point beats it, swap.",
    state=[["watch", "farthest keeper"], ["structure", "size-k max-heap"], ["total", "O(n log k)"]])

# ---- Act 2: fast size-k max-heap ----
heap = []
add(act=2, cells=list(cells), code="fast", line=0,
    intro="the heap FILLS to k, then each point challenges the farthest keeper.",
    invariant=f"the heap holds the {K} nearest points seen; its top is the farthest of them.",
    note=f"Sweep the points once, size-{K} max-heap of (negated d², point).",
    labels=[d2(p) for p in points],
    marks={str(i): "dim" for i in range(len(points))},
    sidebar=sidebar_heap(heap),
    state=[["k", K], ["heap size", 0]])

for i, p in enumerate(points):
    dd = d2(p)
    heapq.heappush(heap, (-dd, p))
    over = len(heap) > K
    add(act=2, code="fast", line=2,
        pointers={"p": i}, marks={str(i): "active"},
        note=f"Point {label(p)}, d²={dd}: push it. Heap size {len(heap)}"
             + (" — over k, challenge the farthest." if over else "."),
        sidebar=sidebar_heap(heap),
        state=[["point", label(p)], ["d²", dd], ["heap size", len(heap)]])
    if over:
        neg, dropped = heapq.heappop(heap)
        add(act=2, code="fast", line=4,
            pointers={"p": i}, marks={str(i): "dim"},
            note=f"Drop the farthest keeper {label(dropped)} (d²={-neg}) — it's not "
                 f"in the {K} nearest.",
            sidebar=sidebar_heap(heap),
            state=[["evicted", label(dropped)], ["its d²", -neg], ["heap size", len(heap)]])

kept = sorted((-nd, p) for nd, p in heap)
kept_labels = [label(p) for _, p in kept]
# verify against solution's k_closest_sorted
want = set(tuple(p) for p in sorted(points, key=d2)[:K])
assert set(tuple(p) for _, p in kept) == want, (kept, want)
add(act=2, code="fast", line=5,
    note=f"Sweep done. Heap holds the {K} nearest: {kept_labels}. Far points never fully ranked.",
    marks={str(i): "dim" for i in range(len(points))},
    sidebar=sidebar_heap(heap),
    state=[["answer", str(kept_labels)], ["heap size", len(heap)]],
    banner=f"{K} nearest = {kept_labels}")

# ---- Act 3: edge case (origin included, k=1) ----
edge = [[0, 0], [1, 1], [2, 2]]
K2 = 1
ecells = [label(p) for p in edge]
heap2 = []
add(act=3, cells=list(ecells), code="fast", line=0,
    intro="the origin itself has distance 0 and must win when k=1.",
    invariant="d²=0 for the origin, so it stays the nearest keeper.",
    note=f"Edge: {[label(p) for p in edge]}, k={K2}. The origin (0,0) is distance 0.",
    labels=[d2(p) for p in edge],
    marks={str(i): "dim" for i in range(len(edge))},
    sidebar=sidebar_heap(heap2),
    state=[["k", K2], ["heap size", 0]])
for i, p in enumerate(edge):
    dd = d2(p)
    heapq.heappush(heap2, (-dd, p))
    dropped = None
    if len(heap2) > K2:
        _, dropped = heapq.heappop(heap2)
    note = f"{label(p)}, d²={dd}: push. "
    if dropped is not None:
        note += f"Over k=1, drop farther {label(dropped)}. "
    nearest = min(heap2, key=lambda t: -t[0])[1]
    note += f"Nearest so far {label(nearest)}."
    add(act=3, code="fast", line=2,
        pointers={"p": i}, marks={str(i): "active"},
        note=note, sidebar=sidebar_heap(heap2),
        state=[["point", label(p)], ["d²", dd], ["heap size", len(heap2)]])
assert set(tuple(p) for _, p in heap2) == {(0, 0)}
add(act=3, code="fast", line=5,
    note="Only (0,0) survives — distance 0 beats everything.",
    marks={str(i): "dim" for i in range(len(edge))},
    sidebar=sidebar_heap(heap2),
    state=[["answer", "(0,0)"]], banner="1 nearest = (0,0)")

trace = {
    "player": "linear",
    "title": "K Closest Points — watch the farthest keeper",
    "acts": ["Naive: sort all by distance", "The waste", "Fast: size-k max-heap", "Edge: origin, k=1"],
    "code": {"naive": NAIVE, "fast": FAST},
    "legend": [["active", "point being challenged in"], ["good", "a kept nearest point"],
               ["dim", "far / discarded"]],
    "cells": list(cells),
    "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
