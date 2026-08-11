"""Full-arc trace for Reconstruct Itinerary (tree renderer as a directed graph).

Hierholzer's algorithm builds an Eulerian path (use every ticket once). Arc: the
naive trap (plain greedy can strand a ticket) -> the rule (walk till stuck, then
prepend) -> run it on a route that reuses an airport -> a simple linear edge case.
Airports are hand-placed nodes; edges are tickets. `active` = airport at the top
of the stack, `done` = its finalized slot in the route (1-based). Mirrors
solution.py's Hierholzer. Writes trace.json.
"""
import json
import os
import heapq
from collections import defaultdict

frames = []

CODE = [
    "for src, dst in tickets:",
    "    heappush(graph[src], dst)   # smallest dst first",
    "stack = ['JFK']; route = []",
    "while stack:",
    "    a = stack[-1]",
    "    if graph[a]:",
    "        stack.append(heappop(graph[a]))",
    "    else:",
    "        route.append(stack.pop())   # stuck: retreat",
    "return route[::-1]",
]


def add(**f):
    frames.append(f)


def build(pos, tickets):
    nodes = [{"id": a, "val": a, "x": pos[a][0], "y": pos[a][1]} for a in pos]
    edges = [[u, v] for u, v in tickets]
    return nodes, edges


# ---- Act 0: the trap — plain greedy can strand a ticket ----
# JFK->KUL, JFK->NRT, NRT->JFK.  Greedy-smallest from JFK picks KUL first -> dead
# end with NRT->JFK unused. Hierholzer avoids that by prepending on the way back.
POS_A = {"JFK": (150, 0), "KUL": (20, 140), "NRT": (280, 140)}
TIX_A = [["JFK", "KUL"], ["JFK", "NRT"], ["NRT", "JFK"]]
nodes_a, edges_a = build(POS_A, TIX_A)
add(act=0, nodes=nodes_a, edges=edges_a, code="dfs", line=1,
    intro="using every ticket once is an Eulerian path.",
    invariant="every ticket must be used exactly once.",
    note="Each ticket is a directed edge we must use once. From JFK the smallest "
    "next airport is KUL — but flying JFK->KUL first dead-ends and strands the "
    "NRT->JFK ticket.",
    active=["JFK"], done={}, state=[["at", "JFK"], ["tickets left", 3]])
add(act=0, code="dfs", line=8,
    note="Naive greedy would get stuck at KUL with a ticket still unused. So we can't "
    "just commit to the smallest edge and forget it.",
    active=["KUL"], done={}, state=[["stuck at", "KUL"], ["tickets left", 1]],
    banner="Greedy-smallest alone can strand a ticket. Hierholzer fixes it by retreating.")

# ---- Act 1: the rule ----
add(act=1, nodes=nodes_a, edges=edges_a, code="dfs", line=3,
    intro="walk forward greedily; when stuck, prepend and back up.",
    invariant="an airport is finalized only when it has no unused ticket out.",
    note="Hierholzer: push JFK. Always follow the smallest unused ticket out of the "
    "top airport. When an airport has none left, it must be a trail end — pop it "
    "onto the route and back up. The route builds back-to-front.",
    active=["JFK"], done={}, state=[["stack", "[JFK]"], ["route", "[]"]])

# ---- Act 2: run Hierholzer on a graph that reuses an airport ----
# LeetCode example 2: JFK->ATL/SFO, SFO->ATL, ATL->JFK/SFO. Answer visits JFK twice.
POS_B = {"JFK": (60, 0), "ATL": (60, 160), "SFO": (280, 80)}
TIX_B = [["JFK", "SFO"], ["JFK", "ATL"], ["SFO", "ATL"], ["ATL", "JFK"], ["ATL", "SFO"]]
nodes_b, edges_b = build(POS_B, TIX_B)

graph = defaultdict(list)
for s, d in TIX_B:
    heapq.heappush(graph[s], d)

