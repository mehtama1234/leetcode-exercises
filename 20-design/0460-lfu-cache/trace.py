"""Rich full-arc trace for LFU Cache (linear renderer).
Design problem, so the arc is: the rule (bucket keys by use-count, track the
min) -> run get/put with a frequency bump -> an eviction that breaks a tie by
recency, then the count-tie edge. The live cache keys are the `cells` row; each
key's value + frequency ride in the labels/state, and the frequency buckets +
min_freq live in the `sidebar`. Mirrors solution.py's _touch / evict. trace.json.
"""
import json
import os
from collections import OrderedDict

frames = []

CODE = [
    "# buckets: freq -> keys in recency order (oldest first)",
    "def _touch(key):           # a use bumps frequency",
    "    move key from bucket[f] to bucket[f+1]",
    "    if bucket[f] emptied and f == min_freq: min_freq += 1",
    "def put(key, value):",
    "    if full: evict front of bucket[min_freq]  # LFU, then LRU",
    "    new key -> freq 1, min_freq = 1",
]


def add(**f):
    frames.append(f)


# We reproduce solution.py's state by hand so the sidebar is exact.
key_val = {}
key_freq = {}
freq_keys = {}  # freq -> OrderedDict of keys (oldest first)
min_freq = [0]


def _reset():
    key_val.clear()
    key_freq.clear()
    freq_keys.clear()
    min_freq[0] = 0


def _touch(key):
    f = key_freq[key]
    bucket = freq_keys[f]
    del bucket[key]
    if not bucket:
        del freq_keys[f]
        if min_freq[0] == f:
            min_freq[0] = f + 1
    nf = f + 1
    key_freq[key] = nf
    freq_keys.setdefault(nf, OrderedDict())[key] = None


def _put(key, value, cap):
    evicted = None
    if key in key_val:
        key_val[key] = value
        _touch(key)
        return None
    if len(key_val) >= cap:
        bucket = freq_keys[min_freq[0]]
        evicted, _ = bucket.popitem(last=False)
        if not bucket:
            del freq_keys[min_freq[0]]
        del key_val[evicted]
        del key_freq[evicted]
    key_val[key] = value
    key_freq[key] = 1
    freq_keys.setdefault(1, OrderedDict())[key] = None
    min_freq[0] = 1
    return evicted


def cells_now():
    """Live keys as cells; labels show key:val; return (cells, labels, freq per idx)."""
    keys = list(key_val.keys())
    cells = keys
    labels = [f"{k}:{key_val[k]}" for k in keys]
    return cells, labels, keys


def sidebar():
    rows = [["min_freq", str(min_freq[0])]]
    for f in sorted(freq_keys):
        ks = ", ".join(str(k) for k in freq_keys[f].keys())
        rows.append([f"freq {f}", ks])
    return {"title": "buckets (oldest -> newest)", "rows": rows}


def snap(idx_of_key):
    """map a key to its cell index for marks/pointers."""
    keys = list(key_val.keys())
    return keys.index(idx_of_key) if idx_of_key in keys else None


# ---- Act 0: the rule ----
_reset()
_put(1, 1, 2)
_put(2, 2, 2)
cells, labels, keys = cells_now()
add(act=0, cells=cells, labels=labels, code="ops", line=0,
    intro="every key sits in a bucket by how often it's been used; min_freq points at "
    "the eviction bucket, so we never scan for the least-frequent.",
    invariant="within a bucket, order is recency: oldest at the front (evict-first).",
    note="LFU groups keys by use-count into buckets. Each bucket keeps its keys in "
    "recency order. min_freq names the bucket to evict from.",
    marks={"0": "good", "1": "good"}, sidebar=sidebar(),
    state=[["capacity", 2], ["min_freq", min_freq[0]]])

# ---- Act 1: a use bumps frequency ----
add(act=1, cells=cells, labels=labels, code="ops", line=1,
    intro="watch key 1 leave the freq-1 bucket and enter freq-2; min_freq rises.",
    invariant="a get or a value-update both count as one use.",
    note="Start: keys 1 and 2, both at freq 1. get(1) is a use — bump key 1 to freq 2.",
    marks={"0": "active", "1": "good"}, pointers={"get": 0}, sidebar=sidebar(),
    state=[["get(1)", "-> 1"], ["min_freq", min_freq[0]]])
_touch(1)  # get(1): value returned is 1
cells, labels, keys = cells_now()
add(act=1, cells=cells, labels=labels, code="ops", line=2,
    note="Key 1 moves from bucket freq-1 to bucket freq-2. Bucket freq-1 now holds only "
    "key 2, so min_freq stays 1 (key 2 is still least frequent).",
    marks={str(snap(1)): "good", str(snap(2)): "active"}, sidebar=sidebar(),
    state=[["returned", 1], ["freq(1)", key_freq[1]], ["min_freq", min_freq[0]]])

