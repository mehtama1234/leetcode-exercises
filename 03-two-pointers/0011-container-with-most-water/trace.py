"""Full-arc trace for Container With Most Water: brute every pair -> the waste ->
converging two pointers (always move the shorter wall) -> edge case. Mirrors
solution.py. Writes trace.json.
"""
import json
import os

height = [1, 8, 6, 2, 5, 4, 8, 3, 7]  # answer 49  (lines 1 and 8, width 7)
frames = []

BRUTE = [
    "for i in range(n):",
    "    for j in range(i+1, n):",
    "        area = (j-i) * min(h[i], h[j])",
    "        best = max(best, area)",
]
FAST = [
    "left, right = 0, n-1",
    "while left < right:",
    "    area = (right-left) * min(h[left], h[right])",
    "    best = max(best, area)",
    "    if h[left] < h[right]: left += 1",
    "    else: right -= 1",
]


def add(**f):
    frames.append(f)


def marks_all(cls):
    return {str(k): cls for k in range(len(height))}


# ---- Act 0: brute force — every pair ----
work = 0
best = 0
best_pair = (0, 0)
add(act=0, cells=height, labels=list(range(len(height))), code="brute", line=0,
    intro="every i drags a j across the whole tail — most pairs can never win.",
    invariant="best holds the largest area among all pairs seen so far.",
    note="Brute force: try every pair of lines. Area = width * shorter wall. Watch i=0 sweep.",
    pointers={"i": 0, "j": 1}, marks={"0": "active", "1": "dim"},
    state=[["i", 0], ["j", 1], ["best", 0], ["pairs", 0]])
for i in range(len(height)):
    for j in range(i + 1, len(height)):
        work += 1
        area = (j - i) * min(height[i], height[j])
        better = area > best
        if better:
            best = area
            best_pair = (i, j)
        # only surface a subset of frames to keep it readable
        if i <= 1 or better:
            add(act=0, code="brute", line=2 if not better else 3,
                note=f"lines {i},{j}: width {j-i} x min({height[i]},{height[j]}) = {area}. "
                     + (f"New best {best}." if better else f"Best stays {best}."),
                pointers={"i": i, "j": j}, arc=[i, j],
                marks={str(i): "active", str(j): "good" if better else "dim"},
                state=[["i", i], ["j", j], ["area", area], ["best", best], ["pairs", work]])
add(act=0, code="brute", line=3,
    note=f"Best area {best} between lines {best_pair[0]} and {best_pair[1]} — but it cost "
         f"{work} pairs for {len(height)} lines.",
    pointers={"i": best_pair[0], "j": best_pair[1]}, arc=list(best_pair),
    marks={str(best_pair[0]): "good", str(best_pair[1]): "good"},
    state=[["best", best], ["pairs", work]])

# ---- Act 1: the waste ----
add(act=1,
    intro="how many pairs the counter racked up — nearly all were doomed by width.",
    note=f"{work} pairs for 9 lines. Any pair narrower than the current best AND no taller "
    "than its short wall was never going to win — yet brute tested them all.",
    marks=marks_all("dim"),
    state=[["pairs (brute)", work], ["pattern", "~ n*n / 2"]])
add(act=1,
    note="Start at the widest container instead. Moving inward only loses width, so the "
    "one hope for more area is a taller SHORTER wall. Move the short wall, never the tall.",
    marks=marks_all("dim"),
    state=[["at n=1000", "~500,000"], ["what we want", "~1,000"]])

# ---- Act 2: fast, converging two pointers ----
left, right = 0, len(height) - 1
best = 0
best_pair = (0, 0)
add(act=2, cells=height, labels=list(range(len(height))), code="fast", line=0,
    intro="the shorter wall always steps in — dropping it throws away no better container.",
    invariant="best holds the largest area for any pair as wide as [left, right] or wider.",
    note="Two pointers at the ends — the widest box. Area caps at the shorter wall.",
    pointers={"L": left, "R": right}, window=[left, right],
    marks={str(left): "active", str(right): "active"},
    state=[["left", left], ["right", right], ["best", 0]])
while left < right:
    width = right - left
    area = width * min(height[left], height[right])
    if area > best:
        best = area
        best_pair = (left, right)
    move_left = height[left] < height[right]
    who = "left" if move_left else "right"
    add(act=2, code="fast", line=2,
        note=f"width {width} x min({height[left]},{height[right]}) = {area}. "
             f"Best {best}. Shorter wall is on the {who} — move it in.",
        pointers={"L": left, "R": right}, window=[left, right], arc=[left, right],
        marks={str(left): "active", str(right): "active"},
        state=[["left", left], ["right", right], ["area", area], ["best", best]])
    if move_left:
        left += 1
    else:
        right -= 1
a, b = best_pair
add(act=2, code="fast", line=3,
    note=f"Sweep done in one pass. Largest area {best} between lines {a} and {b}.",
    pointers={"L": a, "R": b}, window=[a, b], arc=[a, b],
    marks={str(a): "good", str(b): "good"},
    state=[["best", best], ["steps", len(height) - 1], ["vs brute", work]],
    banner=f"Max area {best}   lines {a} and {b}   — one pass vs {work} brute pairs")

# ---- Act 3: edge case, two equal outer walls ----
edge = [4, 3, 2, 1, 4]  # answer 16: the two outer 4s, width 4
frames_before = len(frames)
left, right = 0, len(edge) - 1
best = 0
best_pair = (0, 0)
add(act=3, cells=edge, labels=list(range(len(edge))), code="fast", line=0,
    intro="on a tie either wall may move — the widest tie wins outright here.",
    invariant="ties can move either side; width is largest at the very start.",
    note="Edge case: equal walls at both ends. The widest box is already the answer.",
    pointers={"L": left, "R": right}, window=[left, right],
    marks={str(left): "active", str(right): "active"},
    state=[["left", left], ["right", right], ["best", 0]])
while left < right:
    width = right - left
    area = width * min(edge[left], edge[right])
    if area > best:
        best = area
        best_pair = (left, right)
    # tie -> move right (matches solution: h[left] < h[right] is False on tie)
    if edge[left] < edge[right]:
        left += 1
    else:
        right -= 1
    add(act=3, code="fast", line=3,
        note=f"width {width}: area {area}. Best {best}.",
        pointers={"L": left, "R": right} if left < right else {"L": best_pair[0], "R": best_pair[1]},
        window=[best_pair[0], best_pair[1]],
        marks={str(best_pair[0]): "good", str(best_pair[1]): "good"},
        state=[["area", area], ["best", best]])
a, b = best_pair
frames[-1]["banner"] = f"Max area {best}   the two outer 4s, width {b - a}"

trace = {
    "player": "linear",
    "title": "Container With Most Water — from every pair to one converging sweep",
    "acts": ["Brute force: every pair", "The waste",
             "Fast: move the shorter wall", "Edge case: equal ends"],
    "code": {"brute": BRUTE, "fast": FAST},
    "legend": [["active", "the two walls in play"], ["good", "best container"],
               ["dim", "discarded pair"]],
    "cells": height, "labels": list(range(len(height))), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
