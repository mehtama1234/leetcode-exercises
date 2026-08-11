"""Full-arc trace for Product of Array Except Self, mirroring solution.py: the
O(n^2) re-multiply brute force and the O(n) prefix-then-suffix two-pass. Linear
renderer: nums on top; the `answer` array shown via labels/marks and a sidebar
so the running prefix and suffix are visible. A multiply counter makes
brute-vs-fast concrete. Writes trace.json.
"""
import json
import os

nums = [1, 2, 3, 4]
# answer = [24, 12, 8, 6]
frames = []

BRUTE = [
    "for i in range(n):",
    "    answer[i] = 1",
    "    for j in range(n):",
    "        if j != i:",
    "            answer[i] *= nums[j]",
]
FAST = [
    "prefix = 1",
    "for i in range(n):",
    "    answer[i] = prefix       # product of the LEFT",
    "    prefix *= nums[i]",
    "suffix = 1",
    "for i in range(n-1, -1, -1):",
    "    answer[i] *= suffix      # times product of the RIGHT",
    "    suffix *= nums[i]",
]


def add(**f):
    frames.append(f)


n = len(nums)

# ---- Act 0: brute force ----
work = 0
answer = [1] * n
add(act=0, cells=nums, code="brute", line=0,
    intro="each i re-multiplies almost the whole array — the same products, over and over.",
    invariant="answer[k] holds the finished product for every k already processed.",
    note="Brute force: answer[i] is the product of all the others, so for each i multiply every j != i.",
    pointers={"i": 0}, marks={"0": "active"},
    state=[["i", 0], ["multiplies", 0]])
for i in range(n):
    answer[i] = 1
    for j in range(n):
        if j == i:
            continue
        work += 1
        answer[i] *= nums[j]
        add(act=0, code="brute", line=4,
            note=f"answer[{i}] *= nums[{j}] ({nums[j]}) -> {answer[i]}.",
            pointers={"i": i, "j": j},
            marks={str(i): "active", str(j): "dim"},
            state=[["i", i], ["j", j], [f"answer[{i}]", answer[i]], ["multiplies", work]])
add(act=0, code="brute", line=4,
    note=f"Brute answer = {answer}. It took {work} multiplies — each i re-walked the array.",
    marks={str(k): "good" for k in range(n)},
    banner=f"answer = {answer}   (brute: {work} multiplies)",
    state=[["answer", str(answer)], ["multiplies", work]])

# ---- Act 1: the waste ----
add(act=1,
    intro="every answer[i] recomputes products its neighbours already knew.",
    note=f"{work} multiplies for n=4. That is ~n*(n-1) work. But the product except i splits cleanly: "
         "everything LEFT of i times everything RIGHT of i.",
    marks={str(k): "dim" for k in range(n)},
    state=[["multiplies (brute)", work], ["split", "left x right"]])
add(act=1,
    note="Sweep once left to right carrying the running LEFT product, then once right to left carrying "
         "the running RIGHT product. Two passes, no division.",
    marks={str(k): "dim" for k in range(n)},
    state=[["passes", 2], ["target", "O(n)"]])

# ---- Act 2: prefix pass then suffix pass ----
answer = [1] * n
add(act=2, cells=nums, labels=[str(x) for x in [1] * n], code="fast", line=0,
    intro="answer[i] first receives the LEFT product; the RIGHT product is multiplied in on the way back.",
    invariant="after the first pass, answer[i] = product of everything strictly left of i.",
    note="Pass 1 (left to right): write the running prefix into answer[i] BEFORE folding nums[i] in.",
    pointers={"i": 0}, marks={"0": "active"},
    sidebar={"title": "carry", "rows": [["prefix", "1"], ["suffix", "-"]]},
    state=[["prefix", 1]])
prefix = 1
for i in range(n):
    answer[i] = prefix
    add(act=2, code="fast", line=2, labels=[str(x) for x in answer],
        note=f"answer[{i}] = prefix = {prefix}  (product of everything left of {i}).",
        pointers={"i": i}, marks={str(i): "active"},
        sidebar={"title": "carry", "rows": [["prefix", str(prefix)], ["suffix", "-"]]},
        state=[["i", i], [f"answer[{i}]", answer[i]], ["prefix", prefix]])
    prefix *= nums[i]
    add(act=2, code="fast", line=3, labels=[str(x) for x in answer],
        note=f"Fold nums[{i}] ({nums[i]}) into prefix -> {prefix} for the next index.",
        pointers={"i": i}, marks={str(i): "dim"},
        sidebar={"title": "carry", "rows": [["prefix", str(prefix)], ["suffix", "-"]]},
        state=[["prefix", prefix]])

