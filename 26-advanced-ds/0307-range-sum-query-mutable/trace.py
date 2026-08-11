"""Rich full-arc trace for Range Sum Query - Mutable (grid renderer, Fenwick/BIT).
Arc: the prefix-sum baseline and its waste (every update rewrites the tail) ->
the Fenwick tree of partial sums, each node a bucket covering a power-of-two run ->
a point update walking up the covering buckets -> a range query as two prefix walks.
The grid rows are BIT nodes 1..n; columns are base indices 0..n-1; a node's row is
filled across the block it sums (length = its lowest set bit).
Mirrors NumArray (Fenwick) in solution.py. Writes trace.json.
"""
import json
import os

nums = [1, 3, 5, 2]  # 1-indexed BIT of size 4
frames = []
N = len(nums)

PREFIX = [
    "prefix[k] = sum of first k elements",
    "sumRange(l, r) = prefix[r+1] - prefix[l]   # O(1)",
    "update(i, v): rewrite prefix[i+1 ..]        # O(n) !",
]
BIT = [
    "# node i covers a block of length (i & -i)",
    "def add(i, delta):     # walk UP the buckets",
    "    i += 1",
    "    while i <= n: tree[i] += delta; i += i & -i",
    "def prefix(i):         # walk DOWN the buckets",
    "    i += 1; s = 0",
    "    while i > 0: s += tree[i]; i -= i & -i",
    "    return s",
]


def add(**f):
    frames.append(f)


# BIT layout helpers. Node i (1-indexed) covers 0-based indices [i-lowbit .. i-1].
def lowbit(i):
    return i & (-i)


def covers(i):  # 0-based base indices node i sums
    L = lowbit(i)
    return list(range(i - L, i))


node_labels = [f"node {i} ({i:0{N.bit_length()}b})" for i in range(1, N + 1)]
col_labels = [str(c) for c in range(N)]


def bit_rows(tree, active_node=None, active_cols=None, cls="active"):
    """Grid: row per BIT node; fill columns it covers with the node's stored sum."""
    rows = []
    marks = {}
    for r, i in enumerate(range(1, N + 1)):
        row = [None] * N
        for c in covers(i):
            row[c] = tree[i]
        rows.append(row)
        if active_node == i:
            for c in covers(i):
                marks[f"{r},{c}"] = cls
    if active_cols:
        for (r, c) in active_cols:
            marks[f"{r},{c}"] = "good"
    return rows, marks


# ---- Act 0: prefix baseline + waste ----
add(act=0, rows=[[sum(nums[: c + 1]) for c in range(N)]], rowLabels=["prefix"],
    colLabels=col_labels, code="pre", line=0,
    intro="a prefix array makes range sums O(1) — but every update rewrites the tail.",
    invariant="sumRange(l,r) = prefix[r+1] - prefix[l].",
    note=f"Prefix sums of {nums}: a range sum is one subtraction. But changing element 1 "
    "makes every later prefix wrong.",
    marks={f"0,{c}": "good" for c in range(N)}, state=[["sumRange", "O(1)"], ["update", "O(n)"]])
add(act=0, code="pre", line=2,
    note="update(1, ...) must rebuild prefixes 2,3,4 — O(n) per update. With many updates "
    "that is the waste a Fenwick tree removes.",
    marks={"0,1": "active", "0,2": "bad", "0,3": "bad"},
    state=[["rewritten", "prefix[2..]"], ["cost", "O(n) each"]])

# ---- Act 1: the Fenwick tree of buckets ----
tree = [0] * (N + 1)


def build_add(i, delta):
    i += 1
    path = []
    while i <= N:
        tree[i] += delta
        path.append(i)
        i += lowbit(i)
    return path


for k, x in enumerate(nums):
    build_add(k, x)
rows_full, _ = bit_rows(tree)
add(act=1, rows=rows_full, rowLabels=node_labels, colLabels=col_labels, code="bit", line=0,
    intro="each node stores the sum of a block; block length is its lowest set bit.",
    invariant="node i covers exactly (i & -i) elements ending at index i-1.",
    note=f"Fenwick tree of {nums}. Node 1 sums {{0}}, node 2 sums {{0,1}}, node 3 sums "
    "{2}, node 4 sums {0,1,2,3}. Distinct power-of-two blocks.",
    marks={}, state=[["tree[1..4]", str(tree[1:])]])
