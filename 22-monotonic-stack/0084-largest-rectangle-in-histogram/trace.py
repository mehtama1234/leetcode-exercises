"""Rich full-arc trace for Largest Rectangle in Histogram (linear renderer).
Arc: brute (each bar re-walks its neighbours) -> the waste -> monotonic increasing
stack that resolves each bar the moment a shorter bar appears -> a flat edge case.
The sidebar shows the increasing stack of indices; each pop settles one rectangle.
Mirrors largest_rectangle_brute / largest_rectangle in solution.py. Writes trace.json.
"""
import json
import os

heights = [2, 1, 5, 6, 2, 3]  # answer 10 (bars 5 and 6 over width 2)
frames = []

BRUTE = [
    "for i in range(n):",
    "    walk left while >= h[i]",
    "    walk right while >= h[i]",
    "    best = max(best, h[i] * width)",
]
FAST = [
    "for i, h in enumerate(heights + [0]):",
    "    while stack and heights[stack[-1]] > h:",
    "        top = stack.pop()",
    "        left = stack[-1] if stack else -1",
    "        width = i - left - 1",
    "        best = max(best, heights[top] * width)",
    "    stack.append(i)",
]


def add(**f):
    frames.append(f)


def sb(stack):
    return {"title": "stack (indices, heights rise)",
            "rows": [[str(k), f"h={heights[k]}"] for k in stack]}


# ---- Act 0: brute force ----
work = 0
best_b = 0
add(act=0, cells=heights, code="brute", line=0,
    intro="every bar walks outward over its neighbours to measure its own rectangle.",
    invariant="a rectangle is pinned by its shortest bar; area = height * width.",
    note="Brute force: treat each bar as the shortest, spread left and right while "
    "bars stay at least as tall, then area = height * width.",
    pointers={"i": 0}, marks={"0": "active"}, state=[["best", 0], ["steps", 0]])
for i in range(len(heights)):
    left = i
    while left - 1 >= 0 and heights[left - 1] >= heights[i]:
        left -= 1
        work += 1
    right = i
    while right + 1 < len(heights) and heights[right + 1] >= heights[i]:
        right += 1
        work += 1
    work += 1
    width = right - left + 1
    area = heights[i] * width
    best_b = max(best_b, area)
    add(act=0, code="brute", line=3,
        note=f"bar {i} (h={heights[i]}) spreads [{left}..{right}], width {width} -> "
             f"area {heights[i]}*{width} = {area}.",
        pointers={"i": i},
        marks={**{str(k): "dim" for k in range(len(heights))},
               **{str(k): "active" for k in range(left, right + 1)}, str(i): "good"},
        window=[left, right],
        state=[["i", i], ["width", width], ["area", area], ["best", best_b],
               ["steps", work]])
add(act=0, code="brute", line=3,
    note=f"Best = {best_b}, but it cost {work} neighbour-steps — every bar re-walked "
    "ground its neighbours already covered.",
    marks={str(k): "dim" for k in range(len(heights))},
    state=[["answer", best_b], ["steps", work]])

# ---- Act 1: the waste ----
add(act=1,
    intro="each bar's left and right limits are the first SHORTER bars — knowable once.",
    note=f"The outward walks overlap: neighbouring bars re-scan the same run. {work} "
    "steps for 6 bars grows like n*n.",
    marks={str(k): "dim" for k in range(len(heights))},
    state=[["steps (brute)", work], ["pattern", "~ n * n"]])
add(act=1,
    note="An increasing stack settles a bar the instant a shorter bar appears: that "
    "shorter bar is its right limit, the bar below it on the stack is its left limit.",
    marks={str(k): "dim" for k in range(len(heights))},
    state=[["what we want", "one pass"], ["each bar", "push once, pop once"]])

# ---- Act 2: monotonic stack ----
stack = []
best = 0
seq = heights + [0]
add(act=2, cells=heights, code="fast", line=0,
    intro="a trailing 0 sentinel flushes everything still waiting on the stack.",
    invariant="stack heights strictly increase bottom -> top.",
    note="Keep a stack of indices with rising heights. When a shorter bar arrives, pop "
    "and settle each taller bar: its width spans from just past the new top to here.",
    pointers={"i": 0}, marks={}, sidebar=sb(stack), state=[["best", 0]])
