"""Rich full-arc trace for Buy/Sell Stock with Cooldown (grid renderer).
Arc: brute (branch buy/sell/rest each day, states overlap) -> fill a 3-state x
day table -> answer + edge. Rows are the three running states (hold / sold / rest);
each column is a day, computed from the column before it. This is the same
recurrence as the O(1) roll in solution.py, laid out as a table so the
dependencies are visible. Writes trace.json.
"""
import json
import os

PRICES = [1, 2, 3, 0, 2]
NEG = float("-inf")
NEG_STR = "−∞"
frames = []

CODE = [
    "hold, sold, rest = -inf, 0, 0",
    "for p in prices:",
    "    hold = max(hold, rest - p)   # keep, or buy from a free day",
    "    sold = hold_prev + p         # sell today",
    "    rest = max(rest, sold_prev)  # stay free, or cooldown ends",
    "return max(sold, rest)",
]

# rows: 0=hold, 1=sold, 2=rest ; cols: day 0..n (col 0 = before any day)
ROWLABELS = ["hold", "sold", "rest"]
COLLABELS = ["·"] + [str(p) for p in PRICES]
NCOL = len(PRICES) + 1


def add(**f):
    frames.append(f)


def cell(v):
    return NEG_STR if v == NEG else v


def blank():
    return [[None] * NCOL for _ in range(3)]


# ---- Act 0: brute ----
add(act=0, rows=blank(), rowLabels=ROWLABELS, colLabels=COLLABELS, code=None,
    intro="how the same (day, holding?) situation gets re-explored down the choice tree.",
    invariant="best(day, holding) = most profit from `day` onward in that state.",
    note="Brute force: each day choose buy, sell, or rest, and recurse. Selling forces "
    "the next day to be a cooldown, so buys can only follow a rest day.",
    marks={"0,0": "active"}, state=[["prices", str(PRICES)], ["daily choice", "buy / sell / rest"]])
add(act=0, note="Different early choices reach the same (day, holding) situation and "
    "re-solve the entire rest of the trip. That repeated tail is the waste.",
    marks={"0,3": "bad", "0,0": "active"},
    state=[["recomputed", "best(day 3, hold) …"], ["cost", "exponential"]])

# ---- Act 1: fill the table ----
dp = blank()
add(act=1, rows=blank(), code="tab", line=0,
    intro="each column (a day) is computed from the column to its left.",
    invariant="hold/sold/rest each carry the best profit ending in that state.",
    note="Seed the day-0 column (before trading): you can't hold yet (−∞ profit), and "
    "with nothing done, sold and rest are both 0.",
    marks={}, state=[["seed", "hold=−∞, sold=0, rest=0"]])
hold, sold, rest = NEG, 0, 0
dp[0][0], dp[1][0], dp[2][0] = cell(hold), cell(sold), cell(rest)
add(act=1, code="tab", line=0, note="Day · : hold = −∞, sold = 0, rest = 0.",
    set={"0,0": cell(hold), "1,0": cell(sold), "2,0": cell(rest)},
    marks={"0,0": "good", "1,0": "good", "2,0": "good"},
    state=[["hold", cell(hold)], ["sold", cell(sold)], ["rest", cell(rest)]])

for d, p in enumerate(PRICES):
    col = d + 1
    prev = col - 1
    # snapshot previous column
    ph, ps, pr = hold, sold, rest
    hold = max(ph, pr - p)      # keep holding, or buy today from rest
    sold = ph + p              # sell today (had to be holding)
    rest = max(pr, ps)         # stay free, or cooldown after a prior sale ends
    # hold cell
    add(act=1, code="tab", line=2,
        note=f"Day price {p}: hold = max(prev hold {cell(ph)}, rest {cell(pr)} - {p}) = {cell(hold)}.",
        set={f"0,{col}": cell(hold)},
        marks={f"0,{prev}": "active", f"2,{prev}": "active", f"0,{col}": "good"},
        state=[["price", p], ["prev hold", cell(ph)], ["rest - p", cell(pr - p)], ["hold", cell(hold)]])
    # sold cell
    add(act=1, code="tab", line=3,
        note=f"sold = prev hold {cell(ph)} + price {p} = {cell(sold)} (sell only if you held).",
        set={f"1,{col}": cell(sold)},
        marks={f"0,{prev}": "active", f"1,{col}": "good"},
        state=[["price", p], ["prev hold", cell(ph)], ["sold", cell(sold)]])
    # rest cell
    add(act=1, code="tab", line=4,
        note=f"rest = max(prev rest {cell(pr)}, prev sold {cell(ps)}) = {cell(rest)} — the "
        "cooldown after a sale lands here.",
        set={f"2,{col}": cell(rest)},
        marks={f"2,{prev}": "active", f"1,{prev}": "active", f"2,{col}": "good"},
        state=[["prev rest", cell(pr)], ["prev sold", cell(ps)], ["rest", cell(rest)]])

# ---- Act 2: answer + edge ----
ans = int(max(sold, rest))
last = len(PRICES)
add(act=2, code="tab", line=5,
    intro="the answer is the best non-holding state on the last day.",
    invariant="you never end holding a share; profit is max(sold, rest) at the end.",
    note=f"Last column: max(sold {cell(sold)}, rest {cell(rest)}) = {ans}. Buy at 1, sell at 3, "
    "cooldown, buy at 0, sell at 2.",
    marks={f"1,{last}": "good", f"2,{last}": "good"}, state=[["answer", ans]],
    banner=f"Max profit with cooldown = {ans}")

# edge: descending prices -> no profitable trade -> 0. prices=[2,1]
E = [2, 1]
add(act=2, rows=[["·"] + [None] * len(E) for _ in range(3)],
    rowLabels=ROWLABELS, colLabels=["·"] + [str(p) for p in E], code="tab", line=5,
    note="Edge case: prices only fall ([2, 1]). Every buy would end in a loss, so the "
    "best plan is to trade nothing and the answer is 0.",
    marks={f"2,{len(E)}": "good"}, state=[["answer", 0]],
    banner="Falling prices → 0 profit")

trace = {
    "player": "grid",
    "title": "Stock with Cooldown - three states across the days",
    "acts": ["Brute: buy / sell / rest tree", "Fill the state table", "Answer + edge"],
    "code": {"tab": CODE},
    "legend": [["active", "previous-day cells read"], ["good", "computed / answer"],
               ["bad", "recomputed (waste)"]],
    "rows": blank(), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
