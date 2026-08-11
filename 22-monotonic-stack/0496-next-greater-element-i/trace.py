"""Rich full-arc trace for Next Greater Element I (linear renderer).
Arc: brute (re-scan nums2 for every query) -> the waste -> one monotonic-stack
sweep of nums2 that resolves each waiting value the moment a bigger one arrives ->
answer the queries -> a decreasing edge case (nobody ever pops).
The sidebar shows the stack of values still waiting for a greater element.
Mirrors next_greater_element_brute / next_greater_element in solution.py.
Writes trace.json.
"""
import json
import os

nums1 = [4, 1, 2]
nums2 = [1, 3, 4, 2]
frames = []

BRUTE = [
    "for x in nums1:",
    "    j = nums2.index(x)",
    "    for k in range(j+1, len(nums2)):",
    "        if nums2[k] > x:",
    "            ans = nums2[k]; break",
]
FAST = [
    "for x in nums2:",
    "    while stack and stack[-1] < x:",
    "        next_greater[stack.pop()] = x",
    "    stack.append(x)",
    "# unresolved values default to -1",
]


def add(**f):
    frames.append(f)


def sb(stack):
    return {"title": "stack (waiting values)", "rows": [[str(k), "waiting"] for k in stack]}


# ---- Act 0: brute force ----
work = 0
add(act=0, cells=nums2, code="brute", line=0,
    intro="each query starts a fresh rightward scan of nums2 from scratch.",
    invariant="answer(x) = first value right of x in nums2 that is bigger.",
    note="Brute force: for every query value, find it in nums2, then scan right until "
    "something strictly bigger shows up.",
    pointers={}, marks={}, state=[["queries", nums1], ["scans", 0]])
ans_b = []
for x in nums1:
    j = nums2.index(x)
    nxt = -1
    hit = j
    for k in range(j + 1, len(nums2)):
        work += 1
        if nums2[k] > x:
            nxt = nums2[k]
            hit = k
            break
    ans_b.append(nxt)
    add(act=0, code="brute", line=3,
        note=f"query {x} sits at index {j}; scan right -> "
             + (f"next greater is {nxt} at {hit}." if nxt != -1 else "nothing bigger, -1."),
        pointers={"x": j, "scan": hit if nxt != -1 else len(nums2) - 1},
        marks={str(j): "active", **({str(hit): "good"} if nxt != -1 else {})},
        state=[["query", x], ["answer", nxt], ["scans", work]])
add(act=0, code="brute", line=4,
    note=f"Answers {ans_b}, but every query re-walked nums2 — {work} scan-steps, "
    "re-discovering relationships that never change.",
    marks={}, state=[["answers", str(ans_b)], ["scans", work]])

# ---- Act 1: the waste ----
add(act=1,
    intro="the 'next greater' of every value in nums2 is fixed — compute them all once.",
    note=f"Each query rescans the same array. {work} steps here; with q queries over m "
    "values that is q*m work.",
    marks={}, state=[["scans (brute)", work], ["pattern", "~ q * m"]])
add(act=1,
    note="Instead sweep nums2 ONE time with a decreasing stack: when a bigger value "
    "arrives it resolves every smaller value still waiting behind it.",
    marks={}, state=[["what we want", "one sweep"], ["then queries", "O(1) each"]])

# ---- Act 2: one monotonic sweep of nums2 ----
stack = []
next_greater = {}
add(act=2, cells=nums2, code="fast", line=0,
    intro="the stack holds values still hunting for a bigger neighbour to the right.",
    invariant="stack values strictly decrease bottom -> top.",
    note="Sweep nums2. Each new value pops (and answers) every smaller value waiting on "
    "the stack, then joins the stack itself.",
    pointers={"i": 0}, marks={}, sidebar=sb(stack), state=[["resolved", 0]])
