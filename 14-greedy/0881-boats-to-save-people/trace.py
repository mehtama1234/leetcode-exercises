"""Rich full-arc trace for Boats to Save People, mirroring num_rescue_boats in
solution.py. Shows a greedy-but-wrong idea (pair two heaviest) wasting seats,
names the waste, then runs the correct sort + two-pointer pairing (heaviest with
lightest), and finishes on the everyone-solo edge case. Writes trace.json.
"""
import json
import os

people = [3, 5, 3, 4]
limit = 5
frames = []

WRONG = [
    "people.sort(reverse=True)",
    "i, boats = 0, 0",
    "while i < n:",
    "    # pair two heaviest if they fit",
    "    if i+1 < n and people[i]+people[i+1] <= limit:",
    "        i += 2",
    "    else:",
    "        i += 1",
    "    boats += 1",
]
FAST = [
    "people.sort()",
    "left, right = 0, n - 1",
    "boats = 0",
    "while left <= right:",
    "    if people[left] + people[right] <= limit:",
    "        left += 1",
    "    right -= 1",
    "    boats += 1",
]


def add(**f):
    frames.append(f)


# ---- Act 0: wrong greedy — pair the two heaviest ----
wrong = sorted(people, reverse=True)  # [5,4,3,3]
add(act=0, cells=wrong, code="wrong", line=0,
    intro="pairing heavy-with-heavy: two big people almost never fit, so second seats sit empty.",
    invariant="boats counts committed boats; i marks the heaviest person not yet seated.",
    note=f"Tempting greedy: sort DESCENDING {wrong}, limit {limit}. Try to pair the two "
         "heaviest each boat.",
    pointers={"i": 0}, marks={"0": "active"},
    state=[["limit", limit], ["boats", 0], ["wasted seats", 0]])
i = 0
boats = 0
wasted = 0
while i < len(wrong):
    if i + 1 < len(wrong) and wrong[i] + wrong[i + 1] <= limit:
        boats += 1
        add(act=0, code="wrong", line=5,
            note=f"{wrong[i]} + {wrong[i+1]} = {wrong[i]+wrong[i+1]} <= {limit}: they fit, "
                 "one boat for two.",
            pointers={"i": i}, arc=[i, i + 1],
            marks={str(i): "good", str(i + 1): "good"},
            state=[["pair", f"{wrong[i]}+{wrong[i+1]}"], ["boats", boats],
                   ["wasted seats", wasted]])
        i += 2
    else:
        boats += 1
        wasted += 1
        pair_txt = (f"{wrong[i]} + {wrong[i+1]} = {wrong[i]+wrong[i+1]} > {limit}"
                    if i + 1 < len(wrong) else f"{wrong[i]} is the last person")
        add(act=0, code="wrong", line=7,
            note=f"{pair_txt}: {wrong[i]} sails ALONE. Second seat wasted.",
            pointers={"i": i}, marks={str(i): "bad"},
            state=[["alone", wrong[i]], ["boats", boats], ["wasted seats", wasted]])
        i += 1
add(act=0, code="wrong", line=8,
    note=f"This greedy uses {boats} boats and wasted {wasted} second seats. The light "
         "people never got matched up.",
    marks={str(k): "dim" for k in range(len(wrong))},
    state=[["boats (wrong)", boats], ["wasted seats", wasted]])

# ---- Act 1: the waste ----
add(act=1,
    intro="the second seat is the whole resource — heavy-with-heavy throws it away.",
    note=f"Pairing heavy-with-heavy left {wasted} empty seats. Every empty seat is a "
         "light person who now needs their own boat.",
    marks={str(k): "dim" for k in range(len(wrong))},
    state=[["wasted seats", wasted], ["fix", "fill each 2nd seat"]])
add(act=1,
    note="The heaviest person must sail regardless. So ask the cheapest question: does "
         "the LIGHTEST person fit beside them? If they don't, nobody lighter helps either.",
    marks={str(k): "dim" for k in range(len(wrong))},
    state=[["pair", "heaviest + lightest"], ["cost", "one sorted sweep"]])

