"""Rich full-arc trace for Alien Dictionary (tree renderer as a directed graph).
Arc: extract constraints from adjacent words -> topo-sort the letters into an
order -> a contradiction edge case that has no valid order. Mirrors the
constraint extraction + Kahn's topo sort in solution.py. Letter nodes get
computed x,y; badges show in-degree then the placed order. Writes trace.json.
"""
import json
import os
from collections import deque

frames = []

CODE = [
    "for first, second in zip(words, words[1:]):",
    "    for a, b in zip(first, second):",
    "        if a != b:",
    "            adj[a].add(b)      # a comes before b",
    "            indegree[b] += 1",
    "            break              # only the FIRST diff matters",
    "ready = [c for c in letters if indegree[c] == 0]",
    "while ready:",
    "    c = ready.popleft(); order.append(c)",
    "    for nxt in adj[c]:",
    "        indegree[nxt] -= 1",
    "        if indegree[nxt] == 0: ready.append(nxt)",
    "return order if len(order)==len(letters) else ''",
]


def add(**f):
    frames.append(f)


# Positions for the 5 letters w,e,r,t,f laid out in a row.
LETTERS_A = ["w", "e", "r", "t", "f"]
POS_A = {c: (i * 90, 60) for i, c in enumerate(LETTERS_A)}


def nodes_of(pos):
    return [{"id": c, "val": c, "x": pos[c][0], "y": pos[c][1]} for c in pos]


WORDS_A = ["wrt", "wrf", "er", "ett", "rftt"]

# ---- Act 0: extract constraints ----
adj = {c: set() for c in LETTERS_A}
indeg = {c: 0 for c in LETTERS_A}
edges = []
nodes_a = nodes_of(POS_A)
add(act=0, nodes=nodes_a, edges=[], code="alien", line=0,
    intro="each adjacent word pair leaks ONE fact: the first place they differ.",
    invariant="letters before the first difference are equal and tell us nothing.",
    note="The words are sorted by an unknown alphabet. Compare each adjacent pair; "
    "their first differing letter proves 'this comes before that'. Badge = in-degree.",
    active=[], done={c: 0 for c in LETTERS_A},
    state=[["words", " ".join(WORDS_A)]])
pairs = list(zip(WORDS_A, WORDS_A[1:]))
for first, second in pairs:
    fact = None
    for a, b in zip(first, second):
        if a != b:
            if b not in adj[a]:
                adj[a].add(b)
                indeg[b] += 1
                edges.append([a, b])
            fact = (a, b)
            break
    if fact:
        a, b = fact
        add(act=0, code="alien", line=3, edges=[list(e) for e in edges],
            note=f"'{first}' before '{second}': first difference is '{a}' vs '{b}', "
            f"so '{a}' comes before '{b}'. Add edge {a} -> {b}.",
            active=[a, b], done=dict(indeg),
            state=[["pair", f"{first} < {second}"], ["fact", f"{a} < {b}"]])
add(act=0, code="alien", line=5, edges=[list(e) for e in edges],
    note=f"All pairs read. Constraints: " +
    ", ".join(f"{a}<{b}" for a, b in edges) + ". These edges form a directed graph "
    "over the letters.",
    active=[], done=dict(indeg),
    state=[["edges", len(edges)]])

# ---- Act 1: topo-sort the letters ----
add(act=1, nodes=nodes_a, edges=[list(e) for e in edges], code="alien", line=6,
    intro="a letter is placeable once nothing is required before it (in-degree 0).",
    invariant="the growing order respects every 'a before b' edge.",
    note="Topological sort (Kahn's). Start with letters that have nothing before "
    "them, place one, then relax its out-edges.",
    active=[], done=dict(indeg), state=[["placed", 0], ["of", len(indeg)]])
ready = deque(c for c in indeg if indeg[c] == 0)
order = []
badges = dict(indeg)
add(act=1, code="alien", line=6, edges=[list(e) for e in edges],
    note=f"Letters with in-degree 0 (nothing required first): {list(ready)}.",
    active=list(ready), done=dict(badges), state=[["ready", str(list(ready))]])
