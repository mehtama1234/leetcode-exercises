"""Full-arc trace for Coin Change (grid renderer, dp[amount] as one row).
Arc: the choose-a-last-coin recurrence -> fill dp[0..amount] once -> answer ->
impossible edge case. Mirrors solution.py. Writes trace.json.
"""
import json
import os

coins = [1, 2, 5]
AMOUNT = 6  # answer 2: 5 + 1
INF = float("inf")
frames = []

CODE = [
    "dp = [0] + [inf]*amount",
    "for a in range(1, amount+1):",
    "    for c in coins:",
    "        if c <= a:",
    "            dp[a] = min(dp[a], dp[a-c] + 1)",
    "return dp[amount]",
]


def add(**f):
    frames.append(f)


# dp[a] = fewest coins to make a. Verified: 0 1 1 2 2 1 2
dp = [0] + [INF] * AMOUNT
for a in range(1, AMOUNT + 1):
    for c in coins:
        if c <= a and dp[a - c] + 1 < dp[a]:
            dp[a] = dp[a - c] + 1
assert dp == [0, 1, 1, 2, 2, 1, 2]

labels = [str(a) for a in range(AMOUNT + 1)]


def show(a):
    return "inf" if dp[a] == INF else dp[a]


def blank():
    return [[None] * (AMOUNT + 1)]


# ---- Act 0: the recurrence ----
add(act=0, rows=blank(), rowLabels=["coins"], colLabels=labels, code=None,
    intro="dp[a] answers 'fewest coins to make a', building up from 0.",
    invariant="dp[a] = 1 + the fewest for whatever remains after one coin.",
    note=f"Coins {coins}, target {AMOUNT}. To make amount a, try each coin c as the "
    "LAST coin used; that leaves a-c to make with the same coins.",
    marks={f"0,{AMOUNT}": "active"}, state=[["amount", AMOUNT], ["coins", str(coins)]])
add(act=0,
    note="Plain recursion re-solves the same remaining amount along many coin orders "
    "(3 = 1+2 and 2+1 both ask for dp[0]). That repetition is the waste; fill each "
    "dp[a] once instead.",
    marks={"0,3": "bad", "0,4": "bad"},
    state=[["dp[a]", "recomputed"], ["fix", "fill once"]])

# ---- Act 1: fill dp[0..amount] ----
add(act=1, rows=blank(), rowLabels=["coins"], colLabels=labels, code="dp", line=0,
    intro="each amount solved ONCE, smallest first, so dp[a-c] is always ready.",
    invariant="dp[a] = fewest coins to make exactly a (inf if impossible).",
    note="dp[0] = 0: making zero needs no coins. Everything else starts at inf "
    "(unknown / impossible).",
    set={"0,0": 0}, marks={"0,0": "good"}, state=[["dp[0]", 0]])
for a in range(1, AMOUNT + 1):
    best = INF
    pick = None
    for c in coins:
        if c <= a and dp[a - c] + 1 < best:
            best = dp[a - c] + 1
            pick = c
    add(act=1, code="dp", line=4,
        note=f"dp[{a}] = fewest. Best last coin is {pick}: dp[{a}-{pick}] "
        f"{show(a - pick)} + 1 = {dp[a]}.",
        set={f"0,{a}": dp[a]},
        marks={f"0,{a}": "good", f"0,{a - pick}": "active"},
        state=[["amount", a], ["last coin", pick], [f"dp[{a}]", dp[a]]])

# ---- Act 2: answer + impossible edge ----
add(act=2, code="dp", line=5,
    intro="dp[amount] is the whole answer, filled once.",
    invariant="every smaller amount was solved before this one.",
    note=f"dp[{AMOUNT}] = {dp[AMOUNT]} — a 5 and a 1. Each amount was solved exactly once.",
    marks={f"0,{AMOUNT}": "good", "0,5": "active", "0,1": "active"},
    state=[["answer", dp[AMOUNT]]],
    banner=f"Fewest coins for {AMOUNT} = {dp[AMOUNT]}  (5 + 1)")
# edge: coins=[2], amount=3 -> impossible
e_coins, e_amt = [2], 3
edp = [0] + [INF] * e_amt
for a in range(1, e_amt + 1):
    for c in e_coins:
        if c <= a and edp[a - c] + 1 < edp[a]:
            edp[a] = edp[a - c] + 1
assert edp[e_amt] == INF
add(act=2, rows=[[0 if edp[a] == 0 else ("inf" if edp[a] == INF else edp[a])
                  for a in range(e_amt + 1)]],
    rowLabels=["coins"], colLabels=[str(a) for a in range(e_amt + 1)],
    code="dp", line=5,
    note="Edge case: coins [2], amount 3. Odd amounts stay inf forever — no combination "
    "of 2s makes 3 — so the answer is -1.",
    marks={"0,3": "bad"}, state=[["dp[3]", "inf"], ["answer", -1]],
    banner="No combination -> -1")

trace = {
    "player": "grid",
    "title": "Coin Change - solve each amount once, smallest first",
    "acts": ["The recurrence", "Fill dp[0..amount]", "Answer + impossible edge"],
    "code": {"dp": CODE},
    "legend": [["active", "the amount we build on (a-c)"], ["good", "solved / answer"], ["bad", "impossible / waste"]],
    "rows": blank(), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
