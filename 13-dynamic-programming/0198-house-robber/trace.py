"""Full-arc trace for House Robber (grid renderer, houses + best[] as one row).
Arc: the rob-or-skip choice -> fill best[] once per house -> answer -> edge.
Mirrors the DP in solution.py. Writes trace.json.
"""
import json
import os

nums = [2, 7, 9, 3, 1]  # answer 12: rob houses 0, 2, 4 -> 2 + 9 + 1
n = len(nums)
frames = []

CODE = [
    "take, skip = 0, 0",
    "for money in nums:",
    "    take, skip = skip + money, max(take, skip)",
    "return max(take, skip)",
]


def add(**f):
    frames.append(f)


# dp[i] = best total robbing houses 0..i. dp[i] = max(dp[i-1], dp[i-2]+nums[i]).
dp = []
for i in range(n):
    a = dp[i - 1] if i >= 1 else 0
    b = (dp[i - 2] if i >= 2 else 0) + nums[i]
    dp.append(max(a, b))
assert dp == [2, 7, 11, 11, 12]

labels = [str(i) for i in range(n)]


def money_row():
    return [list(nums)]


def blank():
    return [[None] * n]


# ---- Act 0: the rule (money row) ----
add(act=0, rows=money_row(), rowLabels=["$"], colLabels=labels, code=None,
    intro="each house is a rob-or-skip choice; robbing one blocks its neighbor.",
    invariant="you can never take two houses that sit next to each other.",
    note="The houses in a row, each holding some money. You cannot rob two adjacent "
    "houses. We want the largest total.",
    marks={"0,0": "active"}, state=[["houses", n], ["rule", "no two neighbors"]])
add(act=0,
    note="At each house you either ROB it (take its money, then you must skip the "
    "next) or SKIP it. best(i) = max(best(i-1), best(i-2) + money). Naive recursion "
    "re-solves the same best(i) in many branches.",
    marks={"0,2": "bad", "0,3": "bad"},
    state=[["choice", "rob / skip"], ["waste", "best(i) recomputed"]])

# ---- Act 1: fill best[] once per house ----
add(act=1, rows=blank(), rowLabels=["best"], colLabels=labels, code="dp", line=0,
    intro="one running best per house, each computed once left to right.",
    invariant="best[i] = most money robbable from houses 0..i.",
    note="Start with nothing taken. best[i] compares skipping house i (keep best[i-1]) "
    "against robbing it (best[i-2] + money[i]).",
    marks={}, state=[["take", 0], ["skip", 0]])
for i in range(n):
    prev1 = dp[i - 1] if i >= 1 else 0
    prev2 = dp[i - 2] if i >= 2 else 0
    rob = prev2 + nums[i]
    mk = {f"0,{i}": "good"}
    if i >= 1:
        mk[f"0,{i-1}"] = "active"
    if i >= 2:
        mk[f"0,{i-2}"] = "active"
    add(act=1, code="dp", line=2,
        note=f"House {i} (${nums[i]}): rob = best[{i-2}] {prev2} + {nums[i]} = {rob} "
        f"vs skip = best[{i-1}] {prev1}. best[{i}] = {dp[i]}.",
        set={f"0,{i}": dp[i]}, marks=mk,
        state=[["rob here", rob], ["skip here", prev1], [f"best[{i}]", dp[i]]])

# ---- Act 2: answer + edge ----
add(act=2, code="dp", line=3,
    intro="the last house's best already folded in every earlier choice.",
    invariant="best[n-1] is the whole answer.",
    note=f"best[{n-1}] = {dp[n-1]} — that plan robs houses 0, 2, 4 (2 + 9 + 1). No two "
    "are neighbors.",
    marks={f"0,{n-1}": "good", "0,0": "good", "0,2": "good"},
    state=[["answer", dp[n - 1]]],
    banner=f"Max robbed = {dp[n-1]}  (houses 0, 2, 4)")
add(act=2, rows=[[5]], rowLabels=["$"], colLabels=["0"], code="dp", line=3,
    note="Edge case: one house holding 5. Nothing to conflict with, so rob it — "
    "the answer is 5.",
    marks={"0,0": "good"}, state=[["answer", 5]], banner="Single house -> 5")

trace = {
    "player": "grid",
    "title": "House Robber - one best-so-far per house instead of re-branching",
    "acts": ["The rob/skip rule", "Fill best[] once", "Answer + edge"],
    "code": {"dp": CODE},
    "legend": [["active", "the two we compare"], ["good", "locked best / robbed"], ["bad", "recomputed (waste)"]],
    "rows": money_row(), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
