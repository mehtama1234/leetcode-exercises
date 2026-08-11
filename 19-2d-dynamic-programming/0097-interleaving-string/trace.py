"""Rich full-arc trace for Interleaving String (grid renderer).
Arc: brute (branch which string feeds the next s3 char, subproblems overlap) ->
fill a (m+1)x(n+1) boolean table -> answer + edge. The rolled 1-D solution in
solution.py is the same recurrence; here we show the full 2-D table so the
dependencies (up = from s1, left = from s2) are visible. Writes trace.json.
"""
import json
import os

S1, S2, S3 = "aab", "dbb", "aadbbb"   # kept short so the table stays readable
M, N = len(S1), len(S2)
assert M + N == len(S3)
frames = []

CODE = [
    "dp = [[False]*(n+1) for _ in range(m+1)]",
    "dp[0][0] = True",
    "for i in range(m+1):",
    "    for j in range(n+1):",
    "        up   = dp[i-1][j] and s1[i-1]==s3[i+j-1]   # took from s1",
    "        left = dp[i][j-1] and s2[j-1]==s3[i+j-1]   # took from s2",
    "        dp[i][j] = up or left",
    "return dp[m][n]",
]

# dp[i][j]: can s1[:i] + s2[:j] interleave to s3[:i+j]?
ROWLABELS = ["·"] + list(S1)      # row i uses s1[i-1]
COLLABELS = ["·"] + list(S2)      # col j uses s2[j-1]


def add(**f):
    frames.append(f)


def blank():
    return [[None] * (N + 1) for _ in range(M + 1)]


def fmt(b):
    return "T" if b else "F"


# ---- Act 0: brute ----
add(act=0, rows=blank(), rowLabels=ROWLABELS, colLabels=COLLABELS, code=None,
    intro="how the same (i chars of s1, j chars of s2) state gets re-explored.",
    invariant="dp[i][j] = can s1[:i] + s2[:j] build s3[:i+j]?",
    note="Brute force: to place s3's next character, draw it from s1 or from s2 "
    "(whichever offers it) and recurse. That two-way branch spans a whole tree.",
    marks={"0,0": "active"}, state=[["build", "\"aadbbb\" from \"aab\"+\"dbb\""], ["draw", "from s1 / s2"]])
add(act=0, note="The third pointer k = i+j is derived, so many branches land on the "
    "same (i,j) state — e.g. dp[1][1] is reached two ways and re-solved. That is the waste.",
    marks={"1,1": "bad", "0,0": "active"},
    state=[["recomputed", "state(1,1) …"], ["cost", "exponential"]])

# ---- Act 1: fill the table ----
dp = [[False] * (N + 1) for _ in range(M + 1)]
dp[0][0] = True
add(act=1, rows=blank(), code="tab", line=1,
    intro="each cell = up (took from s1) OR left (took from s2).",
    invariant="dp[i][j] reads dp[i-1][j] and dp[i][j-1] against s3[i+j-1].",
    note="Seed dp[0][0] = T: empty + empty makes the empty prefix of s3.",
    marks={"0,0": "good"}, set={"0,0": "T"}, state=[["dp[0][0]", "T"]])
for i in range(M + 1):
    for j in range(N + 1):
        if i == 0 and j == 0:
            continue
        k = i + j
        up = i > 0 and dp[i - 1][j] and S1[i - 1] == S3[k - 1]
        left = j > 0 and dp[i][j - 1] and S2[j - 1] == S3[k - 1]
        dp[i][j] = up or left
        c = S3[k - 1]
        marks = {f"{i},{j}": "good" if dp[i][j] else "bad"}
        state = [["need s3[%d]" % (k - 1), c]]
        if i > 0:
            marks[f"{i-1},{j}"] = "active"
            state.append(["up: s1[%d]='%s' & dp" % (i - 1, S1[i - 1]), fmt(bool(up))])
        if j > 0:
            marks[f"{i},{j-1}"] = "active"
            state.append(["left: s2[%d]='%s' & dp" % (j - 1, S2[j - 1]), fmt(bool(left))])
        state.append([f"dp[{i}][{j}]", fmt(dp[i][j])])
        add(act=1, code="tab", line=6,
            note=f"To place s3[{k-1}]='{c}': up={fmt(bool(up))}, left={fmt(bool(left))} "
            f"-> dp[{i}][{j}] = {fmt(dp[i][j])}.",
            set={f"{i},{j}": fmt(dp[i][j])}, marks=marks, state=state)

# ---- Act 2: answer + edge ----
add(act=2, code="tab", line=7,
    intro="the bottom-right cell asks: did we consume ALL of both strings?",
    invariant="dp[m][n] is true iff a full interleaving exists.",
    note=f"dp[{M}][{N}] = {fmt(dp[M][N])} — \"{S3}\" {'is' if dp[M][N] else 'is not'} "
    f"an interleaving of \"{S1}\" and \"{S2}\".",
    marks={f"{M},{N}": "good" if dp[M][N] else "bad"},
    state=[["answer", fmt(dp[M][N])]],
    banner=f"\"{S3}\" is an interleaving: {fmt(dp[M][N])}")

# edge: right length but impossible order. s1="ab", s2="cd", s3="abdc"
E1, E2, E3 = "ab", "cd", "abdc"
em, en = len(E1), len(E2)
edp = [[False] * (en + 1) for _ in range(em + 1)]
edp[0][0] = True
for i in range(em + 1):
    for j in range(en + 1):
        if i == 0 and j == 0:
            continue
        k = i + j
        u = i > 0 and edp[i - 1][j] and E1[i - 1] == E3[k - 1]
        le = j > 0 and edp[i][j - 1] and E2[j - 1] == E3[k - 1]
        edp[i][j] = u or le
add(act=2, rows=[[fmt(v) for v in row] for row in edp],
    rowLabels=["·"] + list(E1), colLabels=["·"] + list(E2),
    code="tab", line=7,
    note="Edge case: the length matches (2+2=4) but the order can't work — after "
    "\"ab\" the string needs \"dc\" while s2 only offers \"cd\". The corner is F.",
    marks={f"{em},{en}": "bad"}, state=[["answer", fmt(edp[em][en])]],
    banner="Right length, wrong order → F")

trace = {
    "player": "grid",
    "title": "Interleaving String - decide each (i,j) prefix state once",
    "acts": ["Brute: draw from s1 / s2", "Fill the table", "Answer + edge"],
    "code": {"tab": CODE},
    "legend": [["active", "up / left cell read"], ["good", "reachable (T)"],
               ["bad", "not reachable (F) / waste"]],
    "rows": blank(), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
