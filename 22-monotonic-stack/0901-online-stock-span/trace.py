"""Rich full-arc trace for Online Stock Span (linear renderer).
This is a streaming design problem with no wasteful baseline to race, so the arc
is: the naive per-call walk and its waste -> the (price, span) stack rule run over
the official stream -> a rising edge and a falling edge. The sidebar shows the
decreasing stack of (price, span) blocks; each pop absorbs a run of days.
Mirrors StockSpanner.next in solution.py. Writes trace.json.
"""
import json
import os

prices = [100, 80, 60, 70, 60, 75, 85]  # spans 1,1,1,2,1,4,6
frames = []

NAIVE = [
    "def next(price):        # naive",
    "    count = 1",
    "    walk back over stored prices",
    "    while prev <= price: count += 1",
    "    return count",
]
FAST = [
    "def next(price):",
    "    span = 1",
    "    while stack and stack[-1].price <= price:",
    "        span += stack.pop().span",
    "    stack.append((price, span))",
    "    return span",
]


def add(**f):
    frames.append(f)


def sb(stack):
    return {"title": "stack (price, span)",
            "rows": [[f"{pr}", f"span {sp}"] for pr, sp in stack]}


def marks_upto(k, cls="dim", cur=None, good=None):
    m = {str(i): cls for i in range(k + 1)}
    if good:
        for g in good:
            m[str(g)] = "good"
    if cur is not None:
        m[str(cur)] = "active"
    return m


# ---- Act 0: the naive walk and its waste ----
add(act=0, cells=prices, code="naive", line=0,
    intro="each new price walks backward over ALL earlier days it can see.",
    invariant="span = consecutive days back with price <= today, then a taller day stops it.",
    note="Naive span: for each new price, walk back counting days that were <= today's, "
    "stopping at the first strictly higher day.",
    pointers={"i": 0}, marks={"0": "active"}, state=[["day", 0], ["steps", 0]])
work = 0
for i, p in enumerate(prices):
    steps = 0
    k = i - 1
    while k >= 0 and prices[k] <= p:
        steps += 1
        k -= 1
    work += steps
    add(act=0, code="naive", line=3,
        note=f"day {i} price {p}: walk back {steps} day(s) that were <= {p}, "
             f"stopped by {'the start' if k < 0 else f'day {k} price {prices[k]}'}.",
        pointers={"i": i}, marks=marks_upto(i, cur=i),
        window=[k + 1, i] if k + 1 <= i else None,
        state=[["day", i], ["span", steps + 1], ["back-steps", work]])
add(act=0, code="naive", line=4,
    note=f"Correct, but re-walking earlier days cost {work} steps — day 75 re-counted "
    "60 and 70 that day 70 already swallowed. That overlap is the waste.",
    marks={str(i): "dim" for i in range(len(prices))},
    state=[["back-steps", work], ["pattern", "~ n * n worst case"]])

# ---- Act 1: the rule (compress into blocks) ----
add(act=1, cells=prices, code="fast", line=0,
    intro="when today >= an earlier day, that day can never block a future day again.",
    invariant="stack prices strictly decrease bottom -> top; each block carries its own span.",
    note="Rule: keep a stack of (price, span) blocks. A new price absorbs every block "
    "with price <= today, adding their spans into today's — each day is popped once, "
    "so it is amortized O(1).",
    pointers={}, marks={}, sidebar={"title": "stack (price, span)", "rows": []},
    state=[["idea", "absorb dominated days"]])

# ---- Act 2: run it over the stream ----
stack = []
spans = []
add(act=2, cells=prices, code="fast", line=0,
    intro="watch the stack absorb shorter runs and hand back a growing span.",
    invariant="a popped block's whole span folds into today's span.",
    note="Run the official stream. Each new price pops every block it dominates, sums "
    "their spans, then pushes itself.",
    pointers={"i": 0}, marks={}, sidebar=sb(stack), state=[["spans", "[]"]])
for i, p in enumerate(prices):
    add(act=2, code="fast", line=2,
        note=f"day {i}, price {p}. Absorb every stacked block with price <= {p}.",
        pointers={"i": i}, marks=marks_upto(i, cur=i), sidebar=sb(stack),
        state=[["day", i], ["price", p], ["span so far", 1]])
    span = 1
    while stack and stack[-1][0] <= p:
        pr, ps = stack.pop()
        span += ps
        add(act=2, code="fast", line=3,
            note=f"{p} >= block price {pr}: absorb its span {ps} -> running span {span}.",
            pointers={"i": i}, marks=marks_upto(i, cur=i), sidebar=sb(stack),
            state=[["absorbed", f"({pr}, {ps})"], ["span so far", span]])
    stack.append((p, span))
    spans.append(span)
    add(act=2, code="fast", line=5,
        note=f"Push ({p}, {span}); span for day {i} is {span}.",
        pointers={"i": i},
        marks={**marks_upto(i, good=list(range(i - span + 1, i + 1))), str(i): "good"},
        window=[i - span + 1, i], sidebar=sb(stack),
        state=[["day", i], ["span", span]])
add(act=2, code="fast", line=5,
    note=f"Spans = {spans}. Each day was pushed and popped once across the whole stream.",
    marks={str(i): "good" for i in range(len(prices))}, sidebar=sb(stack),
    state=[["spans", str(spans)], ["vs naive steps", work]],
    banner=f"Spans = {spans}   amortized O(1) per day")

# ---- Act 3: rising then falling edges ----
rising = [1, 2, 3, 4, 5]
stack = []
rspans = []
add(act=3, cells=rising, code="fast", line=0,
    intro="a strictly rising stream absorbs everything each step: spans 1,2,3,...",
    invariant="each new high pops the whole stack.",
    note="Edge case A: strictly rising [1,2,3,4,5]. Every price beats all before it, so "
    "each span is one longer: 1,2,3,4,5.",
    pointers={"i": 0}, marks={}, sidebar={"title": "stack (price, span)", "rows": []},
    state=[["spans", "[]"]])
for i, p in enumerate(rising):
    span = 1
    while stack and stack[-1][0] <= p:
        span += stack.pop()[1]
    stack.append((p, span))
    rspans.append(span)
    add(act=3, code="fast", line=5,
        note=f"day {i} price {p} absorbs all before it -> span {span}.",
        pointers={"i": i}, marks={str(k): "good" for k in range(i + 1)}, window=[0, i],
        sidebar=sb(stack), state=[["span", span]])
add(act=3, note="Edge case B: strictly falling [5,4,3,2,1] — nothing is ever <= today, so "
    "every span is 1.", cells=[5, 4, 3, 2, 1], code="fast", line=5,
    marks={str(k): "bad" for k in range(5)},
    sidebar={"title": "stack (price, span)", "rows": [[str(v), "span 1"] for v in [5, 4, 3, 2, 1]]},
    state=[["spans", "[1, 1, 1, 1, 1]"]],
    banner="Rising -> 1,2,3,4,5   Falling -> all 1")

trace = {
    "player": "linear",
    "title": "Online Stock Span - absorb dominated days into one growing span",
    "acts": ["Naive walk & waste", "The block rule", "Run the stream", "Edges: rising / falling"],
    "code": {"naive": NAIVE, "fast": FAST},
    "legend": [["active", "today's price"], ["good", "days inside the span"],
               ["bad", "blocked (span 1)"], ["dim", "earlier days"]],
    "cells": prices, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
