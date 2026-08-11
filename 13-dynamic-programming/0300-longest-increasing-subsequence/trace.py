"""Full-arc trace for Longest Increasing Subsequence (grid renderer).
Arc: the "ends at i" recurrence -> fill dp[i] scanning predecessors -> answer ->
edge (all equal). Mirrors the O(n^2) DP in solution.py. Writes trace.json.
"""
import json
import os

nums = [10, 9, 2, 5, 3, 7, 101, 18]  # answer 4: [2,3,7,101]
n = len(nums)
frames = []

CODE = [
    "dp = [1] * n",
    "for i in range(n):",
    "    for j in range(i):",
    "        if nums[j] < nums[i]:",
    "            dp[i] = max(dp[i], dp[j] + 1)",
    "return max(dp)",
]


def add(**f):
    frames.append(f)


# dp[i] = length of longest increasing subseq ENDING at i. Verified.
dp = [1] * n
for i in range(n):
    for j in range(i):
        if nums[j] < nums[i]:
            dp[i] = max(dp[i], dp[j] + 1)
assert dp == [1, 1, 1, 2, 2, 3, 4, 4] and max(dp) == 4

labels = [str(v) for v in nums]  # show the values as column heads


def blank():
    return [[None] * n]


# ---- Act 0: the recurrence ----
add(act=0, rows=blank(), rowLabels=["dp"], colLabels=labels, code=None,
    intro="dp[i] = longest increasing run that ENDS exactly at value nums[i].",
    invariant="pinning the last element lets any smaller earlier value be its "
    "predecessor.",
    note=f"Values {nums}. dp[i] anchors the run's end at index i, so any earlier j "
    "with nums[j] < nums[i] can sit right before it.",
    marks={"0,0": "active"}, state=[["n", n], ["want", "longest increasing"]])
add(act=0,
    note="dp[i] = 1 + max(dp[j] for j < i with nums[j] < nums[i]), or 1 if none. "
    "Computed left to right so every dp[j] we read is already final.",
    marks={"0,3": "active", "0,2": "active"},
    state=[["rule", "1 + best smaller predecessor"]])

# ---- Act 1: fill dp[i] ----
add(act=1, rows=blank(), rowLabels=["dp"], colLabels=labels, code="dp", line=0,
    intro="each dp[i] scans the values to its left for a smaller predecessor.",
    invariant="dp[i] final before we move to i+1.",
    note="Every element alone is a length-1 run, so dp starts at 1 everywhere.",
    marks={}, state=[["start", "dp[i] = 1"]])
for i in range(n):
    best_j = None
    for j in range(i):
        if nums[j] < nums[i] and dp[j] + 1 == dp[i]:
            best_j = j
            break
    mk = {f"0,{i}": "good"}
    note_pred = "no smaller value to its left"
    if best_j is not None:
        mk[f"0,{best_j}"] = "active"
        note_pred = f"extends the run ending at {nums[best_j]} (dp {dp[best_j]})"
    add(act=1, code="dp", line=4,
        note=f"nums[{i}] = {nums[i]}: {note_pred}, so dp[{i}] = {dp[i]}.",
        set={f"0,{k}": dp[k] for k in range(i + 1)}, marks=mk,
        state=[[f"nums[{i}]", nums[i]], [f"dp[{i}]", dp[i]], ["best so far", max(dp[: i + 1])]])

# ---- Act 2: answer + edge ----
best_i = dp.index(max(dp))
add(act=2, rows=[list(dp)], rowLabels=["dp"], colLabels=labels, code="dp", line=5,
    intro="the longest run can end anywhere, so the answer is the largest dp value.",
    invariant="max(dp) is the LIS length.",
    note=f"The largest dp is {max(dp)} at value {nums[best_i]} — the run [2, 3, 7, 101]. "
    "The answer is a length, not a fixed cell.",
    marks={f"0,{best_i}": "good", "0,2": "active", "0,4": "active", "0,5": "active"},
    state=[["answer", max(dp)]],
    banner=f"LIS length = {max(dp)}  ([2, 3, 7, 101])")
edge = [7, 7, 7]
edp = [1] * len(edge)
for i in range(len(edge)):
    for j in range(i):
        if edge[j] < edge[i]:
            edp[i] = max(edp[i], edp[j] + 1)
assert max(edp) == 1
add(act=2, rows=[[1, 1, 1]], rowLabels=["dp"], colLabels=["7", "7", "7"],
    code="dp", line=5,
    note="Edge case: all equal. nums[j] < nums[i] is never true (strictly increasing), "
    "so every dp stays 1 and the answer is 1.",
    marks={"0,0": "good", "0,1": "good", "0,2": "good"},
    state=[["answer", 1]], banner="All equal -> 1")

trace = {
    "player": "grid",
    "title": "Longest Increasing Subsequence - dp[i] = best run ending at i",
    "acts": ["The 'ends at i' rule", "Fill dp[i]", "Answer + edge"],
    "code": {"dp": CODE},
    "legend": [["active", "predecessor / members"], ["good", "just-set dp[i]"], ["dim", "inactive"]],
    "rows": blank(), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
