"""Rich full-arc trace for Merge k Sorted Lists (linked-list renderer).
Arc: naive fold (accumulator re-walked every round) -> the waste -> divide &
conquer pairwise -> edge (empties). Mirrors merge_k_lists_naive and
merge_k_lists in solution.py. Each list is laid out as a labelled segment in one
row; the picked node is marked 'good'. Writes trace.json.
"""
import json
import os

frames = []

CODE_NAIVE = [
    "result = None",
    "for lst in lists:",
    "    result = merge_two(result, lst)",
    "return result",
]

CODE_DC = [
    "while len(lists) > 1:",
    "    merged = []",
    "    for i in range(0, len(lists), 2):",
    "        a = lists[i]; b = lists[i+1] if i+1 < len else None",
    "        merged.append(merge_two(a, b))",
    "    lists = merged",
    "return lists[0]",
]


def add(**f):
    frames.append(f)


# k = 4 lists. Lay them in one row with labels; track segment index ranges.
LISTS = [[1, 4, 5], [1, 3, 4], [2, 6], [3, 8]]
vals = []
labels = []
seg = []  # seg[i] = list of global indices for list i
for li, L in enumerate(LISTS):
    idxs = []
    for v in L:
        idxs.append(len(vals))
        vals.append(v)
        labels.append(chr(ord("A") + li))
    seg.append(idxs)


def within_edges(active_lists):
    """Forward chains inside each still-separate list segment."""
    e = []
    for li in active_lists:
        s = seg[li]
        for k in range(len(s)):
            e.append([s[k], s[k + 1] if k + 1 < len(s) else None])
    return e


def merge_indices(idxsA, idxsB):
    """Return the merged order of two sorted index-runs (by value)."""
    i = j = 0
    out = []
    while i < len(idxsA) and j < len(idxsB):
        if vals[idxsA[i]] <= vals[idxsB[j]]:
            out.append(idxsA[i]); i += 1
        else:
            out.append(idxsB[j]); j += 1
    out += idxsA[i:]; out += idxsB[j:]
    return out


def chain_edges(order):
    e = [[order[k], order[k + 1]] for k in range(len(order) - 1)]
    if order:
        e.append([order[-1], None])
    return e


# ============ Act 0: naive fold ============
add(act=0, vals=vals, labels=labels, edges=within_edges([0, 1, 2, 3]),
    code="naive", line=0,
    intro="watch the accumulator get re-walked from the start on every round.",
    invariant="result always holds every node merged so far, in sorted order.",
    note="Four sorted lists A B C D in one row. The obvious plan: merge them into one "
    "accumulator, one list at a time.",
    pointers={}, state=[["lists left", 4], ["nodes re-walked", 0]])

result = []          # accumulated order
rewalks = 0
for li in range(len(LISTS)):
    before = len(result)
    result = merge_indices(result, seg[li])
    rewalks += before  # the whole existing accumulator is walked again
    marks = {str(p): "dim" for p in result}
    for p in seg[li]:
        marks[str(p)] = "active"
    add(act=0, code="naive", line=2, edges=chain_edges(result),
        note=f"Merge list {chr(ord('A') + li)} into result. But the {before} nodes already "
             f"in result get walked again — that re-walk is the cost.",
        marks=marks,
        state=[["lists left", len(LISTS) - li - 1],
               ["result size", len(result)],
               ["nodes re-walked", rewalks]])

add(act=0, code="naive", line=3, edges=chain_edges(result),
    note=f"Merged, but the accumulator was re-swept over and over — {rewalks} redundant "
         f"node touches for {len(vals)} nodes. That grows toward O(k*N).",
    marks={str(p): "good" for p in result},
    state=[["result", " ".join(str(vals[p]) for p in result)],
           ["nodes re-walked", rewalks]],
    banner="Naive fold: correct but re-walks the accumulator")