add(act=2, nodes=nodes_b, edges=edges_b, code="dfs", line=2,
    intro="the route fills from the end; final slots appear as badges.",
    invariant="each ticket, once flown, is gone from its airport's heap.",
    note="A route that must reuse JFK. Follow smallest tickets, prepend when stuck.",
    active=["JFK"], done={}, state=[["stack", "[JFK]"], ["route", "[]"]])

stack = ["JFK"]
route = []
EXPECTED = ["JFK", "ATL", "JFK", "SFO", "ATL", "SFO"]
total = len(TIX_B) + 1  # route length
while stack:
    a = stack[-1]
    if graph[a]:
        nxt = heapq.heappop(graph[a])
        stack.append(nxt)
        add(act=2, code="dfs", line=6,
            note=f"{a} still has tickets — fly the smallest, {a}->{nxt}. Push {nxt}.",
            active=[nxt], done={}, state=[["stack", str(stack)],
                                          ["route", str(route[::-1])]])
    else:
        popped = stack.pop()
        route.append(popped)
        slot = total - len(route) + 1  # this airport's 1-based place in the final route
        # Badge each already-finalized airport with the smallest slot it occupies.
        done = {}
        for i, ap in enumerate(route):
            done[ap] = total - i  # route is back-to-front; slot in final route
        add(act=2, code="dfs", line=8,
            note=f"{popped} has no ticket left — it's a trail end. Prepend it to the "
            f"route (final slot {slot}).",
            active=[stack[-1]] if stack else [],
            done=done,
            state=[["stack", str(stack)], ["route", str(route[::-1])]])

result = route[::-1]
assert result == EXPECTED, result
# Final badges: each airport's 1-based position(s) in the finished route.
slots = defaultdict(list)
for i, ap in enumerate(result):
    slots[ap].append(str(i + 1))
final_badge = {ap: ",".join(s) for ap, s in slots.items()}
add(act=2, code="dfs", line=9,
    note=f"Reverse the built route -> {result}. Every ticket used once, smallest "
    "lexical order.",
    active=[], done=final_badge,
    state=[["itinerary", " ".join(result)]],
    banner=f"Itinerary: {' -> '.join(result)}")

# ---- Act 3: edge case — a single straight line, no reuse ----
POS_C = {"JFK": (20, 60), "MUC": (110, 60), "LHR": (200, 60),
         "SFO": (290, 60), "SJC": (360, 60)}
TIX_C = [["MUC", "LHR"], ["JFK", "MUC"], ["SFO", "SJC"], ["LHR", "SFO"]]
nodes_c, edges_c = build(POS_C, TIX_C)
add(act=3, nodes=nodes_c, edges=edges_c, code="dfs", line=3,
    intro="with no branching there is only one possible trip.",
    invariant="a linear chain has exactly one Eulerian path.",
    note="Edge case: tickets form a single chain JFK->MUC->LHR->SFO->SJC. No choices, "
    "so Hierholzer just walks it straight through.",
    active=["JFK"], done={}, state=[["shape", "straight line"]])
line_route = ["JFK", "MUC", "LHR", "SFO", "SJC"]
add(act=3, code="dfs", line=9,
    note=f"Only one trip exists: {line_route}.",
    active=[], done={ap: str(i + 1) for i, ap in enumerate(line_route)},
    state=[["itinerary", " ".join(line_route)]],
    banner=f"Itinerary: {' -> '.join(line_route)}")

trace = {
    "player": "tree",
    "title": "Reconstruct Itinerary - greedy's trap, Hierholzer's rule, a reused airport, then a straight line",
    "acts": ["Greedy can strand a ticket", "The rule", "Run it (reuses JFK)", "Edge case: straight line"],
    "code": {"dfs": CODE},
    "legend": [["active", "top of stack"], ["good", "final slot in route"]],
    "nodes": nodes_b, "edges": edges_b, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
