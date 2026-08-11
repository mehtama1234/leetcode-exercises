"""Rich full-arc trace for Trapping Rain Water (linear renderer).
Arc: brute (rescan both sides for every column) -> the waste -> monotonic stack
resolving trapped slabs at each pop -> a symmetric edge case. The sidebar shows
the decreasing stack of indices; each pop fills one horizontal water slab.
Mirrors trap_brute / trap in solution.py. Writes trace.json.
"""
import json
import os

height = [4, 2, 0, 3, 2, 5]  # traps 9
frames = []

BRUTE = [
    "for i in range(n):",
    "    left_max = max(height[:i+1])",
    "    right_max = max(height[i:])",
    "    total += min(left_max, right_max) - height[i]",
]
FAST = [
    "for i, h in enumerate(height):",
    "    while stack and height[stack[-1]] < h:",
    "        bottom = stack.pop()",
    "        if not stack: break",
    "        left = stack[-1]",
    "        width = i - left - 1",
    "        bounded = min(height[left], h) - height[bottom]",
    "        total += width * bounded",
    "    stack.append(i)",
]


def add(**f):
    frames.append(f)


def sb(stack):
    return {"title": "stack (indices, heights fall)",
            "rows": [[str(k), f"h={height[k]}"] for k in stack]}


# ---- Act 0: brute force ----
work = 0
add(act=0, cells=height, code="brute", line=0,
    intro="every column rescans ALL the way left and ALL the way right for its walls.",
    invariant="water over i = min(tallest left, tallest right) - height[i].",
    note="Brute force: for each column, find the tallest wall on each side, then the "
    "water it holds is min of those minus its own height.",
    pointers={"i": 0}, marks={"0": "active"},
    state=[["total", 0], ["scans", 0]])
total_b = 0
for i in range(len(height)):
    lm = max(height[:i + 1])
    rm = max(height[i:])
    work += (i + 1) + (len(height) - i)  # cells touched by the two max scans
    w = min(lm, rm) - height[i]
    total_b += w
    add(act=0, code="brute", line=3,
        note=f"col {i} (h={height[i]}): left wall {lm}, right wall {rm} -> "
             f"water {min(lm, rm)}-{height[i]} = {w}.",
        pointers={"i": i},
        marks={str(i): "active", **{str(k): "dim" for k in range(len(height)) if k != i}},
        state=[["i", i], ["left_max", lm], ["right_max", rm], ["water here", w],
               ["total", total_b], ["scans", work]])
add(act=0, code="brute", line=3,
    note=f"Total water = {total_b}. But it cost {work} cell-scans for six columns — "
    "each column re-walked ground its neighbours already covered.",
    marks={str(k): "dim" for k in range(len(height))},
    state=[["answer", total_b], ["scans", work]])

# ---- Act 1: the waste ----
add(act=1,
    intro="both walls for a column are already known from the columns beside it.",
    note=f"The two max-scans repeat: column i and column i+1 rescan almost the same "
    f"left side. {work} scans for 6 columns is about n*n work.",
    marks={str(k): "dim" for k in range(len(height))},
    state=[["scans (brute)", work], ["pattern", "~ n * n"]])
add(act=1,
    note="A monotonic stack fixes each wall exactly once: when a taller bar arrives it "
    "becomes the right wall for everything shorter waiting behind it.",
    marks={str(k): "dim" for k in range(len(height))},
    state=[["what we want", "one pass"], ["each bar", "push once, pop once"]])

# ---- Act 2: monotonic stack ----
stack = []
total = 0
add(act=2, cells=height, code="fast", line=0,
    intro="the stack holds bars still waiting for a taller right wall; each pop fills a slab.",
    invariant="stack heights are non-increasing bottom -> top.",
    note="Keep a stack of indices with falling heights. A taller bar is a right wall: "
    "pop the valley floor, use the new top as the left wall, add that slab of water.",
    pointers={"i": 0}, marks={}, sidebar=sb(stack),
    state=[["total", 0]])
