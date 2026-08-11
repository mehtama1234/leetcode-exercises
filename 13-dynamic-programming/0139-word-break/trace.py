"""Full-arc trace for Word Break (grid renderer, dp[i]=can s[i:] be broken).
Arc: the suffix recurrence -> fill dp from the end once -> answer -> a
can't-break edge. Mirrors solution.py. Writes trace.json.
"""
import json
import os

s = "leetcode"
words = {"leet", "code"}
n = len(s)
frames = []

CODE = [
    "dp[n] = True",
    "for i in range(n-1, -1, -1):",
    "    for j in range(i+1, n+1):",
    "        if s[i:j] in words and dp[j]:",
    "            dp[i] = True; break",
    "return dp[0]",
]


def add(**f):
    frames.append(f)


# dp[i] = can s[i:] be split into dictionary words. dp[n] = True.
dp = [False] * (n + 1)
dp[n] = True
hit = {}  # i -> (j, word) that made dp[i] true
for i in range(n - 1, -1, -1):
    for j in range(i + 1, n + 1):
        if s[i:j] in words and dp[j]:
            dp[i] = True
            hit[i] = (j, s[i:j])
            break
assert dp[0] is True
assert hit == {4: (8, "code"), 0: (4, "leet")}

colLabels = [s[i] for i in range(n)] + ["end"]


def cellval(v):
    return "T" if v else "F"


def blank():
    return [[None] * (n + 1)]


# ---- Act 0: the recurrence ----
add(act=0, rows=blank(), rowLabels=["dp"], colLabels=colLabels, code=None,
    intro="dp[i] answers: can the suffix starting at i be cut into dictionary words?",
    invariant="s[i:] is breakable iff some word matches at i and the rest is breakable.",
    note=f"String \"{s}\", words {sorted(words)}. From position i, try each dictionary "
    "word that matches at i; if the remainder after it is also breakable, so is s[i:].",
    marks={"0,0": "active"}, state=[["s", s], ["words", str(sorted(words))]])
add(act=0,
    note="The remainder is an identical subproblem keyed only by its start index. "
    "Plain recursion re-solves the same suffix along many prefix choices. Fill dp "
    "once, from the end.",
    marks={"0,4": "bad"}, state=[["dp[i]", "recomputed"], ["fix", "fill from end"]])

# ---- Act 1: fill dp from the end ----
add(act=1, rows=blank(), rowLabels=["dp"], colLabels=colLabels, code="dp", line=0,
    intro="fill right to left; each dp[i] scans words that start at i.",
    invariant="dp[i] final once written.",
    note="dp[end] = True: the empty suffix is trivially broken.",
    set={f"0,{n}": "T"}, marks={f"0,{n}": "good"}, state=[["dp[end]", "True"]])
for i in range(n - 1, -1, -1):
    if i in hit:
        j, w = hit[i]
        add(act=1, code="dp", line=4,
            note=f"i={i}: word \"{w}\" matches s[{i}:{j}] and dp[{j}] is True -> "
            f"dp[{i}] = True.",
            set={f"0,{i}": "T"},
            marks={f"0,{i}": "good", f"0,{j}": "active"},
            state=[["match", f'"{w}"'], [f"dp[{i}]", "True"]])
    else:
        add(act=1, code="dp", line=2,
            note=f"i={i} ('{s[i]}'): no dictionary word both matches at {i} and leaves a "
            "breakable rest -> dp[i] stays False.",
            set={f"0,{i}": "F"}, marks={f"0,{i}": "dim"},
            state=[[f"dp[{i}]", "False"]])

# ---- Act 2: answer + edge ----
add(act=2, code="dp", line=5,
    intro="dp[0] is the whole answer: can all of s be broken?",
    invariant="every suffix was solved before the one to its left.",
    note=f"dp[0] = True: \"{s}\" splits as \"leet\" + \"code\".",
    marks={"0,0": "good", "0,4": "good"}, state=[["answer", "True"]],
    banner='"leetcode" -> True  ("leet" + "code")')
# edge: "catsandog" with words that can't cover it -> False
es = "catsandog"
ewords = {"cats", "dog", "sand", "and", "cat"}
en = len(es)
edp = [False] * (en + 1)
edp[en] = True
ehit = {}
for i in range(en - 1, -1, -1):
    for j in range(i + 1, en + 1):
        if es[i:j] in ewords and edp[j]:
            edp[i] = True
            ehit[i] = j
            break
assert edp[0] is False
add(act=2, rows=[[cellval(edp[i]) for i in range(en + 1)]], rowLabels=["dp"],
    colLabels=[es[i] for i in range(en)] + ["end"], code="dp", line=5,
    note="Edge case: \"catsandog\". Words cover the front (\"cats\"/\"cat\"...) but the "
    "tail \"og\" is in no word, so dp[0] is False — the split can't complete.",
    marks={"0,0": "dim", f"0,{en-2}": "bad", f"0,{en-1}": "bad"},
    state=[["dp[0]", "False"], ["answer", "False"]], banner="Tail unbreakable -> False")

trace = {
    "player": "grid",
    "title": "Word Break - solve each suffix once, from the end",
    "acts": ["The suffix rule", "Fill dp from the end", "Answer + edge"],
    "code": {"dp": CODE},
    "legend": [["active", "the rest (dp[j]) we lean on"], ["good", "breakable / answer"], ["dim", "not breakable"], ["bad", "unbreakable tail"]],
    "rows": blank(), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
