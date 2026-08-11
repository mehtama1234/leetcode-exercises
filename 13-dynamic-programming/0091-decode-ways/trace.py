"""Full-arc trace for Decode Ways (grid renderer, dp[i]=ways to decode s[i:]).
Arc: the single/pair recurrence -> fill dp from the end once -> answer -> a
zero-trap edge. Mirrors solution.py. Writes trace.json.
"""
import json
import os

s = "226"  # answer 3: BZ, VF, BBF
n = len(s)
frames = []

CODE = [
    "dp[n] = 1",
    "for i in range(n-1, -1, -1):",
    "    if s[i] == '0': dp[i] = 0",
    "    else:",
    "        dp[i] = dp[i+1]                 # single digit",
    "        if s[i:i+2] <= 26: dp[i]+=dp[i+2]  # pair",
    "return dp[0]",
]


def add(**f):
    frames.append(f)


# dp[i] = ways to decode s[i:], dp[n] = 1. Verified for "226": [3,2,1,1]
dp = [0] * (n + 1)
dp[n] = 1
for i in range(n - 1, -1, -1):
    if s[i] == "0":
        dp[i] = 0
    else:
        dp[i] = dp[i + 1]
        if i + 1 < n and int(s[i:i + 2]) <= 26:
            dp[i] += dp[i + 2]
assert dp == [3, 2, 1, 1]

# columns are positions 0..n; label each with the char it starts (last = end)
colLabels = [s[i] for i in range(n)] + ["end"]


def blank():
    return [[None] * (n + 1)]


# ---- Act 0: the recurrence ----
add(act=0, rows=blank(), rowLabels=["dp"], colLabels=colLabels, code=None,
    intro="dp[i] = number of ways to decode the suffix starting at i.",
    invariant="from i you either take one digit (1..9) or a pair (10..26).",
    note=f"String \"{s}\". Digits 1..26 are letters A..Z. Standing at i, decode the "
    "single digit s[i] and go to i+1, or the pair s[i:i+2] and go to i+2.",
    marks={"0,0": "active"}, state=[["s", s], ["want", "total decodings"]])
add(act=0,
    note="dp[i] = ways from i. Plain recursion reaches the same position i along many "
    "decode paths and re-solves it. Fill dp once, from the end, so both lookaheads "
    "are ready.",
    marks={"0,1": "bad", "0,2": "bad"},
    state=[["dp[i]", "recomputed"], ["fix", "fill from end"]])

# ---- Act 1: fill dp from the end ----
add(act=1, rows=blank(), rowLabels=["dp"], colLabels=colLabels, code="dp", line=0,
    intro="fill right to left; dp[i] reads only dp[i+1] and dp[i+2].",
    invariant="dp[i] final once written.",
    note="dp[n] = 1: reaching the end cleanly is one complete decoding.",
    set={f"0,{n}": 1}, marks={f"0,{n}": "good"}, state=[["dp[end]", 1]])
for i in range(n - 1, -1, -1):
    single = dp[i + 1]
    pair_ok = (i + 1 < n and int(s[i:i + 2]) <= 26)
    pair = dp[i + 2] if pair_ok else 0
    mk = {f"0,{i}": "good", f"0,{i+1}": "active"}
    if pair_ok:
        mk[f"0,{i+2}"] = "active"
    pair_txt = (f"+ pair \"{s[i:i+2]}\" -> dp[{i+2}] {pair}" if pair_ok
                else "(no valid pair)")
    add(act=1, code="dp", line=5,
        note=f"i={i} ('{s[i]}'): single -> dp[{i+1}] {single} {pair_txt} = {dp[i]}.",
        set={f"0,{i}": dp[i]}, marks=mk,
        state=[["single", single], ["pair", pair], [f"dp[{i}]", dp[i]]])

# ---- Act 2: answer + zero-trap edge ----
add(act=2, code="dp", line=6,
    intro="dp[0] is the total number of decodings.",
    invariant="every suffix was solved before the one to its left.",
    note=f"dp[0] = {dp[0]} — \"{s}\" decodes as BZ, VF, or BBF.",
    marks={"0,0": "good"}, state=[["answer", dp[0]]],
    banner=f"\"{s}\" -> {dp[0]} decodings")
# edge: "06" -> 0 (leading zero can't decode)
es = "06"
en = len(es)
edp = [0] * (en + 1)
edp[en] = 1
for i in range(en - 1, -1, -1):
    if es[i] == "0":
        edp[i] = 0
    else:
        edp[i] = edp[i + 1]
        if i + 1 < en and int(es[i:i + 2]) <= 26:
            edp[i] += edp[i + 2]
assert edp[0] == 0
add(act=2, rows=[[edp[0], edp[1], edp[2]]], rowLabels=["dp"],
    colLabels=["0", "6", "end"], code="dp", line=2,
    note="Edge case: \"06\". No letter starts with 0, so dp[0] = 0 immediately — the "
    "answer is 0. A leading zero kills the whole path.",
    marks={"0,0": "bad"}, state=[["dp[0]", 0], ["answer", 0]],
    banner="Leading zero -> 0")

trace = {
    "player": "grid",
    "title": "Decode Ways - fill each suffix's count once, from the end",
    "acts": ["The single/pair rule", "Fill dp from the end", "Answer + zero edge"],
    "code": {"dp": CODE},
    "legend": [["active", "dp[i+1] / dp[i+2] we read"], ["good", "solved / answer"], ["bad", "zero-trap / waste"]],
    "rows": blank(), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
