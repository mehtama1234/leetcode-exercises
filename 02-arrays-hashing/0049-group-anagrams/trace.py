"""Full-arc trace for Group Anagrams, mirroring solution.py: the sorted-letters
key baseline and the O(n*k) 26-count-signature key. The whole problem is picking
a key identical for anagrams and different otherwise, so a dict buckets them in
one pass. Linear renderer: the current word as a row of letter cells, the buckets
shown in the sidebar. Writes trace.json.
"""
import json
import os

words = ["eat", "tea", "tan", "ate", "nat", "bat"]
frames = []

SORTKEY = [
    "for word in strs:",
    '    key = "".join(sorted(word))',
    "    buckets[key].append(word)",
    "return list(buckets.values())",
]
FAST = [
    "for word in strs:",
    "    counts = [0]*26",
    "    for ch in word:",
    "        counts[ord(ch)-ord('a')] += 1",
    "    buckets[tuple(counts)].append(word)",
    "return list(buckets.values())",
]


def add(**f):
    frames.append(f)


def buckets_sidebar(buckets, title):
    rows = [[k, ", ".join(v)] for k, v in buckets.items()]
    if not rows:
        rows = [["(empty)", ""]]
    return {"title": title, "rows": rows}


# ---- Act 0: sorted-key baseline ----
buckets = {}
add(act=0, cells=list(words[0]), code="sort", line=0,
    intro="two words are anagrams exactly when their sorted letters match — so sort makes the key.",
    invariant="every word processed so far sits in the bucket named by its sorted letters.",
    note="Baseline: key each word by its sorted letters. Anagrams sort to the same string, so they share a bucket.",
    marks={str(i): "active" for i in range(len(words[0]))},
    sidebar=buckets_sidebar(buckets, "buckets (sorted-key -> words)"),
    state=[["word", words[0]], ["key", "".join(sorted(words[0]))]])
for word in words:
    key = "".join(sorted(word))
    new = key not in buckets
    buckets.setdefault(key, []).append(word)
    add(act=0, cells=list(word), code="sort", line=2,
        note=f"'{word}' -> sorted '{key}'. "
             + (f"New bucket '{key}'." if new else f"Joins existing bucket '{key}'."),
        marks={str(i): "active" for i in range(len(word))},
        sidebar=buckets_sidebar(buckets, "buckets (sorted-key -> words)"),
        state=[["word", word], ["key", key], ["buckets", len(buckets)]])
add(act=0, code="sort", line=3,
    note=f"Done: {len(buckets)} groups. Correct — but sorting each length-k word costs a k log k factor.",
    sidebar=buckets_sidebar(buckets, "buckets (sorted-key -> words)"),
    banner=f"{list(buckets.values())} — but the key cost a sort per word",
    state=[["groups", len(buckets)], ["key cost", "O(k log k)"]])

# ---- Act 1: the insight ----
add(act=1,
    intro="anagrams share letter COUNTS, so the 26-count vector is already a canonical name — no sort.",
    note="From Valid Anagram: anagrams have identical letter counts. So the tuple of 26 counts is a key that "
         "is equal for anagrams and different otherwise — built in O(k), no sorting.",
    state=[["idea", "count signature"], ["key cost", "O(k) vs O(k log k)"]])

# ---- Act 2: 26-count key ----
buckets = {}


def sig(word):
    c = [0] * 26
    for ch in word:
        c[ord(ch) - ord("a")] += 1
    # compact readable signature: only nonzero letters
    return "{" + ",".join(f"{chr(97 + i)}:{c[i]}" for i in range(26) if c[i]) + "}"


add(act=2, cells=list(words[0]), code="fast", line=0,
    intro="the count vector is the key — equal letters, equal key, same bucket.",
    invariant="each word lands in the bucket named by its 26-count signature.",
    note="Build a 26-slot count for each word and use it as the dict key. One O(k) pass per word.",
    marks={str(i): "active" for i in range(len(words[0]))},
    sidebar=buckets_sidebar(buckets, "buckets (count-sig -> words)"),
    state=[["word", words[0]], ["signature", sig(words[0])]])
for word in words:
    key = sig(word)
    new = key not in buckets
    buckets.setdefault(key, []).append(word)
    add(act=2, cells=list(word), code="fast", line=4,
        note=f"'{word}' -> counts {key}. "
             + (f"New group." if new else f"Same counts as an earlier word — same group."),
        marks={str(i): "good" if not new else "active" for i in range(len(word))},
        sidebar=buckets_sidebar(buckets, "buckets (count-sig -> words)"),
        state=[["word", word], ["signature", key], ["groups", len(buckets)]])
add(act=2, code="fast", line=5,
    note=f"Same {len(buckets)} groups, no sorting. The count vector did the canonicalizing for free.",
    sidebar=buckets_sidebar(buckets, "buckets (count-sig -> words)"),
    banner=f"{list(buckets.values())} — grouped in one O(n*k) pass",
    state=[["groups", len(buckets)]])

# ---- Act 3: edge case, singletons ----
edge = ["abc", "bca", "xyz"]
buckets = {}
add(act=3, cells=list(edge[0]), code="fast", line=0,
    intro="a word with no anagram partner simply owns its bucket alone — that is still a valid group.",
    invariant="a bucket with one word means no other word shares its letters.",
    note="Edge case: 'abc' and 'bca' are anagrams; 'xyz' has no partner and forms a group of one.",
    marks={str(i): "active" for i in range(len(edge[0]))},
    sidebar=buckets_sidebar(buckets, "buckets"),
    state=[["word", edge[0]]])
for word in edge:
    key = sig(word)
    new = key not in buckets
    buckets.setdefault(key, []).append(word)
    add(act=3, cells=list(word), code="fast", line=4,
        note=f"'{word}' -> {key}. "
             + ("New group." if new else "Joins its anagram."),
        marks={str(i): "good" if not new else "active" for i in range(len(word))},
        sidebar=buckets_sidebar(buckets, "buckets"),
        state=[["word", word], ["signature", key], ["groups", len(buckets)]])
add(act=3, code="fast", line=5,
    note=f"Result: {list(buckets.values())}. 'xyz' stands alone — a group of one is fine.",
    sidebar=buckets_sidebar(buckets, "buckets"),
    banner=f"{list(buckets.values())}",
    state=[["groups", len(buckets)]])

trace = {
    "player": "linear",
    "title": "Group Anagrams — pick a key that anagrams share",
    "acts": ["Baseline: sorted-letters key", "The insight", "Fast: 26-count key", "Edge case: a singleton"],
    "code": {"sort": SORTKEY, "fast": FAST},
    "legend": [["active", "letters of the current word"], ["good", "joined an existing group"], ["dim", "inactive"]],
    "cells": list(words[0]), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