while ready:
    c = ready.popleft()
    order.append(c)
    badges[c] = len(order)  # its position in the order
    add(act=1, code="alien", line=8, edges=[list(e) for e in edges],
        note=f"Place '{c}' at position {len(order)}. Order so far: {''.join(order)}.",
        active=[c], done=dict(badges),
        state=[["placed", ''.join(order)]])
    for nxt in sorted(adj[c]):
        indeg[nxt] -= 1
        if badges.get(nxt) is None or not isinstance(badges[nxt], int) or \
                nxt not in order:
            if nxt not in order:
                badges[nxt] = indeg[nxt]
        add(act=1, code="alien", line=10, edges=[list(e) for e in edges],
            note=f"'{c}' done: drop in-degree of '{nxt}' to {indeg[nxt]}." +
            ("  Now ready." if indeg[nxt] == 0 else ""),
            active=[c, nxt], done=dict(badges),
            state=[["relax", f"{nxt} -> {indeg[nxt]}"]])
        if indeg[nxt] == 0:
            ready.append(nxt)
add(act=1, code="alien", line=12, edges=[list(e) for e in edges],
    note=f"All {len(order)} letters placed with no contradiction. The alien alphabet "
    f"is {''.join(order)}.",
    active=[], done=dict(badges), state=[["order", ''.join(order)]],
    banner=f"Alien order = {''.join(order)}")

# ---- Act 2: contradiction edge case ----
# words ["z","x","z"] : z<x (pair 1) and x<z (pair 2) -> a 2-cycle, no valid order
LETTERS_B = ["z", "x"]
POS_B = {"z": (0, 60), "x": (150, 60)}
nodes_b = nodes_of(POS_B)
WORDS_B = ["z", "x", "z"]
adjb = {c: set() for c in LETTERS_B}
indegb = {c: 0 for c in LETTERS_B}
edgesb = []
for first, second in zip(WORDS_B, WORDS_B[1:]):
    for a, b in zip(first, second):
        if a != b:
            if b not in adjb[a]:
                adjb[a].add(b)
                indegb[b] += 1
                edgesb.append([a, b])
            break
add(act=2, nodes=nodes_b, edges=[list(e) for e in edgesb], code="alien", line=3,
    intro="two pairs demand opposite orders — the graph has a cycle.",
    invariant="a cycle means no letter can be placed first; topo sort stalls.",
    note="Edge case: words z, x, z. Pair 1 says z<x; pair 2 says x<z. Both edges "
    "exist, forming a 2-cycle z <-> x.",
    active=["z", "x"], done=dict(indegb),
    state=[["z < x", "pair 1"], ["x < z", "pair 2"]])
readyb = deque(c for c in indegb if indegb[c] == 0)
add(act=2, code="alien", line=6, edges=[list(e) for e in edgesb],
    note="Both letters have in-degree 1, so the ready queue is empty. Nothing can be "
    "placed first.",
    active=["z", "x"], done=dict(indegb), state=[["ready", "[] (empty)"]])
add(act=2, code="alien", line=12, edges=[list(e) for e in edgesb],
    note="0 letters placed but 2 exist: the cycle blocks the sort. The constraints "
    "contradict, so there's no valid order -> return \"\".",
    active=["z", "x"], done=dict(indegb), state=[["placed", 0], ["of", 2]],
    banner='Contradiction: no valid order -> ""')

trace = {
    "player": "tree",
    "title": "Alien Dictionary - read 'before' facts from words, then topo-sort letters",
    "acts": ["Extract constraints", "Topo-sort the letters", "Edge: a contradiction"],
    "code": {"alien": CODE},
    "legend": [["active", "letters being compared / placed"],
               ["good", "in-degree, then order position (badge)"]],
    "nodes": nodes_a, "edges": [], "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