# ---- Act 2: correct two-pointer greedy ----
p = sorted(people)  # [3,3,4,5]
left, right = 0, len(p) - 1
boats = 0
add(act=2, cells=p, code="fast", line=1,
    intro="left = lightest, right = heaviest. The heaviest always boards; the lightest rides along if they fit.",
    invariant="everyone outside [left, right] is already on a boat; boats = boats committed.",
    note=f"Correct greedy: sort ASCENDING {p}. left at the lightest, right at the heaviest.",
    pointers={"left": left, "right": right},
    marks={str(left): "active", str(right): "active"},
    state=[["limit", limit], ["left", p[left]], ["right", p[right]], ["boats", 0]])
while left <= right:
    total = p[left] + p[right]
    boats += 1
    if left == right:
        add(act=2, code="fast", line=6,
            note=f"one person left ({p[right]}): they take the final boat.",
            pointers={"left": left, "right": right}, marks={str(right): "good"},
            state=[["alone", p[right]], ["boats", boats]])
        right -= 1
    elif total <= limit:
        add(act=2, code="fast", line=5,
            note=f"lightest {p[left]} + heaviest {p[right]} = {total} <= {limit}: both "
                 "board. Move both pointers in.",
            pointers={"left": left, "right": right}, arc=[left, right],
            marks={str(left): "good", str(right): "good"},
            state=[["pair", f"{p[left]}+{p[right]}"], ["boats", boats]])
        left += 1
        right -= 1
    else:
        add(act=2, code="fast", line=6,
            note=f"heaviest {p[right]} + lightest {p[left]} = {total} > {limit}: even the "
                 "lightest won't fit, so heaviest sails alone.",
            pointers={"left": left, "right": right}, marks={str(right): "bad"},
            state=[["alone", p[right]], ["boats", boats]])
        right -= 1
add(act=2, code="fast", line=7,
    note=f"{boats} boats — the true minimum. Pairing heaviest-with-lightest never wastes "
         "a seat that could have been filled.",
    marks={str(k): "dim" for k in range(len(p))},
    state=[["answer", boats], ["vs wrong greedy", 4]],
    banner=f"Minimum boats = {boats}   (sort + pair heaviest with lightest)")

# ---- Act 3: edge case — everyone solo ----
edge = [5, 5, 5, 5]
elim = 6
left, right = 0, len(edge) - 1
boats = 0
add(act=3, cells=edge, labels=[0, 1, 2, 3], code="fast", line=3,
    intro="when no two people fit, every step retires only the right pointer — one boat each.",
    invariant="the heaviest still boards each boat; left never advances if no pair fits.",
    note=f"Edge case: {edge}, limit {elim}. 5 + 5 = 10 > 6, so no two ever fit.",
    pointers={"left": left, "right": right},
    marks={str(left): "active", str(right): "active"},
    state=[["limit", elim], ["boats", 0]])
while left <= right:
    boats += 1
    if left == right:
        add(act=3, code="fast", line=6,
            note=f"last person {edge[right]} takes the final boat.",
            pointers={"left": left, "right": right}, marks={str(right): "good"},
            state=[["boats", boats]])
        right -= 1
    else:
        add(act=3, code="fast", line=6,
            note=f"{edge[left]} + {edge[right]} = {edge[left]+edge[right]} > {elim}: "
                 f"{edge[right]} sails alone.",
            pointers={"left": left, "right": right}, marks={str(right): "bad"},
            state=[["alone", edge[right]], ["boats", boats]])
        right -= 1
add(act=3, code="fast", line=7,
    note=f"{boats} boats — everyone solo. left never moved because no pair ever fit.",
    marks={str(k): "dim" for k in range(len(edge))},
    state=[["answer", boats]],
    banner="No two fit -> 4 boats (one per person)")

trace = {
    "player": "linear",
    "title": "Boats to Save People — pair the heaviest with the lightest",
    "acts": ["Wrong greedy: heaviest + heaviest", "The waste",
             "Fast: heaviest + lightest", "Edge case: everyone solo"],
    "code": {"wrong": WRONG, "fast": FAST},
    "legend": [["active", "pointer heads"], ["good", "seated this boat"],
               ["bad", "sails alone"], ["dim", "already ashore"]],
    "cells": people, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
