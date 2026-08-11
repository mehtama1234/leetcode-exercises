"""Full-arc trace for Valid Parentheses: a single pass pushing openers and
matching each closer against the top of a stack (LIFO). No wasteful baseline —
the arc is: the rule -> run a valid string -> two edge cases (mismatch, leftover
opener). Linear renderer: the string as a row of cells, a scanning pointer, and
the stack shown in the sidebar (top at the bottom row). Writes trace.json.
"""
import json
import os

s = "{[]}"
frames = []

FAST = [
    'pairs = {")": "(", "]": "[", "}": "{"}',
    "for ch in s:",
    "    if ch in pairs:            # closer",
    "        if not stack or stack.pop() != pairs[ch]:",
    "            return False",
    "    else:                      # opener",
    "        stack.append(ch)",
    "return not stack",
]
PAIRS = {")": "(", "]": "[", "}": "{"}


def add(**f):
    frames.append(f)


def sidebar(stack):
    # show the stack bottom -> top so the "top" (last pushed) reads as most recent
    rows = [[str(k), v] for k, v in enumerate(stack)]
    rows.append(["top", stack[-1] if stack else "(empty)"])
    return {"title": "stack (openers waiting)", "rows": rows}


def run_act(act, s, intro, invariant, note0):
    stack = []
    add(act=act, cells=list(s), code="fast", line=0,
        intro=intro, invariant=invariant, note=note0,
        pointers={"ch": 0}, marks={"0": "active"}, sidebar=sidebar(stack),
        state=[["s", s], ["stack", "[]"]])
    ok = True
    for i, ch in enumerate(s):
        if ch in PAIRS:  # closer
            need = PAIRS[ch]
            if not stack or stack[-1] != need:
                top = stack[-1] if stack else "(empty)"
                add(act=act, code="fast", line=3,
                    note=f"'{ch}' at index {i} needs '{need}' on top, but top is {top}. Mismatch.",
                    pointers={"ch": i}, marks={str(i): "bad"}, sidebar=sidebar(stack),
                    state=[["closer", ch], ["needs", need], ["top", top], ["result", "False"]])
                add(act=act, code="fast", line=4,
                    note="A closer that does not match the most recent opener means the string is invalid.",
                    pointers={"ch": i}, marks={str(i): "bad"}, sidebar=sidebar(stack),
                    banner=f"False — '{s}' is not balanced",
                    state=[["answer", "False"]])
                ok = False
                break
            popped = stack.pop()
            add(act=act, code="fast", line=3,
                note=f"'{ch}' at index {i} closes the '{popped}' on top. Pop it — matched pair.",
                pointers={"ch": i}, marks={str(i): "good"}, sidebar=sidebar(stack),
                state=[["closer", ch], ["popped", popped], ["stack depth", len(stack)]])
        else:  # opener
            stack.append(ch)
            add(act=act, code="fast", line=6,
                note=f"'{ch}' at index {i} is an opener. Push it — it must be closed later.",
                pointers={"ch": i}, marks={str(i): "active"}, sidebar=sidebar(stack),
                state=[["opener", ch], ["stack depth", len(stack)]])
    if ok:
        empty = not stack
        add(act=act, code="fast", line=7,
            note=("Reached the end and the stack is empty — every opener was closed in order."
                  if empty else
                  f"Reached the end but {len(stack)} opener(s) are still waiting — never closed."),
            marks={str(len(s) - 1): "good" if empty else "bad"}, sidebar=sidebar(stack),
            banner=(f"True — '{s}' is balanced" if empty else f"False — '{s}' has an unclosed opener"),
            state=[["stack empty?", str(empty)], ["answer", str(empty)]])
    return ok


# ---- Act 0: the rule + a valid, nested string ----
run_act(0, "{[]}",
        intro="the bracket that must close next is always the most recent opener — that is a stack.",
        invariant="the stack holds exactly the openers still waiting, newest on top.",
        note0="Push every opener. On a closer, it must match the top of the stack — the one thing allowed to close now.")

# ---- Act 1: valid, mixed ----
run_act(1, "()[]{}",
        intro="closers arrive right after their opener, so the stack stays shallow.",
        invariant="a matched pair pops immediately, keeping only unresolved openers.",
        note0="A second valid case: three pairs side by side. Each closes the opener just pushed.")

# ---- Act 2: edge case, interleaved (order matters) ----
run_act(2, "([)]",
        intro="'([)]' has balanced counts but the WRONG order — the stack catches it.",
        invariant="the top opener must match before an outer one can close.",
        note0="Edge case: interleaved, not nested. The ')' arrives while '[' is still on top.")

# ---- Act 3: edge case, leftover opener ----
run_act(3, "(",
        intro="a lone opener never gets a closer — the final stack is non-empty.",
        invariant="an opener stays on the stack until its matching closer arrives.",
        note0="Edge case: a single '(' with nothing to close it. The end-of-string check decides.")

trace = {
    "player": "linear",
    "title": "Valid Parentheses — the last opener is the first to close",
    "acts": ["The rule: {[]}", "Valid: ()[]{}", "Edge: interleaved ([)]", "Edge: leftover ("],
    "code": {"fast": FAST},
    "legend": [["active", "opener pushed / scanning"], ["good", "a matched, popped pair"], ["bad", "mismatch / leftover"]],
    "cells": list(s), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