for i, h in enumerate(seq):
    sentinel = i == len(heights)
    add(act=2, code="fast", line=1,
        note=(f"Sentinel 0 at the end: pop everything left." if sentinel
              else f"i={i}, h={h}. Pop every stacked bar taller than {h}."),
        pointers={} if sentinel else {"i": i},
        marks={} if sentinel else {str(i): "active"}, sidebar=sb(stack),
        state=[["i", i if not sentinel else "end"], ["h", h], ["best", best]])
    while stack and heights[stack[-1]] > h:
        top = stack.pop()
        left = stack[-1] if stack else -1
        width = i - left - 1
        area = heights[top] * width
        best = max(best, area)
        add(act=2, code="fast", line=5,
            note=f"Settle bar {top} (h={heights[top]}): right limit i={i}, left limit "
                 f"{left} -> width {width}, area {heights[top]}*{width} = {area}."
                 + ("  New best." if area == best else ""),
            pointers={} if sentinel else {"i": i},
            marks={**({} if left < 0 else {str(left): "active"}),
                   str(top): "good", **({} if sentinel else {str(i): "active"})},
            window=[left + 1, i - 1] if width > 0 else None, sidebar=sb(stack),
            state=[["settled", top], ["width", width], ["area", area], ["best", best]])
    if not sentinel:
        stack.append(i)
        add(act=2, code="fast", line=6,
            note=f"Push {i} (h={h}); it waits for a shorter bar to its right.",
            pointers={"i": i}, marks={str(i): "dim"}, sidebar=sb(stack),
            state=[["pushed", i], ["best", best]])
add(act=2, code="fast", line=6,
    note=f"Every bar pushed and popped once. Largest rectangle = {best} (the 5 and 6 "
    "over width 2).",
    marks={"2": "good", "3": "good"}, window=[2, 3], sidebar={"title": "stack", "rows": []},
    state=[["answer", best], ["vs brute steps", work]],
    banner=f"Largest rectangle = {best}   one pass, each bar settled once")

# ---- Act 3: flat edge case ----
edge = [2, 2, 2]
stack = []
best = 0
add(act=3, cells=edge, code="fast", line=0,
    intro="equal bars never pop each other (strict >), so they settle together at the end.",
    invariant="strictly-increasing stack: equals stay stacked until the sentinel.",
    note="Edge case: [2,2,2]. No bar is strictly taller than the next, so nothing pops "
    "until the sentinel — one wide 3x2 rectangle.",
    pointers={"i": 0}, marks={}, sidebar={"title": "stack (indices)", "rows": []},
    state=[["best", 0]])
eseq = edge + [0]
for i, h in enumerate(eseq):
    while stack and edge[stack[-1]] > h:
        top = stack.pop()
        left = stack[-1] if stack else -1
        width = i - left - 1
        area = edge[top] * width
        best = max(best, area)
        add(act=3, code="fast", line=5,
            note=f"Sentinel settles bar {top}: width {width}, area {edge[top]}*{width} = "
                 f"{area}.",
            marks={"0": "good", "1": "good", "2": "good"}, window=[0, 2],
            sidebar={"title": "stack (indices)", "rows": [[str(k), f"h={edge[k]}"] for k in stack]},
            state=[["settled", top], ["area", area], ["best", best]])
    if i < len(edge):
        stack.append(i)
add(act=3, code="fast", line=6,
    note=f"[2,2,2] -> one 3-wide rectangle of height 2 = {best}.",
    marks={"0": "good", "1": "good", "2": "good"}, window=[0, 2],
    state=[["answer", best]], banner="[2,2,2] -> 6")

trace = {
    "player": "linear",
    "title": "Largest Rectangle - settle each bar once when a shorter bar arrives",
    "acts": ["Brute: walk each bar out", "The waste", "Monotonic stack", "Edge: flat [2,2,2]"],
    "code": {"brute": BRUTE, "fast": FAST},
    "legend": [["active", "left/right limits & current bar"], ["good", "settled bar / answer"],
               ["dim", "on stack / skipped"]],
    "cells": heights, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
