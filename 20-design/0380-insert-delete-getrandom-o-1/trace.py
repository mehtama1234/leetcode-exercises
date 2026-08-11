"""Rich full-arc trace for Insert Delete GetRandom O(1) (linear renderer).
Design problem, so the arc is: two structures each missing one thing -> pair them
with the swap-with-last delete trick -> edge (remove the last slot). Mirrors the
array + dict in solution.py; every index is computed, not guessed. The `cells`
row is the `vals` array; the sidebar is the `pos` dict (value -> index). Writes
trace.json.
"""
import json
import os

frames = []

INSERT = [
    "def insert(val):",
    "    if val in pos: return False",
    "    pos[val] = len(vals)",
    "    vals.append(val)",
    "    return True",
]
REMOVE = [
    "def remove(val):",
    "    if val not in pos: return False",
    "    idx = pos[val]",
    "    last = vals[-1]",
    "    vals[idx] = last      # swap last into the hole",
    "    pos[last] = idx",
    "    vals.pop()            # drop the duplicated tail",
    "    del pos[val]",
    "    return True",
]
RANDOM = [
    "def getRandom():",
    "    return vals[random_index]",
]


def add(**f):
    frames.append(f)


def sidebar(pos):
    return {"title": "pos (value -> index)",
            "rows": [[str(k), str(v)] for k, v in pos.items()]}


def labels(vals):
    return list(range(len(vals)))


# ---- Act 0: two structures, each missing one thing ----
add(act=0, cells=[1, 2, 3], labels=[0, 1, 2], code=None,
    intro="watch which operation each structure alone makes slow.",
    invariant="we want insert, remove, AND uniform getRandom all O(1) at once.",
    note="An array gives O(1) random pick — just index a random slot — but deleting "
    "from the middle is O(n): every later element shifts left to close the hole.",
    marks={"1": "bad"},
    state=[["array delete", "O(n) shift"], ["array random", "O(1)"]])
add(act=0, cells=[1, 2, 3], labels=[0, 1, 2], code=None,
    note="A hash set gives O(1) insert and remove, but picking a uniform random "
    "element means walking its buckets — O(n). Neither structure alone does all three.",
    marks={"0": "dim", "1": "dim", "2": "dim"},
    state=[["set insert/remove", "O(1)"], ["set random", "O(n) walk"]])

# ---- Act 1: pair them + the swap-with-last trick ----
vals = []
pos = {}

add(act=1, cells=[], labels=[], code="insert", line=0,
    intro="the array holds the values; the dict remembers each value's index.",
    invariant="pos[v] is always the current index of v inside vals.",
    note="Pair them: an array vals for O(1) random indexing, and a dict pos mapping "
    "value -> its index. Start empty.",
    sidebar=sidebar(pos), state=[["size", 0]])

# insert 1, 2, 3 — mirror: pos[val] = len(vals); vals.append(val)
for v in (1, 2, 3):
    pos[v] = len(vals)
    vals.append(v)
    add(act=1, cells=list(vals), labels=labels(vals), code="insert", line=3,
        note=f"insert({v}): record pos[{v}] = {pos[v]} (the next free index), then "
             f"append {v} to the array. Both O(1).",
        marks={str(pos[v]): "good"}, sidebar=sidebar(pos),
        state=[["inserted", v], ["at index", pos[v]], ["size", len(vals)]])

# getRandom — describe, don't fake a value
add(act=1, cells=list(vals), labels=labels(vals), code="random", line=1,
    note="getRandom(): pick any index into vals — here 0, 1, or 2 — each equally "
    "likely, and return that slot. One array index, O(1), and uniform for free.",
    marks={"0": "active", "1": "active", "2": "active"}, sidebar=sidebar(pos),
    state=[["choices", "index 0, 1, 2"], ["each", "1/3 chance"]])

