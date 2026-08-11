"""Full-arc trace for Cheapest Flights Within K Stops (tree renderer as a weighted graph).

Plain Dijkstra ignores the hop limit; Bellman-Ford in rounds bakes it in. Arc:
Dijkstra's trap -> the fix (rounds) -> run k+1 rounds -> edge case (a cheaper
route that needs one more hop than allowed). Nodes are hand-placed (x,y); `active`
= city being relaxed this round, `done` = its cheapest known price. Mirrors
solution.py. Writes trace.json.
"""
import json
import os

frames = []

CODE = [
    "dist = [INF]*n; dist[src] = 0",
    "for _ in range(k + 1):",
    "    curr = dist[:]        # snapshot",
    "    for u, v, price in flights:",
    "        if dist[u] + price < curr[v]:",
    "            curr[v] = dist[u] + price",
    "    dist = curr",
    "return dist[dst]",
]


def add(**f):
    frames.append(f)


# 4 cities, flights (u,v,price).  src=0, dst=3, k=1  -> answer 700.
POS = {0: (20, 40), 1: (170, 0), 2: (170, 150), 3: (320, 70)}
FLIGHTS = [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600], [2, 3, 200]]
N, SRC, DST, K = 4, 0, 3, 1

nodes = [{"id": nid, "val": nid, "x": POS[nid][0], "y": POS[nid][1]} for nid in POS]
edges = [[u, v] for u, v, p in FLIGHTS]
INF = float("inf")


def badge(dist):
    return {i: dist[i] for i in range(N) if dist[i] != INF}


# ---- Act 0: the trap — Dijkstra grabs the cheapest city, ignoring hops ----
add(act=0, nodes=nodes, edges=edges, code="dfs", line=0,
    intro="cheapest-first can lock in a price that used too many flights.",
    invariant="we must count flights, not just price.",
    note="With at most k=1 stop you may take 2 flights. Plain Dijkstra minimizes "
    "price but forgets that limit — it could reach 3 cheaply via a 3-flight route.",
    active=[SRC], done={SRC: 0}, state=[["src", SRC], ["dst", DST], ["max flights", K + 1]])
add(act=0, code="dfs", line=0,
    note="The tempting cheap route 0->1->2->3 costs 100+100+200 = 400, but that is "
    "3 flights (2 stops). Over budget. We are only allowed 2 flights here.",
    active=[3], done={0: 0, 1: 100, 2: 200, 3: 400},
    state=[["route 0-1-2-3", 400], ["flights used", 3]],
    banner="Cheapest by price can break the hop limit. Count flights per round instead.")

# ---- Act 1: the fix — relax in rounds, one flight per round ----
add(act=1, nodes=nodes, edges=edges, code="dfs", line=1,
    intro="after round i, a city's price uses at most i flights.",
    invariant="each round adds exactly one more flight, no more.",
    note="Bellman-Ford's structure: run k+1 rounds. Read prices from a snapshot of "
    "the previous round so no route sneaks in two flights inside one round.",
    active=[SRC], done={SRC: 0}, state=[["rounds to run", K + 1]])

# ---- Act 2: run k+1 rounds ----
dist = [INF] * N
dist[SRC] = 0
for rnd in range(K + 1):
    curr = dist[:]
    add(act=2, code="dfs", line=2,
        note=f"Round {rnd + 1}: snapshot last round's prices, then relax every flight "
        "reading only from that snapshot.",
        active=[], done=badge(dist), state=[["round", rnd + 1], ["reading", "snapshot"]])
    for u, v, price in FLIGHTS:
        if dist[u] != INF and dist[u] + price < curr[v]:
            curr[v] = dist[u] + price
            add(act=2, code="dfs", line=5,
                note=f"Flight {u}->{v} costs {price}: {dist[u]}+{price} = {curr[v]} "
                f"beats city {v}'s old price. Update it.",
                active=[v], done={**badge(dist), v: curr[v]},
                state=[["round", rnd + 1], ["update", f"city {v} = {curr[v]}"]])
    dist = curr
    add(act=2, code="dfs", line=6,
        note=f"End of round {rnd + 1}. These prices each use at most {rnd + 1} flights.",
        active=[], done=badge(dist), state=[["round done", rnd + 1]])

ans = dist[DST]
add(act=2, code="dfs", line=7,
    note=f"After {K + 1} rounds the cheapest price to city {DST} using at most "
    f"{K + 1} flights is {ans} (route 0->1->3: 100+600).",
    active=[DST], done=badge(dist), state=[["answer", ans]],
    banner=f"Cheapest within {K} stops = {ans}")

# ---- Act 3: edge case — cheaper route exists but needs one more hop ----
# f3: 0->1->2->3 costs 3 (3 flights); direct 0->3 costs 10. k=1 forbids the cheap one.
POS_B = {0: (20, 70), 1: (130, 0), 2: (250, 0), 3: (330, 70)}
FL_B = [[0, 1, 1], [1, 2, 1], [2, 3, 1], [0, 3, 10]]
nodes_b = [{"id": nid, "val": nid, "x": POS_B[nid][0], "y": POS_B[nid][1]} for nid in POS_B]
edges_b = [[u, v] for u, v, p in FL_B]
NB, KB = 4, 1
add(act=3, nodes=nodes_b, edges=edges_b, code="dfs", line=1,
    intro="the hop budget can force a pricier direct flight.",
    invariant="a route only counts if its flight count fits k+1.",
    note="Edge case: 0->1->2->3 costs just 3, but that is 3 flights. With k=1 "
    "(2 flights max) it is off-limits, so the direct 0->3 for 10 wins.",
    active=[0], done={0: 0}, state=[["cheap route", 3], ["its flights", 3], ["allowed", KB + 1]])
# Run the real rounds for the edge case to confirm the number.
distb = [INF] * NB
distb[0] = 0
for _ in range(KB + 1):
    c = distb[:]
    for u, v, p in FL_B:
        if distb[u] != INF and distb[u] + p < c[v]:
            c[v] = distb[u] + p
    distb = c
add(act=3, code="dfs", line=7,
    note=f"Only {KB + 1} rounds run, so the 3-flight bargain never reaches city 3 in "
    f"time. Answer = {distb[3]} (the direct flight).",
    active=[3], done={i: distb[i] for i in range(NB) if distb[i] != INF},
    state=[["answer", distb[3]]],
    banner=f"Within {KB} stop = {distb[3]}  (cheap 3-hop route ignored)")

trace = {
    "player": "tree",
    "title": "Cheapest Flights - Dijkstra's trap, relax in rounds, run k+1, then the hop-limit edge case",
    "acts": ["Dijkstra ignores hops", "The fix: rounds", "Run k+1 rounds", "Edge case: over budget"],
    "code": {"dfs": CODE},
    "legend": [["active", "relaxing this city"], ["good", "cheapest price so far"]],
    "nodes": nodes, "edges": edges, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
