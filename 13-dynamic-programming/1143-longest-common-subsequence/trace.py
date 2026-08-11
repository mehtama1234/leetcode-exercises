"""Full-arc trace for Longest Common Subsequence (grid renderer, 2-D table).
Arc: the match/drop recurrence -> fill the (m+1)x(n+1) table once -> answer ->
a no-overlap edge. Mirrors solution.py. Writes trace.json.
"""
import json
import os

t1 = "abcde"
t2 = "ace"  # LCS = "ace", length 3
m, n = len(t1), len(t2)
frames = []

CODE = [
    "dp = [[0]*(n+1) for _ in range(m+1)]",
    "for i in range(1, m+1):",
    "    for j in range(1, n+1):",
    "        if t1[i-1] == t2[j-1]:",
    "            dp[i][j] = dp[i-1][j-1] + 1",
    "        else:",
    "            dp[i][j] = max(dp[i-1][j], dp[i][j-1])",
    "return dp[m][n]",
]


def add(**f):
    frames.append(f)


# Full table. dp[i][j] = LCS length of t1[:i], t2[:j]. Verified.
dp = [[0] * (n + 1) for _ in range(m + 1)]
for i in range(1, m + 1):
    for j in range(1, n + 1):
        if t1[i - 1] == t2[j - 1]:
            dp[i][j] = dp[i - 1][j - 1] + 1
        else:
            dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
assert dp[m][n] == 3

# row 0 = empty prefix of t1; col 0 = empty prefix of t2
rowLabels = ["-"] + list(t1)
colLabels = ["-"] + list(t2)


def blank():
    return [[None] * (n + 1) for _ in range(m + 1)]


def zeros_seeded():
    """A table with row 0 and col 0 zeroed, interior blank."""
    g = blank()
    for j in range(n + 1):
        g[0][j] = 0
    for i in range(m + 1):
        g[i][0] = 0
    return g


# ---- Act 0: the recurrence ----
add(act=0, rows=blank(), rowLabels=rowLabels, colLabels=colLabels, code=None,
    intro="dp[i][j] = LCS length of the first i chars of t1 and first j of t2.",
    invariant="compare only the two LAST characters of each prefix.",
    note=f"t1 = \"{t1}\" down the rows, t2 = \"{t2}\" across the columns. Each cell is "
    "the LCS length of those two prefixes.",
    marks={f"{m},{n}": "active"}, state=[["t1", t1], ["t2", t2]])
add(act=0,
    note="If the last chars match, they can end the LCS: dp[i][j] = dp[i-1][j-1] + 1 "
    "(a diagonal step). If not, drop one char: dp[i][j] = max(up, left). Naive "
    "recursion re-solves the same (i, j) many times; the table solves each once.",
    marks={f"{m},{n}": "active", f"{m-1},{n-1}": "bad"},
    state=[["match", "diag + 1"], ["mismatch", "max(up, left)"]])

# ---- Act 1: fill the table ----
add(act=1, rows=zeros_seeded(), rowLabels=rowLabels, colLabels=colLabels,
    code="dp", line=0,
    intro="row 0 and column 0 are all zeros; fill the interior top-left to bottom-right.",
    invariant="dp[i][j] final before its right/down neighbors are computed.",
    note="An empty prefix shares nothing, so the whole first row and first column "
    "are 0.",
    marks={}, state=[["seed", "edges = 0"]])
for i in range(1, m + 1):
    for j in range(1, n + 1):
        match = t1[i - 1] == t2[j - 1]
        if match:
            src = {f"{i-1},{j-1}": "active"}
            note = (f"t1[{i-1}]='{t1[i-1]}' == t2[{j-1}]='{t2[j-1]}': "
                    f"dp[{i}][{j}] = diag {dp[i-1][j-1]} + 1 = {dp[i][j]}.")
        else:
            src = {f"{i-1},{j}": "active", f"{i},{j-1}": "active"}
            note = (f"'{t1[i-1]}' != '{t2[j-1]}': dp[{i}][{j}] = max(up "
                    f"{dp[i-1][j]}, left {dp[i][j-1]}) = {dp[i][j]}.")
        marks = dict(src)
        marks[f"{i},{j}"] = "good"
        add(act=1, code="dp", line=4 if match else 6, note=note,
            set={f"{i},{j}": dp[i][j]}, marks=marks,
            state=[["cell", f"({i},{j})"], ["match", match], [f"dp[{i}][{j}]", dp[i][j]]])

# ---- Act 2: answer + edge ----
add(act=2, code="dp", line=7,
    intro="the bottom-right cell is the LCS of the two full strings.",
    invariant="the corner combined every prefix decision into one number.",
    note=f"dp[{m}][{n}] = {dp[m][n]} — the LCS is \"ace\", length 3.",
    marks={f"{m},{n}": "good"}, state=[["answer", dp[m][n]]],
    banner=f'LCS("{t1}", "{t2}") = {dp[m][n]}  ("ace")')
# edge: no common characters -> 0
e1, e2 = "abc", "def"
ed = [[0] * (len(e2) + 1) for _ in range(len(e1) + 1)]
for i in range(1, len(e1) + 1):
    for j in range(1, len(e2) + 1):
        if e1[i - 1] == e2[j - 1]:
            ed[i][j] = ed[i - 1][j - 1] + 1
        else:
            ed[i][j] = max(ed[i - 1][j], ed[i][j - 1])
assert ed[len(e1)][len(e2)] == 0
add(act=2, rows=ed, rowLabels=["-"] + list(e1), colLabels=["-"] + list(e2),
    code="dp", line=7,
    note="Edge case: \"abc\" and \"def\" share no character, so every mismatch just "
    "carries a 0 across — the whole table stays 0 and the answer is 0.",
    marks={f"{len(e1)},{len(e2)}": "good"}, state=[["answer", 0]],
    banner="No common characters -> 0")

trace = {
    "player": "grid",
    "title": "Longest Common Subsequence - fill each (i, j) once",
    "acts": ["The match/drop rule", "Fill the table", "Answer + edge"],
    "code": {"dp": CODE},
    "legend": [["active", "the neighbors we read"], ["good", "just-filled / answer"], ["bad", "recomputed (waste)"]],
    "rows": blank(), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
