"""Full-arc trace for Best Time to Buy and Sell Stock: brute every buy/sell pair ->
the waste (re-scanning the past for a low buy) -> one pass tracking the min price
so far -> edge case (only-falling prices). Mirrors solution.py. Writes trace.json.
"""
import json
import os

prices = [7, 1, 5, 3, 6, 4]  # answer 5 (buy 1, sell 6)
frames = []

BRUTE = [
    "for i in range(n):",
    "    for j in range(i+1, n):",
    "        best = max(best, prices[j] - prices[i])",
    "return best",
]
FAST = [
    "min_price = inf",
    "for price in prices:",
    "    if price < min_price: min_price = price",
    "    else: best = max(best, price - min_price)",
    "return best",
]


def add(**f):
    frames.append(f)


# ---- Act 0: brute — every buy day vs every later sell day ----
work = 0
best = 0
best_pair = (0, 0)
add(act=0, cells=prices, labels=list(range(len(prices))), code="brute", line=0,
    intro="every buy day drags a sell pointer across the whole future after it.",
    invariant="best holds the largest profit among all buy/sell pairs seen so far.",
    note="Brute force: for each buy day, try every later sell day. Keep the best profit.",
    pointers={"buy": 0, "sell": 1},
    marks={"0": "active", "1": "dim"},
    state=[["buy", 0], ["sell", 1], ["best", 0], ["pairs", 0]])
for i in range(len(prices)):
    for j in range(i + 1, len(prices)):
        work += 1
        profit = prices[j] - prices[i]
        better = profit > best
        if better:
            best = profit
            best_pair = (i, j)
        if i == 0 or better:
            add(act=0, code="brute", line=2,
                note=f"buy day {i} ({prices[i]}), sell day {j} ({prices[j]}): profit "
                     f"{profit}. " + (f"New best {best}." if better else f"Best {best}."),
                pointers={"buy": i, "sell": j}, arc=[i, j],
                marks={str(i): "active", str(j): "good" if better else "dim"},
                state=[["buy", i], ["sell", j], ["profit", profit], ["best", best], ["pairs", work]])
add(act=0, code="brute", line=3,
    note=f"Best profit {best}: buy day {best_pair[0]}, sell day {best_pair[1]} — but it "
         f"cost {work} pairs.",
    pointers={"buy": best_pair[0], "sell": best_pair[1]}, arc=list(best_pair),
    marks={str(best_pair[0]): "good", str(best_pair[1]): "good"},
    state=[["best", best], ["pairs", work]])

# ---- Act 1: the waste ----
add(act=1,
    intro="the pair counter — each sell day re-scanned every earlier day for a low buy.",
    note=f"{work} pairs. For each sell day, brute re-hunts the whole past for the cheapest "
    "buy. But that cheapest price is one number we could just carry along.",
    marks={str(k): "dim" for k in range(len(prices))},
    state=[["pairs (brute)", work], ["pattern", "~ n*n / 2"]])
add(act=1,
    note="On any sell day, the only thing you want from history is the single lowest price "
    "before it. Track that minimum as you walk right — one pass, no looking back.",
    marks={str(k): "dim" for k in range(len(prices))},
    state=[["memory of past", "1 number"], ["pattern", "~ n"]])

# ---- Act 2: fast — one pass, min price so far ----
min_price = float("inf")
min_i = 0
best = 0
best_pair = (0, 0)
add(act=2, cells=prices, labels=list(range(len(prices))), code="fast", line=0,
    intro="one marker tracks the cheapest day so far; each day sells against it.",
    invariant="min_price is the lowest price at or before the current day.",
    note="Walk left to right. Remember the cheapest day so far; sell today against it.",
    pointers={"day": 0}, marks={"0": "active"},
    state=[["min so far", "inf"], ["best", 0]])
for i, price in enumerate(prices):
    if price < min_price:
        min_price = price
        min_i = i
        add(act=2, code="fast", line=2,
            note=f"day {i}: {price} is a new low. Remember it as the cheapest day to buy.",
            pointers={"day": i, "min": min_i}, marks={str(i): "active"},
            state=[["day", i], ["price", price], ["min so far", min_price], ["best", best]])
    else:
        profit = price - min_price
        better = profit > best
        if better:
            best = profit
            best_pair = (min_i, i)
        add(act=2, code="fast", line=3,
            note=f"day {i}: sell at {price} against min {min_price} → profit {profit}. "
                 + (f"New best {best}." if better else f"Best {best}."),
            pointers={"day": i, "min": min_i}, arc=[min_i, i],
            marks={str(min_i): "good" if better else "dim",
                   str(i): "good" if better else "active"},
            state=[["day", i], ["price", price], ["min so far", min_price],
                   ["profit", profit], ["best", best]])
a, b = best_pair
add(act=2, code="fast", line=4,
    note=f"One pass. Best profit {best}: buy day {a} ({prices[a]}), sell day {b} ({prices[b]}).",
    pointers={"buy": a, "sell": b}, arc=[a, b],
    marks={str(a): "good", str(b): "good"},
    state=[["best", best], ["passes", 1], ["vs brute pairs", work]],
    banner=f"Best profit {best}   buy {prices[a]} → sell {prices[b]}   — one pass vs {work} brute pairs")

# ---- Act 3: edge case, only-falling prices ----
edge = [7, 6, 4, 3, 1]  # answer 0 — never profitable
min_price = float("inf")
best = 0
add(act=3, cells=edge, labels=list(range(len(edge))), code="fast", line=0,
    intro="the min keeps dropping, so no sell ever beats its buy — the answer is 0.",
    invariant="min_price is the lowest price seen so far; best stays 0 if nothing profits.",
    note="Edge case: prices only fall. Every day is a new low, so no trade ever profits.",
    pointers={"day": 0}, marks={"0": "active"},
    state=[["min so far", "inf"], ["best", 0]])
for i, price in enumerate(edge):
    if price < min_price:
        min_price = price
        add(act=3, code="fast", line=2,
            note=f"day {i}: {price} is yet another new low — nothing to sell against.",
            pointers={"day": i}, marks={str(i): "bad"},
            state=[["day", i], ["price", price], ["min so far", min_price], ["best", best]])
add(act=3, code="fast", line=4,
    note="No day ever sold above its buy. Best profit is 0 — don't trade.",
    marks={str(k): "dim" for k in range(len(edge))},
    state=[["best", 0]],
    banner="Best profit 0   (prices only fall — no trade)")

trace = {
    "player": "linear",
    "title": "Best Time to Buy and Sell Stock — from every pair to one pass with a min",
    "acts": ["Brute force: every pair", "The waste",
             "Fast: track the min price", "Edge case: only falling"],
    "code": {"brute": BRUTE, "fast": FAST},
    "legend": [["active", "current day / min"], ["good", "buy/sell of the best trade"],
               ["bad", "new low (no sell)"], ["dim", "inactive"]],
    "cells": prices, "labels": list(range(len(prices))), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
