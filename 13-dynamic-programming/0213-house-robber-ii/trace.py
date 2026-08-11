"""Full-arc trace for House Robber II (grid renderer).
Arc: the circle constraint -> split into two linear runs (drop-last, drop-first)
-> take the better -> edge. Mirrors solution.py. Writes trace.json.
"""
import json
import os

nums = [1, 2, 3, 1]  # answer 4
n = len(nums)
frames = []

CODE = [
    "def _rob_line(a):",
    "    take, skip = 0, 0",
    "    for m in a: take, skip = skip + m, max(take, skip)",
    "    return max(take, skip)",
    "return max(_rob_line(nums[:-1]), _rob_line(nums[1:]))",
]


def add(**f):
    frames.append(f)


def rob_line(a):
    """Return (answer, best[] per index) for a straight row."""
    dp = []
    for i in range(len(a)):
        p1 = dp[i - 1] if i >= 1 else 0
        p2 = dp[i - 2] if i >= 2 else 0
        dp.append(max(p1, p2 + a[i]))
    return (max(dp) if dp else 0), dp


a_drop_last = nums[:-1]   # [1, 2, 3]
a_drop_first = nums[1:]   # [2, 3, 1]
ansA, dpA = rob_line(a_drop_last)
ansB, dpB = rob_line(a_drop_first)
answer = max(ansA, ansB)
assert dpA == [1, 2, 4] and ansA == 4
assert dpB == [2, 3, 3] and ansB == 3
assert answer == 4

labels = [str(i) for i in range(n)]


def circle_row():
    return [list(nums)]


# ---- Act 0: the circle constraint ----
add(act=0, rows=circle_row(), rowLabels=["$"], colLabels=labels, code=None,
    intro="the houses form a CIRCLE, so the first and last are neighbors too.",
    invariant="house 0 and house n-1 can never both be robbed.",
    note="Same as House Robber, but the row is bent into a circle: house 0 touches "
    "house n-1. They can't both be robbed.",
    marks={"0,0": "active", f"0,{n-1}": "active"},
    state=[["houses", n], ["extra rule", "ends touch"]])
add(act=0,
    note="The only new constraint is that one adjacency. So every legal plan either "
    "skips the last house or skips the first. Solve both as plain straight rows and "
    "keep the better.",
    marks={"0,0": "bad", f"0,{n-1}": "bad"},
    state=[["split", "two linear runs"]])

# ---- Act 1: run A = drop the last house ----
add(act=1, rows=[list(a_drop_last)], rowLabels=["A $"],
    colLabels=[str(i) for i in range(len(a_drop_last))], code="dp", line=4,
    intro="run 1: houses 0..n-2 as a straight row (last house forbidden).",
    invariant="best[i] = most robbable from this sub-row's houses 0..i.",
    note=f"Run A uses houses {a_drop_last} (drop the last). Fill best[] left to right.",
    marks={}, state=[["row", str(a_drop_last)]])
for i in range(len(a_drop_last)):
    mk = {f"0,{i}": "good"}
    if i >= 1:
        mk[f"0,{i-1}"] = "active"
    add(act=1, rows=[list(a_drop_last)], rowLabels=["A best"],
        colLabels=[str(j) for j in range(len(a_drop_last))], code="dp", line=2,
        note=f"House {i} (${a_drop_last[i]}): best[{i}] = {dpA[i]}.",
        set={f"0,{k}": dpA[k] for k in range(i + 1)}, marks=mk,
        state=[[f"best[{i}]", dpA[i]], ["run A best", max(dpA[: i + 1])]])
add(act=1, rows=[list(dpA)], rowLabels=["A best"],
    colLabels=[str(j) for j in range(len(a_drop_last))], code="dp", line=3,
    note=f"Run A answer = {ansA} (rob houses 0 and 2: 1 + 3).",
    marks={f"0,{len(dpA)-1}": "good"}, state=[["run A", ansA]])

# ---- Act 2: run B = drop the first house ----
add(act=2, rows=[list(a_drop_first)], rowLabels=["B $"],
    colLabels=[str(i + 1) for i in range(len(a_drop_first))], code="dp", line=4,
    intro="run 2: houses 1..n-1 as a straight row (first house forbidden).",
    invariant="same recurrence, different window of houses.",
    note=f"Run B uses houses {a_drop_first} (drop the first). Same fill.",
    marks={}, state=[["row", str(a_drop_first)]])
for i in range(len(a_drop_first)):
    mk = {f"0,{i}": "good"}
    if i >= 1:
        mk[f"0,{i-1}"] = "active"
    add(act=2, rows=[list(a_drop_first)], rowLabels=["B best"],
        colLabels=[str(j + 1) for j in range(len(a_drop_first))], code="dp", line=2,
        note=f"House {i+1} (${a_drop_first[i]}): best[{i}] = {dpB[i]}.",
        set={f"0,{k}": dpB[k] for k in range(i + 1)}, marks=mk,
        state=[[f"best[{i}]", dpB[i]], ["run B best", max(dpB[: i + 1])]])
add(act=2, rows=[list(dpB)], rowLabels=["B best"],
    colLabels=[str(j + 1) for j in range(len(a_drop_first))], code="dp", line=3,
    note=f"Run B answer = {ansB} (rob house 2: value 3).",
    marks={"0,1": "good"}, state=[["run B", ansB]])

# ---- Act 3: combine + edge ----
add(act=3, rows=circle_row(), rowLabels=["$"], colLabels=labels, code="dp", line=4,
    intro="the circular answer is just the better of the two straight runs.",
    invariant="every legal circular plan lives in run A or run B.",
    note=f"Answer = max(run A {ansA}, run B {ansB}) = {answer}. That plan robs houses "
    "0 and 2 and never touches both ends.",
    marks={"0,0": "good", "0,2": "good"},
    state=[["run A", ansA], ["run B", ansB], ["answer", answer]],
    banner=f"Circular max = {answer}  = max({ansA}, {ansB})")
add(act=3, rows=[[5]], rowLabels=["$"], colLabels=["0"], code="dp", line=4,
    note="Edge case: one house. There is no other end to conflict with, so rob it — "
    "the answer is 5.",
    marks={"0,0": "good"}, state=[["answer", 5]], banner="Single house -> 5")

trace = {
    "player": "grid",
    "title": "House Robber II - circle splits into two straight runs",
    "acts": ["The circle rule", "Run A: drop last", "Run B: drop first", "Combine + edge"],
    "code": {"dp": CODE},
    "legend": [["active", "compared best"], ["good", "locked best / robbed"], ["bad", "the two ends (can't share)"]],
    "rows": circle_row(), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