for i in range(1, N + 1):
    _, marks = bit_rows(tree, active_node=i)
    add(act=1, code="bit", line=0,
        note=f"node {i} (binary {i:0{N.bit_length()}b}) covers a block of length "
             f"{lowbit(i)} -> indices {covers(i)}, storing their sum {tree[i]}.",
        rows=rows_full, marks=marks,
        state=[[f"node {i}", tree[i]], ["block length", lowbit(i)]])

# ---- Act 2: point update walks up ----
UPD_I, UPD_V = 1, 2  # set index 1 (currently 3) to 2 -> delta -1
delta = UPD_V - nums[UPD_I]
add(act=2, rows=rows_full, rowLabels=node_labels, colLabels=col_labels, code="bit", line=1,
    intro="an update touches only the buckets that contain that index — O(log n) of them.",
    invariant="add lowest set bit to jump to the next node covering i.",
    note=f"update(index {UPD_I}, {UPD_V}): the value drops by {abs(delta)}. Apply delta "
    f"{delta} to every node whose block covers index {UPD_I}.",
    marks={f"{r},{UPD_I}": "active" for r in range(N) if UPD_I in covers(r + 1)},
    state=[["index", UPD_I], ["delta", delta]])
i = UPD_I + 1
while i <= N:
    tree[i] += delta
    r = i - 1
    rows_now, _ = bit_rows(tree)
    add(act=2, code="bit", line=3,
        note=f"node {i} covers index {UPD_I}: tree[{i}] += {delta} -> {tree[i]}. "
             f"Jump by lowbit {lowbit(i)} to node {i + lowbit(i)}.",
        rows=rows_now, rowLabels=node_labels, colLabels=col_labels,
        marks={f"{r},{c}": "good" for c in covers(i)},
        state=[[f"tree[{i}]", tree[i]], ["next node", i + lowbit(i) if i + lowbit(i) <= N else "done"]])
    i += lowbit(i)
nums[UPD_I] = UPD_V

# ---- Act 3: range query as two prefix walks ----
rows_now, _ = bit_rows(tree)
QL, QR = 0, 2  # sumRange(0,2) = 1 + 2 + 5 = 8
add(act=3, rows=rows_now, rowLabels=node_labels, colLabels=col_labels, code="bit", line=4,
    intro="a prefix sum walks DOWN, peeling off the lowest set bit to hop disjoint blocks.",
    invariant="sumRange(l,r) = prefix(r) - prefix(l-1).",
    note=f"sumRange({QL}, {QR}) after the update. Compute prefix({QR}) by summing the "
    "buckets on the way down.",
    marks={}, state=[["query", f"[{QL},{QR}]"]])
i = QR + 1
s = 0
path = []
while i > 0:
    s += tree[i]
    r = i - 1
    add(act=3, code="bit", line=6,
        note=f"add tree[{i}] = {tree[i]} (covers {covers(i)}) -> running {s}. Drop lowbit "
             f"{lowbit(i)} to node {i - lowbit(i) if i - lowbit(i) > 0 else 0}.",
        rows=rows_now, rowLabels=node_labels, colLabels=col_labels,
        marks={f"{r},{c}": "good" for c in covers(i)},
        state=[[f"tree[{i}]", tree[i]], ["prefix so far", s]])
    path.append(i)
    i -= lowbit(i)
prefix_r = s
direct = sum(nums[QL: QR + 1])
add(act=3, code="bit", line=7,
    note=f"prefix({QR}) = {prefix_r}. Since l=0 that IS the range sum: {direct}. "
    f"Both update and query touched only ~log n nodes.",
    rows=rows_now, rowLabels=node_labels, colLabels=col_labels,
    marks={f"{r},{c}": "good" for r in range(N) for c in covers(r + 1) if c <= QR and (r + 1) in path},
    state=[["sumRange(0,2)", direct], ["nodes touched", len(path)]],
    banner=f"sumRange(0,2) = {direct}   (update + query both O(log n))")

trace = {
    "player": "grid",
    "title": "Range Sum Query - a Fenwick tree of power-of-two buckets",
    "acts": ["Prefix baseline & waste", "The bucket tree", "Update walks up", "Query walks down"],
    "code": {"pre": PREFIX, "bit": BIT},
    "legend": [["active", "buckets touched now"], ["good", "summed / final"],
               ["bad", "rewritten (prefix waste)"]],
    "rows": rows_full, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
