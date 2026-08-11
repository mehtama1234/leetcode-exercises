"""Rich full-arc trace for Count of Smaller Numbers After Self (grid renderer, BIT).
Arc: brute (rescan the whole suffix per element) -> the waste -> a Fenwick tree
over value-RANKS: sweep right-to-left, query "how many smaller ranks already
inserted?", then insert this rank. The grid rows are BIT nodes over ranks 1..m;
columns are ranks; a node's row fills across the rank-block it counts.
Mirrors countSmaller_brute / countSmaller in solution.py. Writes trace.json.
"""
import json
import os

nums = [5, 2, 6, 1]  # answer [2, 1, 1, 0]
frames = []

BRUTE = [
    "for i in range(n):",
    "    for j in range(i+1, n):",
    "        if nums[j] < nums[i]:",
    "            result[i] += 1",
]
BIT = [
    "ranks: sorted distinct values -> 1..m",
    "for i from RIGHT to LEFT:",
    "    r = rank(nums[i])",
    "    result[i] = prefix(r - 1)   # smaller, already inserted",
    "    add(r)                       # record nums[i] as 'seen to the right'",
]


def add(**f):
    frames.append(f)


sorted_vals = sorted(set(nums))
rank = {v: i + 1 for i, v in enumerate(sorted_vals)}
M = len(sorted_vals)


def lowbit(i):
    return i & (-i)


def covers(i):  # 1-based ranks node i counts: [i-lowbit+1 .. i]
    return list(range(i - lowbit(i) + 1, i + 1))


node_labels = [f"node {i} ({i:0{M.bit_length()}b})" for i in range(1, M + 1)]
col_labels = [f"r{r}\n={v}" for r, v in zip(range(1, M + 1), sorted_vals)]


def bit_rows(tree):
    rows = []
    for i in range(1, M + 1):
        row = [None] * M
        for r in covers(i):
            row[r - 1] = tree[i]
        rows.append(row)
    return rows


# ---- Act 0: brute force ----
add(act=0, rows=[[v for v in nums]], rowLabels=["nums"], colLabels=[str(i) for i in range(len(nums))],
    code="brute", line=0,
    intro="every element rescans its entire right suffix to tally smaller values.",
    invariant="result[i] = count of j>i with nums[j] < nums[i].",
    note=f"Brute force on {nums}: for each i, scan everything to its right and count the "
    "strictly smaller ones.",
    marks={"0,0": "active"}, state=[["result", "[?, ?, ?, ?]"], ["compares", 0]])
work = 0
result_b = [0] * len(nums)
for i in range(len(nums)):
    for j in range(i + 1, len(nums)):
        work += 1
        if nums[j] < nums[i]:
            result_b[i] += 1
    add(act=0, code="brute", line=2,
        note=f"i={i} (nums[i]={nums[i]}): {result_b[i]} smaller value(s) to its right.",
        rows=[[v for v in nums]], rowLabels=["nums"],
        colLabels=[str(k) for k in range(len(nums))],
        marks={f"0,{i}": "active", **{f"0,{k}": "dim" for k in range(i + 1, len(nums))}},
        state=[["i", i], ["count", result_b[i]], ["compares", work]])
add(act=0, code="brute", line=3,
    note=f"result = {result_b}, but it cost {work} comparisons — each element re-walked "
    "the suffix the element before it already walked.",
    rows=[[v for v in nums]], rowLabels=["nums"], colLabels=[str(k) for k in range(len(nums))],
    marks={}, state=[["result", str(result_b)], ["compares", work]])

# ---- Act 1: the waste ----
add(act=1,
    intro="'how many smaller to my right?' can be a running count, not a fresh scan.",
    note=f"The suffix scans overlap: {work} comparisons for 4 elements, growing like n*n. "
    "A Fenwick tree over value-ranks answers each query in log n.",
    marks={}, state=[["compares (brute)", work], ["pattern", "~ n * n"]])
