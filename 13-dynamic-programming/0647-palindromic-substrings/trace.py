"""Full-arc trace for Palindromic Substrings (grid renderer, 2-D dp[i][j]).
Arc: the ends-match-and-inside recurrence -> fill the triangle, counting Trues ->
answer -> edge. Mirrors the table DP in solution.py. Writes trace.json.
"""
import json
import os

s = "aaa"  # answer 6: a,a,a, aa,aa, aaa
n = len(s)
frames = []

CODE = [
    "dp = [[False]*n for _ in range(n)]",
    "count = 0",
    "for i in range(n-1, -1, -1):",
    "    for j in range(i, n):",
    "        if s[i]==s[j] and (j-i < 2 or dp[i+1][j-1]):",
    "            dp[i][j] = True",
    "            count += 1",
    "return count",
]


def add(**f):
    frames.append(f)


# dp[i][j] = is s[i..j] a palindrome. Count every True. For "aaa" all 6 are True.
dp = [[False] * n for _ in range(n)]
order = []
count = 0
for i in range(n - 1, -1, -1):
    for j in range(i, n):
        ends = s[i] == s[j]
        inside = (j - i < 2) or dp[i + 1][j - 1]
        val = ends and inside
        dp[i][j] = val
        if val:
            count += 1
        reason = ("length <= 2, ends match" if (ends and j - i < 2)
                  else (f"ends match and inside dp[{i+1}][{j-1}] True" if val
                        else f"ends '{s[i]}' != '{s[j]}'"))
        order.append((i, j, val, reason, count))
assert count == 6

colLabels = [f"{c}:{s[c]}" for c in range(n)]
rowLabels = [f"{r}:{s[r]}" for r in range(n)]


def blank():
    return [[None] * n for _ in range(n)]


def cellval(v):
    return "T" if v else "F"


# ---- Act 0: the recurrence ----
add(act=0, rows=blank(), rowLabels=rowLabels, colLabels=colLabels, code=None,
    intro="dp[i][j] marks whether s[i..j] is a palindrome; we count the Trues.",
    invariant="each (start, end) pair counts separately.",
    note=f"String \"{s}\". Every distinct (i, j) that reads the same both ways is one "
    "palindromic substring. \"aaa\" should give 6: a, a, a, aa, aa, aaa.",
    marks={"0,0": "active"}, state=[["s", s], ["count", 0]])
add(act=0,
    note="dp[i][j] = (s[i]==s[j]) and (j-i < 2 or dp[i+1][j-1]). The inside term is a "
    "shorter stretch, so filling shortest-first makes every lookup ready — no "
    "recomputation. Add 1 to count for each True.",
    marks={"0,2": "active", "1,1": "bad"},
    state=[["rule", "ends + inside"], ["order", "shortest first"]])

# ---- Act 1: fill + count ----
add(act=1, rows=blank(), rowLabels=rowLabels, colLabels=colLabels, code="dp", line=0,
    intro="fill i descending / j ascending; every True is one more palindrome.",
    invariant="count = number of True cells decided so far.",
    note="Diagonal cells (single characters) are palindromes, so each adds 1.",
    marks={}, state=[["count", 0]])
for (i, j, val, reason, running) in order:
    src = {}
    if val and j - i >= 2:
        src[f"{i+1},{j-1}"] = "active"
    marks = dict(src)
    marks[f"{i},{j}"] = "good" if val else "dim"
    tail = f"  count -> {running}" if val else ""
    add(act=1, code="dp", line=6 if val else 4,
        note=f"s[{i}..{j}]=\"{s[i:j+1]}\": {reason} -> {val}.{tail}",
        set={f"{i},{j}": cellval(val)}, marks=marks,
        state=[["span", f"[{i}..{j}]"], ["palindrome?", val], ["count", running]])

# ---- Act 2: answer + edge ----
add(act=2, code="dp", line=7,
    intro="the answer is the total number of True cells.",
    invariant="every span was decided exactly once.",
    note=f"All 6 upper-triangle cells are True, so \"{s}\" has {count} palindromic "
    "substrings.",
    marks={f"{i},{j}": "good" for i in range(n) for j in range(i, n)},
    state=[["answer", count]],
    banner=f'"{s}" -> {count} palindromic substrings')
# edge: "abc" -> 3 (only the single chars)
es = "abc"
en = len(es)
edp = [[False] * en for _ in range(en)]
ecount = 0
for i in range(en - 1, -1, -1):
    for j in range(i, en):
        if es[i] == es[j] and (j - i < 2 or edp[i + 1][j - 1]):
            edp[i][j] = True
            ecount += 1
assert ecount == 3
add(act=2, rows=[[(cellval(edp[i][j]) if j >= i else None) for j in range(en)]
                 for i in range(en)],
    rowLabels=[f"{r}:{es[r]}" for r in range(en)],
    colLabels=[f"{c}:{es[c]}" for c in range(en)], code="dp", line=7,
    note="Edge case: \"abc\", all distinct. Only the three single characters are "
    "palindromes; every longer span has mismatched ends -> the answer is 3.",
    marks={"0,0": "good", "1,1": "good", "2,2": "good"},
    state=[["answer", ecount]], banner='"abc" -> 3')

trace = {
    "player": "grid",
    "title": "Palindromic Substrings - decide each span once and count the Trues",
    "acts": ["The ends+inside rule", "Fill + count", "Answer + edge"],
    "code": {"dp": CODE},
    "legend": [["active", "the inside dp[i+1][j-1]"], ["good", "palindrome (counted)"], ["dim", "not a palindrome"], ["bad", "would be recomputed"]],
    "rows": blank(), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
