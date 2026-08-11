"""Rich full-arc trace for Edit Distance (grid renderer).
Arc: brute (branch every edit, subproblems overlap) -> fill the (m+1)x(n+1)
table -> answer + edge. Mirrors the tabulation in solution.py. Writes trace.json.
"""
import json
import os

W1, W2 = "horse", "ros"
M, N = len(W1), len(W2)
frames = []

CODE = [
    "dp = [[0]*(n+1) for _ in range(m+1)]",
    "for j in range(n+1): dp[0][j] = j",
    "for i in range(m+1): dp[i][0] = i",
    "for i in range(1, m+1):",
    "    for j in range(1, n+1):",
    "        if w1[i-1] == w2[j-1]: dp[i][j] = dp[i-1][j-1]",
    "        else: dp[i][j] = 1 + min(diag, left, up)",
    "return dp[m][n]",
]

# row/col labels: index 0 is the empty prefix, then the characters
ROWLABELS = ["·"] + list(W1)      # "·" = the empty prefix
COLLABELS = ["·"] + list(W2)


def add(**f):
    frames.append(f)


def blank():
    return [[None] * (N + 1) for _ in range(M + 1)]


# ---- Act 0: brute force ----
add(act=0, rows=blank(), rowLabels=ROWLABELS, colLabels=COLLABELS, code=None,
    intro="how the same (prefix, prefix) pair gets re-solved down many edit paths.",
    invariant="dist(i,j) = edits to turn w1[:i] into w2[:j].",
    note="Brute force: at each step try all three edits — replace, delete, insert "
    "— and recurse. Turning \"horse\" into \"ros\" branches three ways per character.",
    marks={f"{M},{N}": "active"}, state=[["turn", "horse → ros"], ["choices", "replace / delete / insert"]])
add(act=0, note="Different edit orders keep asking the same subproblem — e.g. dist(2,1) "
    "\"hor→r\" is reached many ways and re-solved each time. That overlap is the waste.",
    marks={"2,1": "bad", f"{M},{N}": "active", "0,0": "active"},
    state=[["recomputed", "dist(2,1) …"], ["cost", "exponential"]])

# ---- Act 1: fill the table ----
dp = [[0] * (N + 1) for _ in range(M + 1)]
add(act=1, rows=blank(), code="tab", line=0,
    intro="each cell filled ONCE from three neighbors: diagonal, left, up.",
    invariant="dp[i][j] computed from dp[i-1][j-1], dp[i][j-1], dp[i-1][j].",
    note="Seed the borders. Row 0: turning \"\" into w2[:j] takes j inserts. "
    "Column 0: turning w1[:i] into \"\" takes i deletes.",
    marks={}, state=[["borders", "row/col = index"]])
for j in range(N + 1):
    dp[0][j] = j
    add(act=1, code="tab", line=1, note=f"dp[0][{j}] = {j} (insert {j} char(s) of \"{W2}\").",
        set={f"0,{j}": j}, marks={f"0,{j}": "good"}, state=[[f"dp[0][{j}]", j]])
for i in range(1, M + 1):
    dp[i][0] = i
    add(act=1, code="tab", line=2, note=f"dp[{i}][0] = {i} (delete {i} char(s) of \"{W1}\").",
        set={f"{i},0": i}, marks={f"{i},0": "good"}, state=[[f"dp[{i}][0]", i]])
# fill interior
for i in range(1, M + 1):
    for j in range(1, N + 1):
        diag = dp[i - 1][j - 1]
        left = dp[i][j - 1]
        up = dp[i - 1][j]
        a, b = W1[i - 1], W2[j - 1]
        if a == b:
            dp[i][j] = diag
            note = (f"w1[{i-1}]='{a}' == w2[{j-1}]='{b}': free move, "
                    f"dp[{i}][{j}] = diag {diag} = {dp[i][j]}.")
            marks = {f"{i-1},{j-1}": "active", f"{i},{j}": "good"}
        else:
            dp[i][j] = 1 + min(diag, left, up)
            note = (f"'{a}' != '{b}': pay 1 + min(diag {diag}, left {left}, up {up}) "
                    f"= {dp[i][j]}.")
            marks = {f"{i-1},{j-1}": "active", f"{i},{j-1}": "active",
                     f"{i-1},{j}": "active", f"{i},{j}": "good"}
        add(act=1, code="tab", line=5 if a == b else 6, note=note,
            set={f"{i},{j}": dp[i][j]}, marks=marks,
            state=[["diag(replace)", diag], ["left(insert)", left], ["up(delete)", up],
                   [f"dp[{i}][{j}]", dp[i][j]]])

# ---- Act 2: answer + edge ----
add(act=2, code="tab", line=7,
    intro="the bottom-right cell reconciles both whole words.",
    invariant="dp[m][n] already folded every edit path into one minimum.",
    note=f"dp[{M}][{N}] = {dp[M][N]} — the fewest edits from \"{W1}\" to \"{W2}\", "
    "each subproblem solved once.",
    marks={f"{M},{N}": "good"}, state=[["answer", dp[M][N]]],
    banner=f"Edit distance(\"{W1}\", \"{W2}\") = {dp[M][N]}")

# edge: equal words -> 0 edits. "abc" -> "abc"
E1, E2 = "abc", "abc"
em, en = len(E1), len(E2)
edp = [[0] * (en + 1) for _ in range(em + 1)]
for j in range(en + 1):
    edp[0][j] = j
for i in range(em + 1):
    edp[i][0] = i
for i in range(1, em + 1):
    for j in range(1, en + 1):
        if E1[i - 1] == E2[j - 1]:
            edp[i][j] = edp[i - 1][j - 1]
        else:
            edp[i][j] = 1 + min(edp[i - 1][j - 1], edp[i][j - 1], edp[i - 1][j])
add(act=2, rows=edp, rowLabels=["·"] + list(E1), colLabels=["·"] + list(E2),
    code="tab", line=7,
    note="Edge case: identical words. Every character matches on the diagonal, so the "
    "cost never grows — the whole diagonal stays 0 and the answer is 0.",
    marks={f"{em},{en}": "good"}, state=[["answer", edp[em][en]]],
    banner="Identical words → 0 edits")

trace = {
    "player": "grid",
    "title": "Edit Distance - fill each (prefix, prefix) cell once",
    "acts": ["Brute: branch every edit", "Fill the table", "Answer + edge"],
    "code": {"tab": CODE},
    "legend": [["active", "neighbors this cell reads"], ["good", "filled / answer"],
               ["bad", "recomputed (waste)"]],
    "rows": blank(), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
