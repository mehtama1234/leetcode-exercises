"""Rich full-arc trace for Target Sum (grid renderer).
Arc: brute (branch +/- on every number, states overlap) -> reduce to subset-sum
count and fill a numbers x sum table -> answer + edge. solution.py rolls the
subset-sum to 1-D; here each number is its own row so the "skip = row above,
take = same row shifted left by the number" dependency is visible. Writes trace.json.
"""
import json
import os

NUMS = [1, 1, 1, 1, 1]
TARGET = 3
TOTAL = sum(NUMS)
# subset-sum reduction: need = (total + target) / 2
NEED = (TOTAL + TARGET) // 2       # = 4
K = len(NUMS)
frames = []

CODE = [
    "need = (sum(nums) + target) // 2",
    "dp = [0]*(need+1); dp[0] = 1",
    "for x in nums:",
    "    for s in range(need, x-1, -1):",
    "        dp[s] += dp[s-x]        # subsets that include x",
    "return dp[need]",
]

# dp[i][s] = subsets of nums[:i] summing to s.
ROWLABELS = ["·"] + [str(x) for x in NUMS]
COLLABELS = [str(s) for s in range(NEED + 1)]
ROWS_TOTAL = K + 1


def add(**f):
    frames.append(f)


def blank():
    return [[None] * (NEED + 1) for _ in range(ROWS_TOTAL)]


# ---- Act 0: brute ----
add(act=0, rows=blank(), rowLabels=ROWLABELS, colLabels=COLLABELS, code=None,
    intro="how the same (index, running sum) state recurs across the ± tree.",
    invariant="ways(i, run) = sign choices for nums[i:] that hit the target.",
    note="Brute force: put + or - in front of each number and branch both ways. "
    "Two different prefixes can reach the same running sum yet each spawns a subtree.",
    marks={"0,0": "active"}, state=[["target", "+/- sum = 3"], ["branch", "+x / -x"]])
add(act=0, note="With five equal 1's, many sign choices reach the same running sum — "
    "the same (index, sum) state solved again and again. That overlap is the waste.",
    marks={"3,2": "bad", "0,0": "active"},
    state=[["recomputed", "ways(3, 2) …"], ["cost", "2^n"]])

# ---- Act 1: reduce + fill ----
# subset-sum count: dp[i][s]
dp2 = [[0] * (NEED + 1) for _ in range(ROWS_TOTAL)]
dp2[0][0] = 1
add(act=1, rows=blank(), code="tab", line=0,
    intro="reduce to: how many subsets sum to need? each cell = skip(up) + take(left by x).",
    invariant="dp[i][s] = subsets of nums[:i] summing to s.",
    note=f"Split into + and - groups. sum(P)-sum(N)=target and sum(P)+sum(N)={TOTAL}, "
    f"so sum(P) = ({TOTAL}+{TARGET})/2 = {NEED}. Now just COUNT subsets summing to {NEED}.",
    marks={"0,0": "good"}, set={"0,0": 1}, state=[["need = (total+target)/2", NEED], ["dp[·][0]", 1]])
for s in range(1, NEED + 1):
    add(act=1, code="tab", line=1, note=f"dp[·][{s}] = 0 (empty subset can't sum to {s}).",
        set={f"0,{s}": 0}, marks={f"0,{s}": "dim"}, state=[[f"dp[·][{s}]", 0]])
for i in range(1, ROWS_TOTAL):
    x = NUMS[i - 1]
    for s in range(0, NEED + 1):
        skip = dp2[i - 1][s]                 # don't include this number: row above
        if s >= x:
            take = dp2[i - 1][s - x]         # include it: row above, s-x  (0/1 subset)
            dp2[i][s] = skip + take
            marks = {f"{i-1},{s}": "active", f"{i-1},{s-x}": "active", f"{i},{s}": "good"}
            note = (f"num {x}, sum {s}: skip {skip} + take dp[{i-1}][{s-x}]={take} "
                    f"= {dp2[i][s]}.")
            state = [["num", x], ["skip(up)", skip], ["take(up-left)", take],
                     [f"dp[{i}][{s}]", dp2[i][s]]]
        else:
            dp2[i][s] = skip
            marks = {f"{i-1},{s}": "active", f"{i},{s}": "good"}
            note = (f"num {x} > sum {s}: can't include, dp[{i}][{s}] = skip {skip} "
                    f"= {dp2[i][s]}.")
            state = [["num", x], ["skip(up)", skip], [f"dp[{i}][{s}]", dp2[i][s]]]
        add(act=1, code="tab", line=4, note=note,
            set={f"{i},{s}": dp2[i][s]}, marks=marks, state=state)

# ---- Act 2: answer + edge ----
ans = dp2[K][NEED]
add(act=2, code="tab", line=5,
    intro="bottom-right: all numbers considered, sum = need.",
    invariant="dp[K][need] counted each subset once — that is the number of sign assignments.",
    note=f"dp[{K}][{NEED}] = {ans} — the number of ways to sign {NUMS} to reach {TARGET}.",
    marks={f"{K},{NEED}": "good"}, state=[["answer", ans]],
    banner=f"Ways to sign {NUMS} to {TARGET} = {ans}")

# edge: infeasible parity. nums=[1,2], target=2 -> total=3, total+target=5 odd -> 0
E_NUMS, E_TARGET = [1, 2], 2
e_total = sum(E_NUMS)
infeasible = (e_total + E_TARGET) % 2 != 0
# build a tiny 1-row display to show the parity gate
add(act=2, rows=[[None]], rowLabels=["·"], colLabels=["·"], code="tab", line=0,
    note=f"Edge case: nums={E_NUMS}, target={E_TARGET}. total+target = {e_total+E_TARGET} is odd, "
    "so no integer subset sum exists — the split is impossible, the answer is 0.",
    marks={"0,0": "dim"}, state=[["total+target", e_total + E_TARGET], ["parity", "odd → impossible"], ["answer", 0]],
    banner="Odd total+target → 0 ways")

trace = {
    "player": "grid",
    "title": "Target Sum - reduce to subset-sum count, one number per row",
    "acts": ["Brute: branch every sign", "Reduce + fill", "Answer + edge"],
    "code": {"tab": CODE},
    "legend": [["active", "skip(up) + take(up-left)"], ["good", "filled / answer"],
               ["bad", "recomputed (waste)"], ["dim", "zero / impossible"]],
    "rows": blank(), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