# ============ Act 1: name the waste ============
add(act=1, vals=vals, labels=labels, edges=within_edges([0, 1, 2, 3]),
    code="naive", line=1,
    intro="pairing lists up means each node is touched once per round, and rounds halve.",
    invariant="after each round the number of lists is halved.",
    note="The waste: one growing accumulator gets re-read every step. Instead, merge in "
    "PAIRS so each round halves how many lists remain: 4 -> 2 -> 1. log k rounds, each "
    "touching every node once -> O(N log k).",
    pointers={}, state=[["fold", "O(k*N)"], ["pairwise", "O(N log k)"]])

# ============ Act 2: divide and conquer ============
add(act=2, vals=vals, labels=labels, edges=within_edges([0, 1, 2, 3]),
    code="dc", line=0,
    intro="round 1 pairs (A,B) and (C,D); round 2 merges the two results.",
    invariant="every node is touched exactly once per round.",
    note="Divide and conquer. Round 1: merge A with B, and C with D — two independent "
    "merges.",
    pointers={}, state=[["round", 1], ["lists", 4]])

# Round 1: (A,B) and (C,D)
ab = merge_indices(seg[0], seg[1])
add(act=2, code="dc", line=4, edges=chain_edges(ab) + within_edges([2, 3]),
    note="A + B -> " + " ".join(str(vals[p]) for p in ab) + ".",
    marks={str(p): "good" for p in ab},
    state=[["round", 1], ["merged", "A+B"]])
cd = merge_indices(seg[2], seg[3])
add(act=2, code="dc", line=4, edges=chain_edges(ab) + chain_edges(cd),
    note="C + D -> " + " ".join(str(vals[p]) for p in cd) +
         ". Round 1 done: 4 lists became 2.",
    marks={**{str(p): "dim" for p in ab}, **{str(p): "good" for p in cd}},
    state=[["round", 1], ["lists", 2]])

# Round 2: (AB, CD)
add(act=2, code="dc", line=0, edges=chain_edges(ab) + chain_edges(cd),
    note="Round 2: merge the two survivors (A+B) and (C+D) into one.",
    marks={**{str(p): "active" for p in ab}, **{str(p): "active" for p in cd}},
    state=[["round", 2], ["lists", 2]])
final = merge_indices(ab, cd)
add(act=2, code="dc", line=4, edges=chain_edges(final),
    note="Final merge -> " + " ".join(str(vals[p]) for p in final) +
         ". Two rounds (log 4) and each node touched once per round.",
    marks={str(p): "good" for p in final},
    state=[["round", 2], ["lists", 1]])
add(act=2, code="dc", line=6, edges=chain_edges(final),
    note="One sorted list, in O(N log k). The accumulator re-walking is gone.",
    marks={str(p): "good" for p in final},
    state=[["result", " ".join(str(vals[p]) for p in final)]],
    banner="Divide & conquer: merged in log k rounds")

# ============ Act 3: edge — empties ============
vals2 = [1]
labels2 = ["B"]
add(act=3, vals=vals2, labels=labels2, edges=[[0, None]], code="dc", line=0,
    intro="empty lists just drop out; a lone list is already the answer.",
    invariant="merging with None returns the other list unchanged.",
    note="Edge case: [[], [1], []]. The empty lists contribute nothing, so pairing them "
    "with [1] leaves [1] as the whole result.",
    pointers={}, marks={"0": "good"},
    state=[["result", "1"]],
    banner="Empties drop out: result is 1")

trace = {
    "player": "linkedlist",
    "title": "Merge k Sorted Lists - pair up instead of folding one at a time",
    "acts": ["Naive: fold into one accumulator", "The waste", "Divide & conquer",
             "Edge: empty lists"],
    "code": {"naive": CODE_NAIVE, "dc": CODE_DC},
    "legend": [["good", "in this round's merged result"], ["active", "being merged now"],
               ["dim", "already merged earlier"]],
    "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