# suffix pass
add(act=2, cells=nums, labels=[str(x) for x in answer], code="fast", line=4,
    note="Pass 2 (right to left): multiply the running suffix (product of everything to the right) into answer[i].",
    pointers={"i": n - 1}, marks={str(n - 1): "active"},
    sidebar={"title": "carry", "rows": [["prefix", "done"], ["suffix", "1"]]},
    state=[["suffix", 1]])
suffix = 1
for i in range(n - 1, -1, -1):
    answer[i] *= suffix
    add(act=2, code="fast", line=6, labels=[str(x) for x in answer],
        note=f"answer[{i}] *= suffix ({suffix}) -> {answer[i]}  (left product x right product).",
        pointers={"i": i}, marks={str(i): "good"},
        sidebar={"title": "carry", "rows": [["prefix", "done"], ["suffix", str(suffix)]]},
        state=[["i", i], [f"answer[{i}]", answer[i]], ["suffix", suffix]])
    suffix *= nums[i]
add(act=2, code="fast", line=7, labels=[str(x) for x in answer],
    note=f"answer = {answer} in two passes, {2 * n} multiplies vs {work} brute. No division used.",
    marks={str(k): "good" for k in range(n)},
    banner=f"answer = {answer}   (fast: 2 passes vs {work} brute multiplies)",
    state=[["answer", str(answer)], ["multiplies", 2 * n], ["vs brute", work]])

# ---- Act 3: edge case, a single zero ----
edge = [-1, 1, 0, -3, 3]
# answer = [0, 0, 9, 0, 0]
ea = [1] * len(edge)
add(act=3, cells=edge, labels=[str(x) for x in ea], code="fast", line=0,
    intro="the one index sitting ON the zero is the only answer that survives — its left*right skips the zero.",
    invariant="prefix and suffix each exclude nums[i], so index i never multiplies its own zero in.",
    note="Edge case: a single 0. Every index except the zero's own position multiplies that 0 in -> 0.",
    pointers={"i": 0}, marks={"2": "bad"},
    sidebar={"title": "carry", "rows": [["prefix", "1"], ["suffix", "-"]]},
    state=[["zero at", 2]])
prefix = 1
for i in range(len(edge)):
    ea[i] = prefix
    prefix *= edge[i]
suffix = 1
for i in range(len(edge) - 1, -1, -1):
    ea[i] *= suffix
    suffix *= edge[i]
    surv = ea[i] != 0
    add(act=3, code="fast", line=6, labels=[str(x) for x in ea],
        note=f"answer[{i}] = {ea[i]}. "
             + ("Non-zero — this index is the zero's own slot, its product skips the 0."
                if surv else "Zero — this index multiplied the lone 0 in."),
        pointers={"i": i}, marks={str(i): "good" if surv else "bad", "2": "bad"},
        sidebar={"title": "carry", "rows": [["suffix", str(suffix)]]},
        state=[[f"answer[{i}]", ea[i]]])
add(act=3, code="fast", line=7, labels=[str(x) for x in ea],
    note=f"answer = {ea}. Only index 2 (the zero itself) is non-zero.",
    marks={str(k): "good" if ea[k] != 0 else "bad" for k in range(len(edge))},
    banner=f"answer = {ea} — a single zero zeroes everything but its own slot",
    state=[["answer", str(ea)]])

trace = {
    "player": "linear",
    "title": "Product of Array Except Self — left product times right product",
    "acts": ["Brute force: re-multiply", "The waste", "Fast: prefix then suffix", "Edge case: a single zero"],
    "code": {"brute": BRUTE, "fast": FAST},
    "legend": [["active", "index being filled"], ["good", "finished answer"], ["dim", "folded into a carry"], ["bad", "zeroed out"]],
    "cells": nums, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
