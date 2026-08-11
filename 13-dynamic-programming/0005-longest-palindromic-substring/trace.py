"""Full-arc trace for Longest Palindromic Substring (grid renderer, 2-D dp[i][j]).
Arc: the ends-match-and-inside recurrence -> fill the upper triangle by length ->
answer -> edge. Mirrors the table DP in solution.py. Writes trace.json.
"""
import json
import os

s = "babad"  # answer "aba" (or "bab"); this fill order lands on "aba"
n = len(s)
frames = []

CODE = [
    "dp = [[False]*n for _ in range(n)]",
    "for i in range(n-1, -1, -1):",
    "    for j in range(i, n):",
    "        if s[i]==s[j] and (j-i < 2 or dp[i+1][j-1]):",
    "            dp[i][j] = True",
    "            if j-i+1 > best: start, best = i, j-i+1",
    "return s[start:start+best]",
]


def add(**f):
    frames.append(f)


# dp[i][j] = is s[i..j] a palindrome. Fill i descending, j ascending.
dp = [[False] * n for _ in range(n)]
order = []          # (i, j, value, reason) in fill order
start, best = 0, 1
for i in range(n - 1, -1, -1):
    for j in range(i, n):
        ends = s[i] == s[j]
        inside = (j - i < 2) or dp[i + 1][j - 1]
        val = ends and inside
        dp[i][j] = val
        reason = ""
        if not ends:
            reason = f"ends '{s[i]}' != '{s[j]}'"
        elif j - i < 2:
            reason = "ends match, length <= 2 (no interior)"
        else:
            reason = f"ends match and inside dp[{i+1}][{j-1}] is {dp[i+1][j-1]}"
        if val and j - i + 1 > best:
            start, best = i, j - i + 1
        order.append((i, j, val, reason))
assert s[start:start + best] == "aba"

colLabels = [f"{c}:{s[c]}" for c in range(n)]
rowLabels = [f"{r}:{s[r]}" for r in range(n)]


def blank():
    return [[None] * n for _ in range(n)]


def cellval(v):
    return "T" if v else "F"


# ---- Act 0: the recurrence ----
add(act=0, rows=blank(), rowLabels=rowLabels, colLabels=colLabels, code=None,
    intro="dp[i][j] asks: is the stretch s[i..j] a palindrome?",
    invariant="s[i..j] is a palindrome iff its ends match AND its inside is one.",
    note=f"String \"{s}\". Cell (i, j) marks whether s[i..j] reads the same both ways. "
    "Only the upper triangle (j >= i) is meaningful.",
    marks={"0,0": "active"}, state=[["s", s], ["want", "longest palindrome"]])
add(act=0,
    note="dp[i][j] = (s[i]==s[j]) and (j-i < 2 or dp[i+1][j-1]). The inner term is a "
    "SHORTER stretch, so if we fill by increasing length every lookup is ready — no "
    "recomputation.",
    marks={"1,3": "active", "2,2": "bad"},
    state=[["needs", "dp[i+1][j-1]"], ["order", "shortest first"]])

# ---- Act 1: fill the triangle ----
add(act=1, rows=blank(), rowLabels=rowLabels, colLabels=colLabels, code="dp", line=0,
    intro="fill i descending / j ascending so the inside is always solved first.",
    invariant="dp[i][j] final once written; we keep the widest True span.",
    note="Diagonal cells (i == j) are single characters — always palindromes.",
    marks={}, state=[["best", "s[0:1]"]])
cur_start, cur_best = 0, 1
for (i, j, val, reason) in order:
    src = {}
    if val and j - i >= 2:
        src[f"{i+1},{j-1}"] = "active"
    marks = dict(src)
    marks[f"{i},{j}"] = "good" if val else "dim"
    updated = ""
    if val and j - i + 1 > cur_best:
        cur_start, cur_best = i, j - i + 1
        updated = f"  new best: \"{s[cur_start:cur_start+cur_best]}\""
    add(act=1, code="dp", line=4 if val else 3,
        note=f"s[{i}..{j}]=\"{s[i:j+1]}\": {reason} -> {val}.{updated}",
        set={f"{i},{j}": cellval(val)}, marks=marks,
        state=[["span", f"[{i}..{j}]"], ["palindrome?", val], ["best", f'"{s[cur_start:cur_start+cur_best]}"']])

# ---- Act 2: answer + edge ----
add(act=2, code="dp", line=6,
    intro="the widest True span is the answer.",
    invariant="every shorter stretch was decided before the ones that lean on it.",
    note=f"The widest True cell is s[{start}..{start+best-1}] = \"{s[start:start+best]}\".",
    marks={f"{start},{start+best-1}": "good"},
    state=[["answer", f'"{s[start:start+best]}"']],
    banner=f'Longest palindrome in "{s}" = "{s[start:start+best]}"')
# edge: "cbbd" -> "bb"
es = "cbbd"
en = len(es)
edp = [[False] * en for _ in range(en)]
estart, ebest = 0, 1
for i in range(en - 1, -1, -1):
    for j in range(i, en):
        if es[i] == es[j] and (j - i < 2 or edp[i + 1][j - 1]):
            edp[i][j] = True
            if j - i + 1 > ebest:
                estart, ebest = i, j - i + 1
assert es[estart:estart + ebest] == "bb"
add(act=2, rows=[[(cellval(edp[i][j]) if j >= i else None) for j in range(en)]
                 for i in range(en)],
    rowLabels=[f"{r}:{es[r]}" for r in range(en)],
    colLabels=[f"{c}:{es[c]}" for c in range(en)], code="dp", line=6,
    note="Edge case: \"cbbd\". No single character extends, but the adjacent pair "
    "s[1..2]=\"bb\" has matching ends and length 2 (base case) -> the answer is \"bb\".",
    marks={"1,2": "good"}, state=[["answer", '"bb"']],
    banner='"cbbd" -> "bb"')

trace = {
    "player": "grid",
    "title": "Longest Palindromic Substring - decide each span once, shortest first",
    "acts": ["The ends+inside rule", "Fill the triangle", "Answer + edge"],
    "code": {"dp": CODE},
    "legend": [["active", "the inside dp[i+1][j-1]"], ["good", "palindrome / answer"], ["dim", "not a palindrome"], ["bad", "would be recomputed"]],
    "rows": blank(), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
