"""Rich full-arc trace for Burst Balloons (grid renderer, interval DP).
Arc: brute (pick which to pop FIRST -> neighbours keep shifting, subproblems
overlap) -> fill dp[l][r] by increasing gap, asking which balloon pops LAST ->
answer + edge. dp[l][r] = coins from bursting everything strictly between walls
l and r. Mirrors the tabulation in solution.py. Writes trace.json.
"""
import json
import os

NUMS = [3, 1, 5]
BALLOONS = [1] + NUMS + [1]          # virtual 1 walls at both ends
N = len(BALLOONS)                    # = 5
frames = []

CODE = [
    "balloons = [1] + nums + [1]",
    "dp = [[0]*n for _ in range(n)]",
    "for gap in range(2, n):          # widen the open interval",
    "    for l in range(0, n-gap):",
    "        r = l + gap",
    "        dp[l][r] = max(",
    "            balloons[l]*balloons[k]*balloons[r]",
    "            + dp[l][k] + dp[k][r]   # k bursts LAST",
    "            for k in range(l+1, r))",
    "return dp[0][n-1]",
]

# rows/cols indexed by wall position 0..n-1; label shows the balloon value there
ROWLABELS = [f"{i}:{BALLOONS[i]}" for i in range(N)]
COLLABELS = [f"{i}:{BALLOONS[i]}" for i in range(N)]


def add(**f):
    frames.append(f)


def blank():
    return [[None] * N for _ in range(N)]


# ---- Act 0: brute ----
add(act=0, rows=blank(), rowLabels=ROWLABELS, colLabels=COLLABELS, code=None,
    intro="how thinking 'which balloon FIRST' keeps the neighbours moving and overlaps subproblems.",
    invariant="dp[l][r] = coins from bursting everything strictly between walls l and r.",
    note="Brute force: try popping each balloon FIRST. But once it's gone the neighbours "
    "shift, so the left and right pieces are no longer independent — a messy tangle.",
    marks={"0,4": "active"}, state=[["balloons", str(NUMS)], ["pick", "which pops first?"]])
add(act=0, note="Flip it: ask which balloon bursts LAST in an interval. When k is last, "
    "walls l and r are fixed, splitting into independent (l,k) and (k,r). Without this, "
    "the same interval is re-solved many ways — the waste.",
    marks={"1,3": "bad", "0,4": "active"},
    state=[["recomputed", "interval (1,3) …"], ["fix", "k bursts LAST"]])

# ---- Act 1: fill by increasing gap ----
dp = [[0] * N for _ in range(N)]
add(act=1, rows=blank(), code="tab", line=2,
    intro="fill shortest intervals first; dp[l][r] reads dp[l][k] (its row) + dp[k][r] (its column).",
    invariant="dp[l][r] = max over k of walls*balloon[k] + dp[l][k] + dp[k][r].",
    note="gap 1 means no balloon strictly between the walls, so those cells are 0 "
    "(the diagonal just above the main one).",
    marks={}, state=[["base", "empty interval = 0"]])
# show the gap==1 zero cells (l, l+1)
for l in range(N - 1):
    r = l + 1
    add(act=1, code="tab", line=2, note=f"dp[{l}][{r}] = 0 (no balloon between walls {l} and {r}).",
        set={f"{l},{r}": 0}, marks={f"{l},{r}": "dim"}, state=[[f"dp[{l}][{r}]", 0]])

for gap in range(2, N):
    for l in range(0, N - gap):
        r = l + gap
        best = None
        best_k = None
        for k in range(l + 1, r):
            val = BALLOONS[l] * BALLOONS[k] * BALLOONS[r] + dp[l][k] + dp[k][r]
            if best is None or val > best:
                best = val
                best_k = k
        dp[l][r] = best
        k = best_k
        gain = BALLOONS[l] * BALLOONS[k] * BALLOONS[r]
        add(act=1, code="tab", line=7,
            note=f"dp[{l}][{r}]: best k={k} bursts last -> walls {BALLOONS[l]}*{BALLOONS[k]}*"
            f"{BALLOONS[r]} = {gain}, + dp[{l}][{k}]={dp[l][k]} + dp[{k}][{r}]={dp[k][r]} = {best}.",
            set={f"{l},{r}": best},
            marks={f"{l},{r}": "good", f"{l},{k}": "active", f"{k},{r}": "active"},
            state=[["gap", gap], ["last k", k], ["walls product", gain],
                   ["left dp[l][k]", dp[l][k]], ["right dp[k][r]", dp[k][r]],
                   [f"dp[{l}][{r}]", best]])

# ---- Act 2: answer + edge ----
ans = dp[0][N - 1]
add(act=2, code="tab", line=9,
    intro="the widest interval — both walls are the virtual 1s — is the whole answer.",
    invariant="dp[0][n-1] already tried every 'last balloon', each interval solved once.",
    note=f"dp[0][{N-1}] = {ans} — the most coins from bursting {NUMS} in the best order.",
    marks={f"0,{N-1}": "good"}, state=[["answer", ans]],
    banner=f"Max coins from {NUMS} = {ans}")

# edge: single balloon [5] -> pop it between two 1-walls -> 1*5*1 = 5
E_NUMS = [5]
E_BAL = [1] + E_NUMS + [1]
en = len(E_BAL)                      # 3
edp = [[0] * en for _ in range(en)]
for gap in range(2, en):
    for l in range(0, en - gap):
        r = l + gap
        edp[l][r] = max(E_BAL[l] * E_BAL[k] * E_BAL[r] + edp[l][k] + edp[k][r]
                        for k in range(l + 1, r))
add(act=2, rows=[[v if (v != 0 or (i < j)) else 0 for j, v in enumerate(row)] for i, row in enumerate(edp)],
    rowLabels=[f"{i}:{E_BAL[i]}" for i in range(en)],
    colLabels=[f"{i}:{E_BAL[i]}" for i in range(en)], code="tab", line=9,
    note="Edge case: one balloon worth 5. Its neighbours are the two virtual walls, so "
    "bursting it earns 1*5*1 = 5.",
    marks={f"0,{en-1}": "good"}, state=[["answer", edp[0][en - 1]]],
    banner="Single balloon [5] → 5 coins")

trace = {
    "player": "grid",
    "title": "Burst Balloons - interval DP on which balloon pops LAST",
    "acts": ["Brute: which pops first?", "Fill by interval length", "Answer + edge"],
    "code": {"tab": CODE},
    "legend": [["active", "left dp[l][k] + right dp[k][r]"], ["good", "filled / answer"],
               ["bad", "re-solved interval (waste)"], ["dim", "empty interval = 0"]],
    "rows": blank(), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
