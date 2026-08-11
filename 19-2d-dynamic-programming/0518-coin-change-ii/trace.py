"""Rich full-arc trace for Coin Change II (grid renderer).
Arc: brute (skip/take recursion re-solves states) -> fill a coins x amount count
table -> answer + edge. solution.py rolls this to 1-D; here each coin is its own
row so the "skip = row above, take = same row to the left" dependency is visible.
Writes trace.json.
"""
import json
import os

AMOUNT = 5
COINS = [1, 2, 5]
K = len(COINS)
frames = []

CODE = [
    "dp = [0]*(amount+1); dp[0] = 1",
    "for coin in coins:",
    "    for a in range(coin, amount+1):",
    "        dp[a] += dp[a-coin]     # ways that use this coin",
    "return dp[amount]",
]

# Table rows: row 0 = "no coins yet" (base), then one row per coin.
# dp[i][a] = ways to make amount a using coins[:i].
ROWLABELS = ["·"] + [str(c) for c in COINS]     # row i uses coins up to coins[i-1]
COLLABELS = [str(a) for a in range(AMOUNT + 1)]
ROWS_TOTAL = K + 1


def add(**f):
    frames.append(f)


def blank():
    return [[None] * (AMOUNT + 1) for _ in range(ROWS_TOTAL)]


# ---- Act 0: brute ----
add(act=0, rows=blank(), rowLabels=ROWLABELS, colLabels=COLLABELS, code=None,
    intro="how the same (coin index, remaining amount) state gets re-counted.",
    invariant="ways(i, a) = combinations of coins[i:] that sum to a.",
    note="Brute force: for each coin, either skip it and move on, or take one more "
    "of it and stay. Fixing the coin order stops 1+2 and 2+1 counting twice.",
    marks={f"{K},{AMOUNT}": "active"}, state=[["make", "5 from {1,2,5}"], ["choice", "skip / take"]])
add(act=0, note="Many skip/take paths reach the same (coin, remaining) pair — e.g. "
    "make 3 from {1,2} — and re-solve it. That repeated work is the waste.",
    marks={"2,3": "bad", f"{K},{AMOUNT}": "active"},
    state=[["recomputed", "ways(coin2, 3) …"], ["cost", "exponential"]])

# ---- Act 1: fill the table ----
# dp2[i][a]
dp2 = [[0] * (AMOUNT + 1) for _ in range(ROWS_TOTAL)]
dp2[0][0] = 1
add(act=1, rows=blank(), code="tab", line=0,
    intro="each cell = skip (cell directly above) + take (this row, coin steps left).",
    invariant="dp[i][a] = dp[i-1][a] + dp[i][a-coin].",
    note="Seed the base row: with NO coins there is exactly one way to make 0 (take "
    "nothing) and no way to make any positive amount.",
    marks={"0,0": "good"}, set={"0,0": 1},
    state=[["dp[·][0]", 1]])
for a in range(1, AMOUNT + 1):
    add(act=1, code="tab", line=0, note=f"dp[·][{a}] = 0 (no coins, can't make {a}).",
        set={f"0,{a}": 0}, marks={f"0,{a}": "dim"}, state=[[f"dp[·][{a}]", 0]])
# fill each coin row
for i in range(1, ROWS_TOTAL):
    coin = COINS[i - 1]
    for a in range(0, AMOUNT + 1):
        skip = dp2[i - 1][a]                 # don't use this coin: row above
        if a >= coin:
            take = dp2[i][a - coin]          # use this coin at least once: same row, left
            dp2[i][a] = skip + take
            marks = {f"{i-1},{a}": "active", f"{i},{a-coin}": "active",
                     f"{i},{a}": "good"}
            note = (f"coin {coin}, amount {a}: skip {skip} + take dp[{i}][{a-coin}]={take} "
                    f"= {dp2[i][a]}.")
            state = [["coin", coin], ["skip(up)", skip], ["take(left)", take],
                     [f"dp[{i}][{a}]", dp2[i][a]]]
        else:
            dp2[i][a] = skip
            marks = {f"{i-1},{a}": "active", f"{i},{a}": "good"}
            note = (f"coin {coin} > amount {a}: can't use it, dp[{i}][{a}] = skip {skip} "
                    f"= {dp2[i][a]}.")
            state = [["coin", coin], ["skip(up)", skip], [f"dp[{i}][{a}]", dp2[i][a]]]
        add(act=1, code="tab", line=3, note=note,
            set={f"{i},{a}": dp2[i][a]}, marks=marks, state=state)

# ---- Act 2: answer + edge ----
ans = dp2[K][AMOUNT]
add(act=2, code="tab", line=4,
    intro="the bottom-right cell: all coins available, full amount.",
    invariant="dp[K][amount] folded in every coin once, no order double-counted.",
    note=f"dp[{K}][{AMOUNT}] = {ans} — the number of coin combinations that make {AMOUNT}: "
    "5, 1+2+2, 1+1+1+2, 1+1+1+1+1.",
    marks={f"{K},{AMOUNT}": "good"}, state=[["answer", ans]],
    banner=f"Ways to make {AMOUNT} from {COINS} = {ans}")

# edge: amount 3 with only coin {2} -> 0
E_AMT, E_COINS = 3, [2]
ek = len(E_COINS)
edp = [[0] * (E_AMT + 1) for _ in range(ek + 1)]
edp[0][0] = 1
for i in range(1, ek + 1):
    coin = E_COINS[i - 1]
    for a in range(E_AMT + 1):
        edp[i][a] = edp[i - 1][a] + (edp[i][a - coin] if a >= coin else 0)
add(act=2, rows=edp, rowLabels=["·"] + [str(c) for c in E_COINS],
    colLabels=[str(a) for a in range(E_AMT + 1)], code="tab", line=4,
    note="Edge case: make 3 using only a coin worth 2. Even amounts are reachable "
    "(0, 2) but 3 is not — the corner stays 0.",
    marks={f"{ek},{E_AMT}": "dim"}, state=[["answer", edp[ek][E_AMT]]],
    banner="Make 3 from {2} → 0 ways")

trace = {
    "player": "grid",
    "title": "Coin Change II - count combinations, one coin per row",
    "acts": ["Brute: skip / take", "Fill the table", "Answer + edge"],
    "code": {"tab": CODE},
    "legend": [["active", "skip(up) + take(left)"], ["good", "filled / answer"],
               ["bad", "recomputed (waste)"], ["dim", "zero / unreachable"]],
    "rows": blank(), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