add(act=1,
    note=f"Compress values to ranks: {dict(rank)}. Sweep RIGHT to LEFT; the tree counts "
    "ranks already inserted (all to the right). Query prefix(rank-1) = smaller-so-far.",
    marks={}, state=[["ranks", str(dict(rank))], ["sweep", "right -> left"]])

# ---- Act 2: BIT over ranks ----
tree = [0] * (M + 1)


def bit_add(i):
    while i <= M:
        tree[i] += 1
        i += lowbit(i)


def bit_prefix(i):
    s = 0
    while i > 0:
        s += tree[i]
        i -= lowbit(i)
    return s


add(act=2, rows=bit_rows(tree), rowLabels=node_labels, colLabels=col_labels, code="bit", line=1,
    intro="the tree is a frequency counter over ranks; prefix(r) = how many ranks <= r inserted.",
    invariant="everything inserted so far lies to the right of the current index.",
    note="Sweep right-to-left. At each element: query smaller ranks already inserted, then "
    "insert this rank.",
    marks={}, state=[["result", "[?, ?, ?, ?]"]])
result = [0] * len(nums)
for i in range(len(nums) - 1, -1, -1):
    r = rank[nums[i]]
    cnt = bit_prefix(r - 1)
    result[i] = cnt
    # highlight the prefix path buckets for r-1
    hl = {}
    j = r - 1
    while j > 0:
        for c in covers(j):
            hl[f"{j - 1},{c - 1}"] = "good"
        j -= lowbit(j)
    add(act=2, code="bit", line=3,
        note=f"nums[{i}]={nums[i]} has rank {r}. prefix({r - 1}) = {cnt} smaller value(s) "
             f"already to its right -> result[{i}] = {cnt}.",
        rows=bit_rows(tree), rowLabels=node_labels, colLabels=col_labels,
        marks=hl if hl else {},
        state=[["nums[i]", nums[i]], ["rank", r], ["smaller right", cnt]])
    bit_add(r)
    # highlight update path for r
    up = {}
    j = r
    while j <= M:
        for c in covers(j):
            up[f"{j - 1},{c - 1}"] = "active"
        j += lowbit(j)
    add(act=2, code="bit", line=4,
        note=f"Insert rank {r}: bump every bucket covering it. tree = {tree[1:]}.",
        rows=bit_rows(tree), rowLabels=node_labels, colLabels=col_labels, marks=up,
        state=[["inserted rank", r], ["tree", str(tree[1:])]])
add(act=2, code="bit", line=4,
    note=f"result = {result} — same answer as brute, but each query and insert was O(log m).",
    rows=bit_rows(tree), rowLabels=node_labels, colLabels=col_labels, marks={},
    state=[["result", str(result)], ["vs brute compares", work]],
    banner=f"counts = {result}   (Fenwick over ranks, O(n log n))")

# ---- Act 3: sorted edge case ----
edge = [1, 2, 3, 4]
add(act=3, rows=[[v for v in edge]], rowLabels=["nums"], colLabels=[str(i) for i in range(4)],
    code="bit", line=1,
    intro="already sorted: nothing smaller is ever to the right.",
    invariant="a rank inserted is always >= every future query -> zero counts.",
    note="Edge case: [1,2,3,4], already ascending. Sweeping right-to-left, every inserted "
    "value is larger than the next one queried, so every count is 0.",
    marks={f"0,{i}": "good" for i in range(4)},
    state=[["result", "[0, 0, 0, 0]"]], banner="Sorted input -> all zeros")

trace = {
    "player": "grid",
    "title": "Count of Smaller After Self - a Fenwick tree over value ranks",
    "acts": ["Brute: rescan suffix", "The waste", "BIT over ranks", "Edge: already sorted"],
    "code": {"brute": BRUTE, "bit": BIT},
    "legend": [["active", "buckets updated (insert)"], ["good", "buckets summed (query) / answer"],
               ["dim", "suffix being scanned"]],
    "rows": [[v for v in nums]], "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