# remove(2) — the key swap-with-last trick
val = 2
idx = pos[val]          # 1
last = vals[-1]         # 3
add(act=1, cells=list(vals), labels=labels(vals), code="remove", line=2,
    note=f"remove(2): the dict says 2 sits at index {idx}. Deleting it directly would "
    f"leave a hole and force a shift — so instead we use the last element, {last}.",
    marks={str(idx): "active", str(len(vals) - 1): "active"}, arc=[idx, len(vals) - 1],
    sidebar=sidebar(pos), state=[["remove", val], ["idx", idx], ["last", last]])

# vals[idx] = last  ;  pos[last] = idx
vals[idx] = last
pos[last] = idx
add(act=1, cells=list(vals), labels=labels(vals), code="remove", line=5,
    note=f"Swap: copy {last} into index {idx} and update pos[{last}] = {idx}. Now the "
    f"element we want gone is only the duplicated copy at the end.",
    marks={str(idx): "good", str(len(vals) - 1): "bad"}, arc=[len(vals) - 1, idx],
    sidebar=sidebar(pos), state=[["moved", f"{last} -> index {idx}"]])

# vals.pop()  ;  del pos[val]
vals.pop()
del pos[val]
add(act=1, cells=list(vals), labels=labels(vals), code="remove", line=6,
    note=f"Pop the last slot (removing from the end is O(1)) and delete pos[{val}]. "
    f"2 is gone, no shifting — vals is {vals}.",
    marks={str(i): "good" for i in range(len(vals))}, sidebar=sidebar(pos),
    state=[["removed", val], ["size", len(vals)]],
    banner="remove(2): last element swapped into the hole, then popped — all O(1)")

# ---- Act 2: edge — remove the last element (no real swap) ----
val = 3
idx = pos[val]          # index of 3 in current vals [1, 3]
last = vals[-1]         # 3 itself — val IS the last slot
add(act=2, cells=list(vals), labels=labels(vals), code="remove", line=2,
    intro="when val is already the last slot, the swap moves an element onto itself.",
    invariant="the trick still works: swap-then-pop is safe even when idx == last.",
    note=f"Edge: remove(3) when 3 IS the last element (index {idx}). last = vals[-1] = "
    f"{last} is the same element.",
    marks={str(idx): "active"}, sidebar=sidebar(pos),
    state=[["remove", val], ["idx", idx], ["last", last]])

vals[idx] = last        # 3 onto itself — no-op move
pos[last] = idx         # pos[3] = idx — unchanged
add(act=2, cells=list(vals), labels=labels(vals), code="remove", line=4,
    note=f"The swap copies {last} onto its own slot — a harmless no-op. No other "
    f"element moves.",
    marks={str(idx): "active"}, sidebar=sidebar(pos),
    state=[["swap", "3 onto itself"]])

vals.pop()
del pos[val]
add(act=2, cells=list(vals), labels=labels(vals), code="remove", line=6,
    note=f"Pop the tail and delete pos[3]. Only 1 remains, vals = {vals}. Removing the "
    f"last slot needs no real swap.",
    marks={str(i): "good" for i in range(len(vals))}, sidebar=sidebar(pos),
    state=[["removed", val], ["vals", str(vals)]])

# re-insert to show it stays consistent
v = 2
pos[v] = len(vals)
vals.append(v)
add(act=2, cells=list(vals), labels=labels(vals), code="insert", line=3,
    note=f"insert(2) again: pos[2] = {pos[v]}, append 2. The set is consistent after "
    f"the removals — indices and dict still agree.",
    marks={str(pos[v]): "good"}, sidebar=sidebar(pos),
    state=[["re-inserted", v], ["at index", pos[v]], ["vals", str(vals)]],
    banner="Removing the last slot, then re-inserting, keeps vals and pos in sync")

trace = {
    "player": "linear",
    "title": "Insert Delete GetRandom O(1) - array for random, dict for index, swap-with-last to delete",
    "acts": ["Two structures, each missing one thing",
             "Pair them + the swap-with-last trick",
             "Edge: remove the last element"],
    "code": {"insert": INSERT, "remove": REMOVE, "random": RANDOM},
    "legend": [["active", "cell(s) in play"], ["good", "live / inserted"],
               ["bad", "the slot being dropped"], ["dim", "inactive"]],
    "cells": [], "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
