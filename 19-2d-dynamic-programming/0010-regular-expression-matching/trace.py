"""Rich full-arc trace for Regular Expression Matching (grid renderer).
Arc: brute (branch on every '*', suffixes re-matched) -> fill the (m+1)x(n+1)
boolean table from the empty suffixes back to (0,0) -> answer + edge. Mirrors the
tabulation in solution.py. Writes trace.json.
"""
import json
import os

S, P = "aab", "c*a*b"
M, N = len(S), len(P)
frames = []

CODE = [
    "dp = [[False]*(n+1) for _ in range(m+1)]",
    "dp[m][n] = True                 # empty matches empty",
    "for i in range(m, -1, -1):",
    "    for j in range(n-1, -1, -1):",
    "        first = i<m and p[j] in (s[i], '.')",
    "        if p[j+1] == '*':",
    "            dp[i][j] = dp[i][j+2] or (first and dp[i+1][j])",
    "        else:",
    "            dp[i][j] = first and dp[i+1][j+1]",
    "return dp[0][0]",
]

# dp[i][j] = does s[i:] match p[j:]?  rows i=0..m (last = empty s),
# cols j=0..n (last = empty p).
ROWLABELS = list(S) + ["·"]
COLLABELS = list(P) + ["·"]


def add(**f):
    frames.append(f)


def blank():
    return [[None] * (N + 1) for _ in range(M + 1)]


def fmt(b):
    return "T" if b else "F"


# ---- Act 0: brute ----
add(act=0, rows=blank(), rowLabels=ROWLABELS, colLabels=COLLABELS, code=None,
    intro="how the same (s-suffix, p-suffix) pair gets re-matched down '*' branches.",
    invariant="dp[i][j] = does s[i:] match p[j:]?",
    note="Brute force: compare the fronts. A plain char must match and both advance; "
    "'x*' branches — use it zero times (skip the pair) or one more (consume s[i]).",
    marks={"0,0": "active"}, state=[["match", "\"aab\" vs \"c*a*b\""], ["'*' branch", "zero / one-more"]])
add(act=0, note="Each '*' can loop, so many branches re-ask the same suffix pair — "
    "e.g. dp[1][2] \"ab vs a*b\" is reached several ways. That repetition is the waste.",
    marks={"1,2": "bad", "0,0": "active"},
    state=[["recomputed", "dp(1,2) …"], ["cost", "exponential"]])

# ---- Act 1: fill the table (bottom-right back) ----
dp = [[False] * (N + 1) for _ in range(M + 1)]
dp[M][N] = True
add(act=1, rows=blank(), code="tab", line=1,
    intro="filled from empty suffixes back; each cell reads down, down-right, or two-right.",
    invariant="dp[i][j] follows the recurrence exactly, computed once.",
    note="Seed dp[m][n] = T: the empty string matches the empty pattern.",
    marks={f"{M},{N}": "good"}, set={f"{M},{N}": "T"}, state=[[f"dp[{M}][{N}]", "T"]])
for i in range(M, -1, -1):
    for j in range(N - 1, -1, -1):
        first = i < M and (P[j] == S[i] or P[j] == ".")
        star = j + 1 < N and P[j + 1] == "*"
        if star:
            skip = dp[i][j + 2]                       # x* used zero times
            consume = first and dp[i + 1][j]          # x* used once more
            dp[i][j] = skip or consume
            marks = {f"{i},{j+2}": "active", f"{i},{j}": "good" if dp[i][j] else "bad"}
            if first:
                marks[f"{i+1},{j}"] = "active"
            note = (f"'{P[j]}*': zero-use dp[{i}][{j+2}]={fmt(skip)}"
                    + (f" or consume s[{i}] dp[{i+1}][{j}]={fmt(bool(consume))}" if first else " (front doesn't match, can't consume)")
                    + f" -> {fmt(dp[i][j])}.")
            state = [["p[%d]" % j, P[j] + "*"], ["zero-use(2 right)", fmt(skip)],
                     ["consume(down)", fmt(bool(consume))], [f"dp[{i}][{j}]", fmt(dp[i][j])]]
        else:
            dr = dp[i + 1][j + 1] if i < M else False
            dp[i][j] = bool(first and dr)
            marks = {f"{i},{j}": "good" if dp[i][j] else "bad"}
            if i < M:
                marks[f"{i+1},{j+1}"] = "active"
            note = (f"plain '{P[j]}': front match={fmt(bool(first))}"
                    + (f" and dp[{i+1}][{j+1}]={fmt(dr)}" if i < M else " (no s left)")
                    + f" -> {fmt(dp[i][j])}.")
            state = [["p[%d]" % j, P[j]], ["front match", fmt(bool(first))],
                     ["rest(down-right)", fmt(dr)], [f"dp[{i}][{j}]", fmt(dp[i][j])]]
        add(act=1, code="tab", line=6 if star else 8, note=note,
            set={f"{i},{j}": fmt(dp[i][j])}, marks=marks, state=state)

# ---- Act 2: answer + edge ----
add(act=2, code="tab", line=9,
    intro="the top-left cell answers the whole match.",
    invariant="dp[0][0] combined every '*' choice, each suffix solved once.",
    note=f"dp[0][0] = {fmt(dp[0][0])} — \"{S}\" {'matches' if dp[0][0] else 'does not match'} "
    f"\"{P}\".",
    marks={"0,0": "good" if dp[0][0] else "bad"}, state=[["answer", fmt(dp[0][0])]],
    banner=f"\"{S}\" vs \"{P}\" -> {fmt(dp[0][0])}")

# edge: ".*" matches anything. s="ab", p=".*"
E_S, E_P = "ab", ".*"
em, en = len(E_S), len(E_P)
edp = [[False] * (en + 1) for _ in range(em + 1)]
edp[em][en] = True
for i in range(em, -1, -1):
    for j in range(en - 1, -1, -1):
        first = i < em and (E_P[j] == E_S[i] or E_P[j] == ".")
        if j + 1 < en and E_P[j + 1] == "*":
            edp[i][j] = edp[i][j + 2] or (first and edp[i + 1][j])
        else:
            edp[i][j] = bool(first and (edp[i + 1][j + 1] if i < em else False))
add(act=2, rows=[[fmt(v) for v in row] for row in edp],
    rowLabels=list(E_S) + ["·"], colLabels=list(E_P) + ["·"],
    code="tab", line=9,
    note="Edge case: pattern \".*\" — the dot matches any character, the star repeats it "
    "any number of times, so it matches every string. The corner is T.",
    marks={"0,0": "good"}, state=[["answer", fmt(edp[0][0])]],
    banner="\".*\" matches anything → T")

trace = {
    "player": "grid",
    "title": "Regular Expression Matching - decide each (suffix, suffix) once",
    "acts": ["Brute: branch every '*'", "Fill the table", "Answer + edge"],
    "code": {"tab": CODE},
    "legend": [["active", "cells this one reads"], ["good", "matches (T)"],
               ["bad", "no match (F) / waste"]],
    "rows": blank(), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