for i, x in enumerate(nums2):
    add(act=2, code="fast", line=1,
        note=f"i={i}, value {x}. Pop every waiting value smaller than {x}.",
        pointers={"i": i}, marks={str(i): "active"}, sidebar=sb(stack),
        state=[["i", i], ["value", x], ["resolved", len(next_greater)]])
    while stack and stack[-1] < x:
        popped = stack.pop()
        next_greater[popped] = x
        pidx = nums2.index(popped)
        add(act=2, code="fast", line=2,
            note=f"{x} is the next greater element of {popped} -> record {popped}:{x}.",
            pointers={"i": i}, arc=[pidx, i],
            marks={str(pidx): "good", str(i): "active"}, sidebar=sb(stack),
            state=[["resolved", f"{popped}->{x}"], ["total resolved", len(next_greater)]])
    stack.append(x)
    add(act=2, code="fast", line=3,
        note=f"{x} has no answer yet; push it to wait.",
        pointers={"i": i}, marks={str(i): "dim"}, sidebar=sb(stack),
        state=[["waiting", str(stack)]])
add(act=2, code="fast", line=4,
    note=f"Sweep done. Left on the stack: {stack} — no greater element to their right, "
    "so they default to -1.",
    marks={}, sidebar=sb(stack),
    state=[["map", str(next_greater)], ["default", "-1"]])

# ---- Act 3: answer the queries ----
add(act=3, cells=nums1, labels=list(range(len(nums1))), code="fast", line=4,
    intro="each query is now a single dictionary lookup.",
    invariant="value -> next-greater was precomputed in one sweep.",
    note="Answer each query from the map: found -> that value, missing -> -1.",
    pointers={}, marks={},
    state=[["map", str(next_greater)]])
result = []
for i, x in enumerate(nums1):
    v = next_greater.get(x, -1)
    result.append(v)
    add(act=3, code="fast", line=4,
        note=f"query {x}: map -> {v}.",
        pointers={"q": i}, marks={str(i): "good" if v != -1 else "bad"},
        state=[["query", x], ["answer", v]])
add(act=3, code="fast", line=4,
    note=f"Answers = {result}. One sweep built the map; each query was O(1).",
    marks={str(i): "good" for i in range(len(nums1))},
    state=[["answer", str(result)], ["vs brute scans", work]],
    banner=f"Next greater = {result}   (one sweep + O(1) lookups)")

# ---- Act 4: strictly-decreasing edge ----
edge = [3, 2, 1]
stack = []
ng = {}
add(act=4, cells=edge, code="fast", line=0,
    intro="in a falling sequence nothing is ever bigger than what waits — no pops.",
    invariant="every value keeps stacking; none gets resolved.",
    note="Edge case: nums2 = [3,2,1]. Each value is smaller than the last, so nothing "
    "pops and every value's next-greater is -1.",
    pointers={"i": 0}, marks={}, sidebar={"title": "stack (waiting values)", "rows": []},
    state=[["resolved", 0]])
for i, x in enumerate(edge):
    while stack and stack[-1] < x:
        ng[stack.pop()] = x
    stack.append(x)
    add(act=4, code="fast", line=3,
        note=f"{x} pops nothing (all earlier values are bigger); push it. Still 0 resolved.",
        pointers={"i": i}, marks={str(i): "dim"},
        sidebar={"title": "stack (waiting values)", "rows": [[str(k), "waiting"] for k in stack]},
        state=[["waiting", str(stack)], ["resolved", len(ng)]])
add(act=4, code="fast", line=4,
    note="All three stay unresolved -> every answer is -1.",
    marks={"0": "bad", "1": "bad", "2": "bad"},
    state=[["answer", "[-1, -1, -1]"]], banner="Falling sequence -> all -1")

trace = {
    "player": "linear",
    "title": "Next Greater Element - one stack sweep instead of a scan per query",
    "acts": ["Brute: scan per query", "The waste", "One monotonic sweep", "Answer queries",
             "Edge: falling [3,2,1]"],
    "code": {"brute": BRUTE, "fast": FAST},
    "legend": [["active", "current value"], ["good", "resolved / answer"],
               ["bad", "no greater element (-1)"], ["dim", "pushed, waiting"]],
    "cells": nums2, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