# put(3,3): full -> evict front of min_freq bucket (freq 1) = key 2
add(act=1, cells=cells, labels=labels, code="ops", line=5,
    note="put(3,3): cache is full. Evict from bucket min_freq=1. Its front (oldest) is "
    "key 2 — the least frequent, and among those the least recent.",
    marks={str(snap(2)): "bad", str(snap(1)): "good"}, pointers={"evict": snap(2)},
    sidebar=sidebar(),
    state=[["min_freq", min_freq[0]], ["evict", "key 2"]])
ev = _put(3, 3, 2)  # evicts 2
cells, labels, keys = cells_now()
add(act=1, cells=cells, labels=labels, code="ops", line=6,
    note=f"Dropped key {ev}. New key 3 enters at freq 1, so min_freq resets to 1. "
    "Cache now holds 1 (freq 2) and 3 (freq 1).",
    marks={str(snap(3)): "good", str(snap(1)): "good"}, sidebar=sidebar(),
    state=[["evicted", ev], ["min_freq", min_freq[0]], ["get(2)", -1]],
    banner="put(3,3) evicted key 2 (least frequently used)")

# ---- Act 2: tie broken by recency, then edge ----
# get(3) -> freq 2, so both 1 and 3 at freq 2; put(4,4) evicts older of the two = key 1
add(act=2, cells=cells, labels=labels, code="ops", line=1,
    intro="when counts tie, the older key in that bucket loses — that is the LRU "
    "tiebreak baked into bucket order.",
    invariant="the front of a bucket is always the oldest key at that frequency.",
    note="get(3) bumps key 3 to freq 2. Now both 1 and 3 are at freq 2 — a tie.",
    marks={str(snap(3)): "active"}, pointers={"get": snap(3)}, sidebar=sidebar(),
    state=[["get(3)", "-> 3"]])
_touch(3)
cells, labels, keys = cells_now()
add(act=2, cells=cells, labels=labels, code="ops", line=5,
    note="put(4,4): full, min_freq is now 2 (both keys are freq 2). Evict the FRONT of "
    "bucket 2 — key 1 entered that bucket first, so it is the least recent.",
    marks={str(snap(1)): "bad", str(snap(3)): "good"}, pointers={"evict": snap(1)},
    sidebar=sidebar(),
    state=[["min_freq", min_freq[0]], ["tie", "1 vs 3"], ["older", "key 1"]])
ev2 = _put(4, 4, 2)
cells, labels, keys = cells_now()
add(act=2, cells=cells, labels=labels, code="ops", line=6,
    note=f"Evicted key {ev2} (the least recent among the freq-2 tie). Kept 3, added 4 "
    "at freq 1.",
    marks={str(snap(4)): "good", str(snap(3)): "good"}, sidebar=sidebar(),
    state=[["evicted", ev2], ["get(1)", -1]],
    banner="Tie at freq 2 broken by recency: evict key 1")

# Edge: updating a key's value counts as a use (bumps freq)
_reset()
_put(1, 10, 2)
_put(2, 20, 2)
cells, labels, keys = cells_now()
add(act=2, cells=cells, labels=labels, code="ops", line=4,
    note="Edge: keys 1 and 2 both at freq 1. put(1,100) UPDATES key 1's value — and "
    "that update counts as a use.",
    marks={str(snap(1)): "active", str(snap(2)): "good"}, sidebar=sidebar(),
    state=[["put(1,100)", "update+use"]])
_put(1, 100, 2)  # updates value AND bumps freq
cells, labels, keys = cells_now()
add(act=2, cells=cells, labels=labels, code="ops", line=1,
    note="Key 1 is now value 100 AND freq 2. So put(3,30) evicts key 2 (still freq 1), "
    "not the just-updated key 1.",
    marks={str(snap(1)): "good", str(snap(2)): "bad"}, sidebar=sidebar(),
    state=[["freq(1)", key_freq[1]], ["min_freq", min_freq[0]], ["next evict", "key 2"]],
    banner="An update is a use: put(1,100) protects key 1 from eviction")

trace = {
    "player": "linear",
    "title": "LFU Cache - bucket keys by use-count, evict the front of the min bucket",
    "acts": ["The rule: buckets + min_freq", "A use bumps frequency + evict", "Tie by recency + edge"],
    "code": {"ops": CODE},
    "legend": [["active", "key being used"], ["good", "live cache key"],
               ["bad", "evicted"], ["dim", "inactive"]],
    "cells": [1, 2], "labels": ["1:1", "2:2"], "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