for i, h in enumerate(height):
    add(act=2, code="fast", line=1,
        note=f"i={i}, h={h}. While the stack top is shorter than {h}, it has found its "
             f"right wall.",
        pointers={"i": i}, marks={str(i): "active"}, sidebar=sb(stack),
        state=[["i", i], ["h", h], ["total", total]])
    while stack and height[stack[-1]] < h:
        bottom = stack.pop()
        if not stack:
            add(act=2, code="fast", line=3,
                note=f"Popped floor {bottom} (h={height[bottom]}) but the stack is now "
                     f"empty — no left wall, so water spills off the left edge.",
                pointers={"i": i}, marks={str(i): "active", str(bottom): "bad"},
                sidebar=sb(stack), state=[["spills", "no left wall"], ["total", total]])
            break
        left = stack[-1]
        width = i - left - 1
        bounded = min(height[left], h) - height[bottom]
        total += width * bounded
        add(act=2, code="fast", line=7,
            note=f"Slab over floor {bottom}: left wall {height[left]}, right wall {h}, "
                 f"width {width} -> {width}*({min(height[left], h)}-{height[bottom]}) "
                 f"= {width * bounded}.",
            pointers={"i": i},
            marks={str(left): "active", str(i): "active", str(bottom): "good"},
            arc=[left, i], sidebar=sb(stack),
            state=[["floor", bottom], ["width", width], ["bounded", bounded],
                   ["+water", width * bounded], ["total", total]])
    stack.append(i)
    add(act=2, code="fast", line=8,
        note=f"Push {i} onto the stack and move on.",
        pointers={"i": i}, marks={str(i): "dim"}, sidebar=sb(stack),
        state=[["pushed", i], ["total", total]])
add(act=2, code="fast", line=8,
    note=f"One pass, each bar pushed and popped once. Total water = {total}.",
    marks={str(k): "good" for k in range(len(height))}, sidebar=sb(stack),
    state=[["answer", total], ["vs brute scans", work]],
    banner=f"Trapped water = {total}   filled in horizontal slabs, one pass")

# ---- Act 3: edge case, symmetric bowl ----
edge = [2, 0, 2]
stack = []
total = 0
add(act=3, cells=edge, code="fast", line=0,
    intro="a single dip between two equal walls — one clean slab.",
    invariant="same rule: a taller-or-equal-enough right wall resolves the floor.",
    note="Edge case: [2,0,2], a symmetric bowl. The middle 0 traps 2 units.",
    pointers={"i": 0}, marks={}, sidebar={"title": "stack (indices)", "rows": []},
    state=[["total", 0]])
for i, h in enumerate(edge):
    while stack and edge[stack[-1]] < h:
        bottom = stack.pop()
        if not stack:
            break
        left = stack[-1]
        width = i - left - 1
        bounded = min(edge[left], h) - edge[bottom]
        total += width * bounded
        add(act=3, code="fast", line=7,
            note=f"Right wall {h} at i={i} meets left wall {edge[left]}: floor {bottom} "
                 f"holds width {width} * height {bounded} = {width * bounded}.",
            pointers={"i": i}, marks={"0": "good", "1": "good", "2": "good"},
            arc=[left, i],
            sidebar={"title": "stack (indices)", "rows": [[str(k), f"h={edge[k]}"] for k in stack]},
            state=[["water", width * bounded], ["total", total]])
    stack.append(i)
add(act=3, code="fast", line=8,
    note=f"The bowl [2,0,2] traps {total}.",
    marks={"0": "good", "1": "good", "2": "good"},
    state=[["answer", total]], banner="[2,0,2] traps 2")

trace = {
    "player": "linear",
    "title": "Trapping Rain Water - from rescanning walls to one slab-filling pass",
    "acts": ["Brute: rescan both walls", "The waste", "Monotonic stack: slabs", "Edge: [2,0,2] bowl"],
    "code": {"brute": BRUTE, "fast": FAST},
    "legend": [["active", "walls / current bar"], ["good", "resolved floor / filled"],
               ["bad", "spilled (no left wall)"], ["dim", "on stack / skipped"]],
    "cells": height, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
